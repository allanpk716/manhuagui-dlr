# https://bark.abc.com/123456789/
barkRootUrl = "https://bark.abc.com/123456789/"


def BarkNotify(title, isError):
    try:
        if isError == True:
            requests.post(barkRootUrl + title + ",下载重试多次失败")
        else:
            requests.post(barkRootUrl + title + ",更新完毕")
    except:
        print("bark error")
