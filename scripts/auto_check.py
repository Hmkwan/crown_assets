import os
import sys
import json
import re
from urllib.parse import urljoin, urlparse
import requests

import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
pkg_init = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', '__init__.py'))
spec = importlib.util.spec_from_file_location('app_package', pkg_init)
app_pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_pkg)
create_app = getattr(app_pkg, 'create_app')

app = create_app()

report = {
    'pages': [],
    'resources': {},
}

try:
    import requests
    _have_requests = True
except Exception:
    requests = None
    _have_requests = False

css_js_img_pattern = re.compile(r"(?:href|src)=[\'\"]([^\'\"]+)\.(css|js|png|jpg|jpeg|gif|svg)\b", re.I)

with app.app_context():
    client = app.test_client()

    # collect GET rules without variables
    routes = []
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and '<' not in rule.rule and rule.rule != '/static/<path:filename>':
            routes.append(rule.rule)

    for route in sorted(set(routes)):
        try:
            resp = client.get(route)
            status = resp.status_code
            text = resp.get_data(as_text=True)
        except Exception as e:
            report['pages'].append({'route': route, 'status': 'error', 'error': str(e)})
            continue

        page_entry = {'route': route, 'status': status, 'resources': []}

        # find resource links
        for m in css_js_img_pattern.finditer(text):
            url = m.group(1) + '.' + m.group(2)
            # normalize to absolute path on same host
            parsed = urlparse(url)
            if parsed.netloc:
                # external resource, record as external
                res_path = url
            else:
                # make sure starts with /
                if not url.startswith('/'):
                    # relative path -> join with route
                    url = urljoin(route + '/', url)
                res_path = url

            # request resource
            try:
                parsed_res = urlparse(res_path)
                if parsed_res.scheme and parsed_res.netloc:
                    # external absolute URL -> use real HTTP request to verify reachability
                    if not _have_requests:
                        rcode = 'skipped:no_requests'
                    else:
                        try:
                            rr = requests.get(res_path, timeout=5)
                            rcode = rr.status_code
                        except Exception as e:
                            rcode = 'error:' + str(e)
                else:
                    # local resource -> use Flask test_client
                    try:
                        r = client.get(res_path)
                        rcode = r.status_code
                    except Exception as e:
                        rcode = 'error:' + str(e)
            except Exception as e:
                rcode = 'error:' + str(e)

            page_entry['resources'].append({'url': res_path, 'status': rcode})

            # global tally
            report['resources'].setdefault(res_path, []).append({'from': route, 'status': rcode})

        report['pages'].append(page_entry)

    # write report
    out_path = os.path.join(os.path.dirname(__file__), 'auto_check_report.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('WROTE', out_path)
    print('Pages checked:', len(report['pages']))
    missing = []
    for res, hits in report['resources'].items():
        for h in hits:
            if h['status'] != 200 and h['status'] != 304:
                missing.append({'resource': res, 'from': h['from'], 'status': h['status']})
    print('Non-200/304 resources count:', len(missing))
    if missing:
        print(json.dumps(missing, ensure_ascii=False, indent=2))
