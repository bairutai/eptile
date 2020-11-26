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

#
#登录时表单提交到的地址（用开发者工具可以看到）
login_url = do_main + 'Admin_ChkLogin_G.asp'
main_url = do_main + "index.asp"
order_url = do_main + "Scm_Order.asp?action=ListType"

headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded'}

QueryBDate = ""
QueryEDate = ""

queryData = {'QueryBDate':'','QueryEDate':''}
if __name__ == '__main__':
#先访问主页获取session
    response = requests.get(url=main_url)
    cookie_value = ''
    for key,value in response.cookies.items():  
        cookie_value += key + '=' + value + ';'  
    headers['Cookie'] = cookie_value
    print(headers)
    CheckCode = crack_captcha(headers);
    loginData['CheckCode'] = CheckCode
    print(loginData)
    post_data = urllib.parse.urlencode(loginData).encode('utf-8')
    #构造登录请求
    #response = urllib.request.Request(login_url, headers = headers, data = post_data)
    response = requests.post(url=login_url, data=post_data,headers=headers)
    #print(response.content.decode("gbk"))
    #for key,value in response.cookies.items():  
        #cookie_value += key + '=' + value + ';'  
    #headers['Cookie'] += cookie_value
    #print(headers)
    
    if len(sys.argv) == 3:
        QueryBDate = sys.argv[1]
        queryData['QueryBDate'] = QueryBDate
        QueryEDate = sys.argv[2]
        queryData['QueryEDate'] = QueryEDate
    post_data = urllib.parse.urlencode(queryData).encode('utf-8')
    response = requests.post(url=order_url, data=post_data,headers=headers)
    
    orderListHtml = response.content.decode("gbk")
    endIndex = orderListHtml.find('条纪录')
    orderCount = 0
    if endIndex != -1:
        result = orderListHtml[endIndex - 3:endIndex]
        beginIndex = result.find('共')
        if beginIndex != -1:
            result = result[beginIndex + 1:]
            orderCount = int(result)
    print(orderCount)
    #print(response.content.decode("gbk"))