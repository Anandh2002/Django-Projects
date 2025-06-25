import re
import json
import base64
import hashlib
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from urllib.parse import urljoin

session_store = {}

def pass_endec(password):
    password_hash = hashlib.md5(password.encode()).hexdigest()
    combined_string = f"kr9rk{password_hash}kr9rk"
    return hashlib.sha512(combined_string.encode()).hexdigest()

def regex_match(regex, content):
    match = re.search(regex, content, flags=re.I)
    return match.group(1) if match else ''


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        sess = requests.Session()
        sess.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        session_store[username] = sess

        resp = sess.get('https://passbook.epfindia.gov.in/MemberPassBook/login', headers={
            'Upgrade-Insecure-Requests': '1', 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        })

        soup = BeautifulSoup(resp.text, 'html.parser')
        token = soup.find('input', attrs={'name': 'login-token'}).get('value')
        base64_image = soup.find('img', attrs={'id': 'captcha_id'}).get('src')
        _, encoded_data = base64_image.split(',', 1)
        image_data = base64.b64decode(encoded_data)

        with open(f'epfo_app/static/captcha_{username}.jpg', 'wb') as f:
            f.write(image_data)

        request.session['username'] = username
        request.session['password'] = pass_endec(password)
        request.session['token'] = token

        return redirect('captcha')


class CaptchaView(View):
    def get(self, request):
        return render(request, 'captcha.html', {
            'captcha_url': f'/static/captcha_{request.session["username"]}.jpg'
        })

    def post(self, request):
        username = request.session['username']
        captcha = request.POST['captcha'].strip()
        sess = session_store[username]

        resp = sess.post(
            'https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/final/checkLogin',
            data={
                'username': username,
                'password': request.session['password'],
                'token': request.session['token'],
                'answer': captcha
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://passbook.epfindia.gov.in/MemberPassBook/login',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
        )
        data = resp.json()
        print(data)
        soup = BeautifulSoup(data['object'], 'html.parser')
        otp_token = soup.find('button', attrs={'name': 'login-otp-verification'}).get('data-token')
        request.session['otp_token'] = otp_token
        return redirect('otp')


class OTPView(View):
    def get(self, request):
        return render(request, 'otp.html')

    def post(self, request):
        username = request.session['username']
        otp = request.POST['otp'].strip()
        sess = session_store[username]

        resp = sess.post(
            'https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/verify-login-otp',
            data={'token': request.session['otp_token'], 'otp': otp},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://passbook.epfindia.gov.in/MemberPassBook/login',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
        )

        token_data = resp.json()["data"]
        request.session['otp_verify_url'] = f'https://passbook.epfindia.gov.in/MemberPassBook/getting_data?token={token_data}'
        return redirect('passbook')


class PassbookView(View):
    def get(self, request):
        username = request.session['username']
        sess = session_store[username]
        otp_verify_url = request.session['otp_verify_url']

        resp = sess.get(otp_verify_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://passbook.epfindia.gov.in/MemberPassBook/login'
        })
        member_pass_book_content = resp.text
        
        uan_username = regex_match('function\s*chk\(\)\s*\{[\w\W]+?d\["username"\]\s*=\s*([^\;]+?)\;', member_pass_book_content)
        token = regex_match('function\s*chk\(\)\s*\{[\w\W]+?d\["token"\]\s*=\s*\'([^\;]+?)\'\;', member_pass_book_content)

        obj = sess.post('https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/chk-uan-oth-data', data = {'username': int(uan_username), 'token': token}, headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Referer': otp_verify_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'})

        
        uan_username = regex_match('function\s*mid\(\)\s*\{[\w\W]+?d\["username"\]\s*=\s*([^\;]+?)\;',member_pass_book_content)
        token = regex_match('function\s*mid\(\)\s*\{[\w\W]+?d\["token"\]\s*=\s*\'([^\;]+?)\'\;', member_pass_book_content)

        obj = sess.post('https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/get-uan-mids-data', data = {'username': int(uan_username), 'token': token}, headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Referer': otp_verify_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'})
        
        uan_username = regex_match('function\s*prd\(\)\s*\{[\w\W]+?d\["username"\]\s*=\s*([^\;]+?)\;', member_pass_book_content)
        token = regex_match('function\s*prd\(\)\s*\{[\w\W]+?d\["token"\]\s*=\s*\'([^\;]+?)\'\;', member_pass_book_content)

        obj = sess.post('https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/get-uan-profile-data', data = {'username': int(uan_username), 'token': token}, headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Referer': otp_verify_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'})
        with open('get_uan_profile_data_content.json', 'wb') as fh:
            fh.write(obj.content)
        
        uan_username = regex_match('function\s*psb\(\)\s*\{[\w\W]+?d\["username"\]\s*=\s*([^\;]+?)\;', member_pass_book_content)
        token = regex_match('function\s*psb\(\)\s*\{[\w\W]+?d\["token"\]\s*=\s*\'([^\;]+?)\'\;', member_pass_book_content)

        obj = sess.post('https://passbook.epfindia.gov.in/MemberPassBook/passbook/api/ajax/get-uan-passbook', data = {'username': int(uan_username), 'token': token}, headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Referer': otp_verify_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'X-Requested-With': 'XMLHttpRequest'})

        get_uan_passbook = obj.json()
        obj = sess.get(f'https://passbook.epfindia.gov.in/MemberPassBook/home?token={get_uan_passbook["object"]}', headers = {'Referer': otp_verify_url, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Host': 'passbook.epfindia.gov.in', 'Connection': 'keep-alive', 'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'same-origin', 'pragma': 'no-cache', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'accept-language': 'en-US,en;q=0.9,hi;q=0.8', 'cache-control': 'no-cache', 'connection': 'keep-alive'}, timeout=120)

        
        soup = BeautifulSoup(obj.text, 'html.parser')
        base_url = 'https://passbook.epfindia.gov.in'

        # Fix <link> tags (CSS)
        for tag in soup.find_all('link', href=True):
            tag['href'] = urljoin(base_url, tag['href'])

        # Fix <script> tags (JS)
        for tag in soup.find_all('script', src=True):
            tag['src'] = urljoin(base_url, tag['src'])

        # Fix <img> tags
        for tag in soup.find_all('img', src=True):
            tag['src'] = urljoin(base_url, tag['src'])

        # Convert soup back to string
        content = str(soup)
        return render(request,'passbook.html',{'passbook_html':content})
