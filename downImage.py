import io

import requests

from cfg import origin_pic_folder
import time
def downloads_pic():
    currentTime = str(int(time.time())*1000)
    # 向指定的url请求验证码图片
    rand_captcha_url = 'http://59.49.77.231:81/getcode.asp?t=' + currentTime
    res = requests.get(rand_captcha_url, stream=True)
    with open(origin_pic_folder + currentTime+'.bmp', 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()
        
if __name__ == '__main__':
    for i in range(100):
        downloads_pic()