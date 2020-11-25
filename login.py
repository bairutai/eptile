import sys
import io
import urllib.request
import http.cookiejar
from predict import crack_captcha
import requests
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
do_main = 'http://59.49.77.231:81/'

#登录时需要POST的数据
loginData = {'UserName':'0316009',
'Password':'5266660',
'Submit':'确认'}

#登录时表单提交到的地址（用开发者工具可以看到）
login_url = do_main + 'Admin_ChkLogin_G.asp'

headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

if __name__ == '__main__':
    CheckCode = crack_captcha();
    loginData['CheckCode'] = CheckCode
    print(loginData)
    post_data = urllib.parse.urlencode(loginData).encode('utf-8')
    #构造登录请求
    #req = urllib.request.Request(login_url, headers = headers, data = post_data)
    req = requests.post(url=login_url, data=post_data,headers=headers)
    print(req.content.decode("gbk"))
    cookie = http.cookiejar.CookieJar()
    print(cookie)