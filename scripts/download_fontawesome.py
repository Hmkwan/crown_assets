import requests, os

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'vendor', 'fontawesome')
CSS_DIR = os.path.join(BASE_DIR, 'css')
WEBFONTS_DIR = os.path.join(BASE_DIR, 'webfonts')
os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(WEBFONTS_DIR, exist_ok=True)

VERSION = '5.15.4'
CSS_URL = f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{VERSION}/css/all.min.css'
FONT_URLS = [
    f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{VERSION}/webfonts/fa-solid-900.woff2',
    f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{VERSION}/webfonts/fa-regular-400.woff2',
    f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{VERSION}/webfonts/fa-brands-400.woff2'
]

print('Downloading CSS from', CSS_URL)
r = requests.get(CSS_URL)
if r.status_code == 200:
    css_path = os.path.join(CSS_DIR, 'all.min.css')
    open(css_path, 'wb').write(r.content)
    print('Wrote', css_path)
else:
    print('Failed to download CSS', r.status_code)

for u in FONT_URLS:
    fn = u.split('/')[-1]
    print('Downloading', u)
    r = requests.get(u)
    if r.status_code == 200:
        p = os.path.join(WEBFONTS_DIR, fn)
        open(p, 'wb').write(r.content)
        print('Wrote', p)
    else:
        print('Failed to download', u, r.status_code)

# Quick sanity: ensure CSS references correct relative path
print('Verifying CSS references...')
css_text = open(os.path.join(CSS_DIR, 'all.min.css'), 'r', encoding='utf-8').read()
if 'webfonts/fa-solid-900.woff2' in css_text:
    print('CSS references webfonts OK')
else:
    print('Warning: CSS does not reference expected webfonts')

print('Done')
