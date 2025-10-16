import requests
import time
import re
from config import TLS_FRANCE_BASE, TLS_GERMANY_BASE

class TLSAuth:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def login(self, email, password, country):
        base_url = TLS_FRANCE_BASE if country == 'france' else TLS_GERMANY_BASE
        
        try:
            auth_url = f"{base_url}/auth/realms/atlas/protocol/openid-connect/auth"
            params = {
                'client_id': 'tlscitizen',
                'redirect_uri': f'{base_url}/auth-callback',
                'response_type': 'code',
                'scope': 'openid',
                'ui_locales': 'fr'
            }
            
            response = self.session.get(
                auth_url, 
                params=params, 
                proxies=self.proxy_manager.get_proxy(), 
                timeout=30, 
                allow_redirects=True
            )
            
            form_url = self._extract_login_form_url(response.text, response.url)
            if not form_url:
                return False
            
            login_data = {
                'username': email,
                'password': password,
            }
            
            login_response = self.session.post(
                form_url,
                data=login_data,
                allow_redirects=False,
                proxies=self.proxy_manager.get_proxy(),
                timeout=30,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': response.url
                }
            )
            
            if login_response.status_code in [302, 303]:
                redirect_url = login_response.headers.get('Location', '')
                if redirect_url:
                    if not redirect_url.startswith('http'):
                        redirect_url = base_url + redirect_url
                    
                    final_response = self.session.get(
                        redirect_url,
                        allow_redirects=True,
                        proxies=self.proxy_manager.get_proxy(),
                        timeout=30
                    )
                    
                    if 'travel-groups' in final_response.url or 'workflow' in final_response.url:
                        return True
            
            return False
            
        except Exception as e:
            return False
    
    def _extract_login_form_url(self, html, current_url):
        if 'name="username"' in html:
            action_match = re.search(r'<form[^>]*action="([^"]*)"', html)
            if action_match:
                form_action = action_match.group(1)
                if not form_action.startswith('http'):
                    from urllib.parse import urljoin
                    form_action = urljoin(current_url, form_action)
                return form_action
        
        return current_url
