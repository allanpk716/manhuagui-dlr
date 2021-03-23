# Development by HSSLCreative
# Date: 2020/5/6

import re
import time
import bs4
import requests
import lzstring
from download import downloadCh
from generate_config import generate_config
from proxyinfo import getProxyDic
from barknotify import BarkNotify

check_re = r'^https?://([a-zA-Z0-9]*\.)?manhuagui\.com/comic/([0-9]+)/?'
request_url = 'https://tw.manhuagui.com/comic/%s'
host = 'https://tw.manhuagui.com'


def ChooseEpisode2Process(dlroot):
    # 输入一个漫画的网址，选择章节去下载

    while True:
        print('輸入URL:')
        # 格式:https://*.manhuagui.com/comic/XXXXX
        # 是否進入章節都沒關係
        # 例如https://*.manhuagui.com/comic/XXXXX/XXXXX.html也行
        # 反正要得只有id
        url = input()
        try:
            checked_id = re.match(check_re, url).group(2)
            break
        except:
            print('無效的網址')
            continue
    try:
        res = requests.get(request_url % checked_id, proxies=getProxyDic())
        res.raise_for_status()
    except:
        print('錯誤:可能是沒網路或被ban ip?')
        return
    bs = bs4.BeautifulSoup(res.text, 'html.parser')
    title = bs.select('.book-title h1')[0]
    print('標題: %s' % title.text)
    authors_link = bs.select('a[href^="/author"]')
    authors = []
    for author in authors_link:
        authors.append(author.text)
    authors = '、'.join(authors)
    config_json = generate_config(title.text, authors)
    links = bs.select('.chapter-list a')
    if not links:
        links = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser').select('.chapter-list a')
    links.reverse()
    ch_list = []
    for link in links:
        ch_list.append([link.attrs['title'], link.attrs['href']])
    print('編號 對應名稱')
    for ch_index in range(len(ch_list)):
        ch = ch_list[ch_index]
        print(str(ch_index).ljust(4), ch[0])
    print('輸入上列編號(ex:輸入1-2 5-8 10 將會下載編號 1, 2, 5, 6, 7, 8, 10 的章節)')
    choose_chs = input()
    tmp = re.findall(r'[0-9]+\-?[0-9]*', choose_chs)
    choose_block_list = []
    config_writed = False
    for block in tmp:
        try:
            block = block.split('-')
            for i in range(len(block)):
                block[i] = int(block[i])
                if block[i] > len(ch_list) or block[i] < 0:
                    raise Exception('out of range')
            if len(block) >= 2:
                if block[1] < block[0]:
                    block[0], block[1] = block[1], block[0]
                choose_block_list.append([block[0], block[1]])
            else:
                choose_block_list.append([block[0], block[0]])
        except:
            continue
    for area in choose_block_list:
        block = ch_list[area[0]:area[1]+1]
        for ch in block:
            if not config_writed:
                downloadCh(dlroot, host + ch[1], config_json)
            else:
                downloadCh(dlroot, host + ch[1])
                config_writed = True
            print('延遲5秒...')
            # 每話間隔5秒
            time.sleep(5)


def UpdateAll(dlroot, url):
    checked_id = re.match(check_re, url).group(2)
    try:
        res = requests.get(request_url % checked_id, proxies=getProxyDic())
        res.raise_for_status()
    except:
        print('錯誤:可能是沒網路或被ban ip?')
        return
    bs = bs4.BeautifulSoup(res.text, 'html.parser')
    title = bs.select('.book-title h1')[0]
    print('標題: %s' % title.text)
    authors_link = bs.select('a[href^="/author"]')
    authors = []
    for author in authors_link:
        authors.append(author.text)
    authors = '、'.join(authors)
    config_json = generate_config(title.text, authors)
    links = bs.select('.chapter-list a')
    if not links:
        links = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser').select('.chapter-list a')
    links.reverse()
    ch_list = []
    for link in links:
        ch_list.append([link.attrs['title'], link.attrs['href']])

    config_writed = False
    for ch in ch_list:
        if not config_writed:
            downloadCh(dlroot, host + ch[1], config_json)
        else:
            downloadCh(dlroot, host + ch[1])
            config_writed = True
        print('延遲5秒...')
        # 每話間隔5秒
        time.sleep(5)

    # bark 通知
    BarkNotify(title.text, False)


if __name__ == "__main__":
    # 修改 proxyinfo.py 中的代理地址
    # 这个是漫画是存放目录
    downloadRootPath = "x:\\动漫柜\\"
    comicList = []
    # 修改  barknotify.py 为自己的 Bark 通知接口
    # ---------------------------------------------------------
    # 正在更新
    # ---------------------------------------------------------
    # 咒术回战
    comicList.append("https://www.manhuagui.com/comic/28004")
    # 进击的巨人
    comicList.append("https://www.manhuagui.com/comic/4740")
    # 一拳超人 原作
    comicList.append("https://www.manhuagui.com/comic/9637")
    # 一拳超人
    comicList.append("https://www.manhuagui.com/comic/7580")
    # 海贼王
    comicList.append("https://www.manhuagui.com/comic/1128")
    # ---------------------------------------------------------
    # 已经完结
    # ---------------------------------------------------------
    # 火影忍者
    comicList.append("https://www.manhuagui.com/comic/4681")
    # 东京都立咒术高等专门学校
    comicList.append("https://www.manhuagui.com/comic/28122/")
    # 极黑的布伦希尔德
    comicList.append("https://www.manhuagui.com/comic/1401")
    # ---------------------------------------------------------
    for oneComicUrl in comicList:
        UpdateAll(downloadRootPath, oneComicUrl)
    # ---------------------------------------------------------
    # 输入某一部漫画的 url，选择某一些章节进行下载
    # ChooseEpisode2Process(downloadRootPath)
