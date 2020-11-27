import sys
import io
import urllib.request
import http.cookiejar
from predict import crack_captcha
import requests
from bs4 import BeautifulSoup
import re
import xlwt
import xlrd
import os
from cfg import home_root
from xlutils.copy import copy
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
do_main = 'http://59.49.77.231:81/'

#登录时需要POST的数据
loginData = {'UserName':'0316009',
'Password':'5266660',
'Submit':'确认'}

#登录时表单提交到的地址（用开发者工具可以看到）
login_url = do_main + 'Admin_ChkLogin_G.asp'
main_url = do_main + "index.asp"
order_url = do_main + "Scm_Order.asp?action=ListType"

headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded'}

QueryBDate = ""
QueryEDate = ""

queryData = {'QueryBDate':'','QueryEDate':''}

#保存的excel表名
excel = home_root + "药品详情.xls"

#表头
tabhead = ['订单号','仓库号','品种数','制单日期','订单状态','失效日期','制单人','入库单号','商品编码','供应商编码','商品名称','单位','规格','生产商','国药准字','订单数量']
def dealHtml(html,list):
    return

def removeBlank(data):
    if data != None:
        return data.strip().replace(u'\u3000', u' ').replace(u'\xa0', u' ')
    else:   
        return data
        
def getRealUrl(linkUrl):
    match_obj = re.match(r"JavaScript:window.open[(]['](.*)['][,][']['][,](.*)", linkUrl, re.I)
    if match_obj:
        return do_main + match_obj.group(1)
    else:
        print("没有匹配到链接")

def analysisHtml(html,list):
    soup = BeautifulSoup(html,'lxml') #html.parser是解析器，也可是lxml
    orderList = soup.html.find_all("tr", recursive=False)
    if len(orderList) > 0:
        realOrderList = orderList[0].find_all("tr")
        if len(realOrderList) > 0:
            for i in range(1,len(realOrderList)):
                dataList = realOrderList[i].find_all("td")
                #print(dataList)
                if len(dataList) == 9:
                    testData = {}
                    testData['订单号'] = removeBlank(dataList[0].find('strong').get_text())
                    testData['仓库号'] = removeBlank(dataList[1].string)
                    testData['品种数'] = removeBlank(dataList[2].find('span').get_text())
                    testData['制单日期'] = removeBlank(dataList[3].string)
                    status = removeBlank(dataList[4].string)
                    if status == None:
                        status = removeBlank(dataList[4].find('font').get_text())
                    testData['订单状态'] = status
                    testData['失效日期'] = removeBlank(dataList[5].string)
                    testData['制单人'] = removeBlank(dataList[6].string)
                    testData['入库单号'] = removeBlank(dataList[7].string)
                    linkurl = dataList[8].find('a').get('onclick')
                    testData['明细查询'] = getRealUrl(removeBlank(linkurl))
                    list.append(testData)
    else:
        print("没查到订单数据")
        
def getOtherPageOrder(begin,end,page,headers,list):
    #print("page:" + str(page))
    url = order_url + "&QueryBDate=" + begin + "&QueryEDate=" + end + "&textfield=" + "&page=" + str(page)
    response = requests.get(url=url,headers=headers)
    orderListHtml = response.content.decode("gbk").replace('&nbsp;', ' ')
    analysisHtml(orderListHtml,list)

def analysisGoodsHtml(html,order,list):
    soup = BeautifulSoup(html,'lxml') #html.parser是解析器，也可是lxml
    goodsList = soup.body.table.find_all("tr", recursive=False)
    if len(goodsList) > 0:
        realOrderList = goodsList[1].find_all("tr")
        if len(realOrderList) > 5:
            realOrderList = realOrderList[4].find("table").find_all("tr")
            for i in range(1,len(realOrderList)):
                dataList = realOrderList[i].find_all("td")
                #print(dataList)
                if len(dataList) == 9:
                    testData = order.copy()
                    testData['商品编码'] = removeBlank(dataList[1].string)
                    testData['供应商编码'] = removeBlank(dataList[2].find('span').get_text())
                    testData['商品名称'] = removeBlank(dataList[3].string)
                    testData['单位'] = removeBlank(dataList[4].string)
                    testData['规格'] = removeBlank(dataList[5].string)
                    testData['生产商'] = removeBlank(dataList[6].string)
                    testData['国药准字'] = removeBlank(dataList[7].string)
                    testData['订单数量'] = removeBlank(dataList[8].find('strong').get_text())
                    #print(testData)
                    list.append(testData)
                    #print(list)
        
