# Development by HSSLCreative
# Date: 2020/5/6

import requests
import os
import time
import re
from get import get
from proxyinfo import getProxyDic
from barknotify import BarkNotify
from PIL import Image


def downloadPg(comicNameAndEpisode, dlRootPath, dlEpisodePath, url, e, m, counter):
    h = {'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
         'accept-encoding': 'gzip, deflate, br',
         'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
         'cache-control': 'no-cache',
         'pragma': 'no-cache',
         'referer': 'https://www.manhuagui.com/',
         'sec-fetch-dest': 'image',
         'sec-fetch-mode': 'no-cors',
         'sec-fetch-site': 'cross-site',
         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    # 这里进行修改，下载先到一个缓存的目录
    tmpDownloadPath = os.path.join(dlRootPath, 'TmpDownload')
    if os.path.exists(tmpDownloadPath) == False:
        os.mkdir(tmpDownloadPath)
    # 这样的好处是一开始判断总张数的逻辑才是真正有意义的
    tmp_fileName = os.path.join(dlRootPath, 'TmpDownload', "tmpPic.tmp")
    # 提前判断是否需要下载这一页
    # 这里是 raw 文件夹存储的文件名
    # str(counter).zfill(4)
    output_filename = str(counter) + '.jpg'
    # 这里是 jpg 文件夹下载的存储名称
    jpg_src_filename = os.path.join(dlEpisodePath, output_filename)
    # 标志位
    bJpgFileExsit = False
    # 判断 jpg 的文件已经存在
    if os.path.exists(jpg_src_filename) == True and os.path.isfile(jpg_src_filename) == True:
        bJpgFileExsit = True

    # 單頁最大重試次數
    for i in range(20):
        try:
            res = requests.get(url, params={'e': e, 'm': m}, headers=h, timeout=10, proxies=getProxyDic())
            res.raise_for_status()
        except:
            sc = "res error"
            print('頁面 %s 下載失敗: %s 重試中...' % (url, sc), end='')
            print('等待 5 秒...')
            # 每次重試間隔
            time.sleep(5)
            continue
        # 存储到 tmp 文件
        file = open(tmp_fileName, 'wb')
        for chunk in res.iter_content(100000):
            file.write(chunk)
        file.close()
        # 转换格式
        im = Image.open(tmp_fileName)
        im.save(jpg_src_filename, 'jpeg')
        # 轉檔結束
        return
    print('超過最大重試次數（20） 跳過此檔案')
    # XX漫画_第几话_1页 错误
    BarkNotify(comicNameAndEpisode + "_" + str(counter), True)


def downloadCh(dlRootPath, url, config_json=None):
    j = get(url)
    if not j:
        return False
    bname = j['bname']
    episodeName = j['cname']
    # 极黑的布伦希尔德\\jpg\\特别篇
    comicName = re.sub(r'[\\/:*?"<>|]', '_', bname)
    nowComicFolder = os.path.join(dlRootPath, comicName)
    if os.path.exists(nowComicFolder) == False:
        os.mkdir(nowComicFolder)
    # 写配置文件
    configFullName = os.path.join(nowComicFolder, 'config.json')
    if config_json:
        with open(configFullName, 'w') as config:
            config.write(config_json)
            config.close()
    # 当前话的目标下载目录
    desDownloadEpisodeFolderPath = os.path.join(dlRootPath, comicName, episodeName)
    length = j['len']
    print('下載 %s %s 中 共%s頁' % (bname, episodeName, length))
    # 判断，下载的目标文件夹中，是否总图片张数与网页读取到的总张数一致
    # 不一致则开始下载
    # 首先是这个目录得存在，不存在则创建
    if os.path.exists(desDownloadEpisodeFolderPath) == False:
        os.mkdir(desDownloadEpisodeFolderPath)
    if coutFiles(desDownloadEpisodeFolderPath) == length:
        print("已经下载，跳过")
        return True

    e = j['sl']['e']
    m = j['sl']['m']
    path = j['path']
    i = 1
    for filename in j['files']:
        pgUrl = 'https://i.hamreus.com' + path + filename
        print(os.path.basename(pgUrl))
        print('%s / %s' % (i, length), end='\r')
        downloadPg(comicName + "_" + episodeName, dlRootPath, desDownloadEpisodeFolderPath, pgUrl, e, m, i)
        # 每頁間隔0.5秒
        time.sleep(0.5)
        i += 1
    return True


def coutFiles(dir):
    tmp = 0
    for item in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, item)) and os.path.splitext(item)[-1] == ".jpg":
            tmp += 1
    return tmp
