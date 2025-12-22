#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selenium-based validation using local Edge/Chrome.

- Launch local browser (prefers Edge if found), do in-page login, open /chat
- Verify CSRF meta exists, check in-page Socket.IO client connected, attempt to fetch conversations via fetch and report status
- Save screenshot to scripts/selenium_chat.png and print browser console logs
"""
import os
import re
import time
import json
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options as EdgeOptions

BASE = 'http://10.168.93.93:5020'
USERNAME = 'admin'
PASSWORD = 'TempPass123!'

MSEDGE_PATHS = [r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
CHROME_PATHS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]


def find_local_browser():
    for p in MSEDGE_PATHS + CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None


def main():
    exe = find_local_browser()
    print('Detected local browser executable:', exe if exe else 'none')

    options = EdgeOptions()
    if exe:
        options.binary_location = exe
    # Use headless mode; new headless mode flag for Chromium
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    driver.set_window_size(1280, 800)

    try:
        print('Opening login page...')
        driver.get(BASE + '/auth/login')
        # try to fill form if available
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'username')))
            driver.find_element(By.NAME, 'username').clear(); driver.find_element(By.NAME, 'username').send_keys(USERNAME)
            driver.find_element(By.NAME, 'password').clear(); driver.find_element(By.NAME, 'password').send_keys(PASSWORD)
            # click login button if present
            btns = driver.find_elements(By.CSS_SELECTOR, 'button[type=submit]')
            if btns:
                btns[0].click()
            else:
                driver.find_element(By.NAME, 'password').submit()
            # wait for possible redirect / homepage
            time.sleep(2)
        except Exception as e:
            print('Form-based login interaction failed (trying programmatic requests fallback):', e)
            # fallback: use requests to get cookie and inject into browser
            s = requests.Session()
            r = s.get(BASE + '/auth/login')
            m = re.search(r"name=[\"']csrf_token[\"']\s+value=[\"']([^\"']+)[\"']", r.text)
            csrf = m.group(1) if m else ''
            payload = {'username': USERNAME, 'password': PASSWORD, 'csrf_token': csrf, 'submit': 'Login'}
            headers = {}
            if csrf:
                headers['X-CSRFToken'] = csrf
            login = s.post(BASE + '/auth/login', data=payload, headers=headers, allow_redirects=True)
            print('Requests login status:', login.status_code)
            # inject session cookie
            if 'session' in s.cookies:
                cookie_val = s.cookies.get('session')
                driver.get(BASE)  # ensure domain
                driver.add_cookie({'name': 'session', 'value': cookie_val, 'path': '/', 'domain': '10.168.93.93'})
                print('Injected session cookie into browser')

        print('Navigating to /chat...')
        driver.get(BASE + '/chat')

        # Wait for CSRF meta
        try:
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return !!document.querySelector('meta[name=\'csrf-token\']')"))
            csrf = driver.execute_script("return document.querySelector('meta[name=\'csrf-token\']').content")
            print('Found CSRF meta token:', bool(csrf))
        except TimeoutException:
            print('CSRF meta token not found on /chat')
            csrf = ''

        # Check page socket status
        try:
            socket_connected = driver.execute_script("return !!(window.socket && window.socket.connected === true)")
            print('Page Socket.IO client connected:', socket_connected)
        except JavascriptException as e:
            print('Socket check JS failed:', e)
            socket_connected = False

        # Try in-page fetch of conversations via async script
        js = """
        var callback = arguments[0];
        (async () => {
            try {
                const meta = document.querySelector('meta[name="csrf-token"]');
                const csrf = meta ? meta.content : '';
                const resp = await fetch(arguments[1] + '/api/chat/conversations', {credentials: 'include', headers: {'X-CSRFToken': csrf}});
                const txt = await resp.text();
                callback({status: resp.status, body: txt});
            } catch (e) { callback({error: String(e)}); }
        })();
        """
        try:
            conv_result = driver.execute_async_script(js, BASE)
            print('In-page fetch result:', conv_result)
        except Exception as e:
            print('In-page fetch script failed:', e)
            conv_result = None

        # Capture browser console logs (if available)
        try:
            logs = driver.get_log('browser')
            print('Browser console logs (tail 10):')
            for entry in logs[-10:]:
                print(entry)
        except Exception as e:
            print('Could not retrieve browser logs:', e)

        # Screenshot
        out_path = os.path.join('scripts', 'selenium_chat.png')
        driver.save_screenshot(out_path)
        print('Saved screenshot to', out_path)

        # Save page source for inspection
        with open('scripts/selenium_chat_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print('Saved page HTML to scripts/selenium_chat_page.html')

    finally:
        driver.quit()

if __name__ == '__main__':
    main()