def getDetails(order,headers,list):
    url = order['明细查询']
    #print(url)
    response = requests.get(url=url,headers=headers)
    goodsListHtml = response.content.decode("gbk").replace('&nbsp;', ' ')
    analysisGoodsHtml(goodsListHtml,order,list)
    
def writeExcel(goodsList):
        #打开工作簿
        workbook = xlrd.open_workbook(excel)
        #获取工作簿中的所有表格
        sheets = workbook.sheet_names()
        #获取工作簿中所有表格中的的第一个表格
        worksheet = workbook.sheet_by_name(sheets[0])
        rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
        new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
        new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
        for i in range(0,len(goodsList)):
            for key in goodsList[i]:
                for j in range(0,len(tabhead)):
                    if key == tabhead[j]:
                        new_worksheet.write(i+rows_old,j,goodsList[i][key])
        new_workbook.save(excel)
        
if __name__ == '__main__':
#先访问主页获取session
    response = requests.get(url=main_url)
    cookie_value = ''
    for key,value in response.cookies.items():  
        cookie_value += key + '=' + value + ';'  
    headers['Cookie'] = cookie_value
    #print(headers)
    CheckCode = crack_captcha(headers);
    loginData['CheckCode'] = CheckCode
    #print(loginData)
    post_data = urllib.parse.urlencode(loginData).encode('utf-8')
    #构造登录请求
    #response = urllib.request.Request(login_url, headers = headers, data = post_data)
    response = requests.post(url=login_url, data=post_data,headers=headers)
    if response.content.decode("gbk").startswith('<SCRIPT language=JavaScript>'):
        print("登录失败,原因:" + response.content.decode("gbk"))
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
    orderListHtml = response.content.decode("gbk").replace('&nbsp;', ' ')
    
    orderCount = 0
    orderPage = 0
    endIndex = orderListHtml.find('条纪录')
    if endIndex != -1:
        result = orderListHtml[endIndex - 10:endIndex]
        beginIndex = result.find('共')
        if beginIndex != -1:
            result = result[beginIndex + 1:]
            orderCount = int(result)
    else:
        print("没查到数据")
        sys.exit();
    
    endIndex = orderListHtml.find('页，每页')
    if endIndex != -1:
        result = orderListHtml[endIndex - 10:endIndex]
        beginIndex = result.find('/共')
        if beginIndex != -1:
            result = result[beginIndex + 2:]
            orderPage = int(result)
    
    #print(orderCount)
    #print(orderPage)
    orderObjectList = []
    analysisHtml(orderListHtml,orderObjectList)
    
    #print(orderObjectList)
    if orderPage > 1:
        for i in range(2,orderPage + 1):
            getOtherPageOrder(QueryBDate,QueryEDate,i,headers,orderObjectList)
    #print(len(orderObjectList))
    
    goodsList = []
    for i in range(0,len(orderObjectList)):
        getDetails(orderObjectList[i],headers,goodsList)
    #print(goodsList)
    #print(len(goodsList))
    
    if len(goodsList) == 0:
        print("没有药品详情")
        sys.exit();
        
    if not os.path.isfile(excel):
        workbook = xlwt.Workbook()  # 新建一个工作簿
        sheet = workbook.add_sheet("表格1")  # 在工作簿中新建一个表格
        
        for i in range(0,len(tabhead)):
            sheet.write(0, i, tabhead[i])  # 像表格中写入数据（对应的行和列）
        workbook.save(excel)  # 保存工作簿
    #print(goodsList)
    writeExcel(goodsList)