import os
import time
import requests
import optparse


class Blogger(object):
    def __init__(self, uid, albumID, endTimeStamp):
        '''
        :param uid: 博主uid
        :param endTimeStamp: 过去某个时间点的时间戳
        '''
        self.uid = uid
        self.screenName = self.getScreenName()
        # 给此博主创建目录
        self.path = "{}/{}".format(dir, self.screenName)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.albumID = albumID
        self.endTimeStamp = endTimeStamp
        self.maxPage = 100

    def getScreenName(self):
        '''
        获取博主昵称
        :return:
        '''
        response = requests.get("https://m.weibo.cn/api/container/getIndex?type=uid&value={}".format(self.uid))
        return eval(response.text, Json.pars)["data"]["userInfo"]["screen_name"]


class Picture(object):
    def __init__(self, photoID, picName, picTimeStamp, picHost):
        self.picID = photoID
        self.picName = picName
        self.picHost = picHost
        self.picTimeStamp = picTimeStamp
        self.createdTime = time.strftime("%Y-%m-%d", time.localtime(self.picTimeStamp))
        self.picEntireName = "{}-{}{}".format(self.createdTime, self.picID, os.path.splitext(self.picName)[-1])
        self.path = ""


class Json(object):
    pars = {
        "false": False,
        "true": True,
        "null": None
    }


class User(object):
    def __init__(self, COOKIE):
        self.username = ""
        self.password = ""
        self.session = requests.session()
        self.session.headers = {
            "cookie": COOKIE,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        }
        self.countNum = 0

    def getAllPic(self, blogger):
        for p in range(1, blogger.maxPage + 1):
            print("正在进行第 {} 页".format(p))
            self.getPicListResponse(p, blogger)

    def getPicListResponse(self, page, blogger):
        url = "https://photo.weibo.com/photos/get_all?uid={}&album_id={}&count=100&page={}&type=3".format(
            blogger.uid, blogger.albumID, page)
        response = self.session.get(url=url)
        self.weiboPicResponse = response
        self.extractPic(page, blogger)

    def extractPic(self, currentPage, blogger):
        info = eval(self.weiboPicResponse.text, Json.pars)
        picList = []
        num = 0
        for photo in info["data"]["photo_list"]:
            # print(i)
            # print(type(i))
            num += 1
            # print("正在提取第 {}/{} 个图片".format(num, currentPage))
            pic = Picture(photo["photo_id"], photo["pic_name"], photo["timestamp"],
                          photo["pic_host"].replace("\\", ""))
            picList.append(pic)
        self.downloadPic(picList, currentPage)
        if len(picList) == 0 or picList[-1].picTimeStamp < blogger.endTimeStamp:
            print("已到达设定的时间点或已经到最后，程序停止")
            exit(0)

    def downloadPic(self, picList, currentPage, blogger):
        num = 0
        for pic in picList:
            num += 1
            self.countNum += 1
            print("正在下载第 {}/{}/{} 个图片。".format(num, currentPage, self.countNum), end="")
            url = "{}/large/{}".format(pic.picHost, pic.picName)
            print(url, end=" ")
            pic.path = "{}/{}".format(blogger.path, pic.picEntireName)
            if self.fileExists(pic):
                print("已存在：{}".format(pic.picEntireName))
            else:
                response = self.session.get(url)
                self.savePic(response, pic)

    def fileExists(self, pic):
        return os.path.exists(pic.path)

    def savePic(self, response, pic):
        print(pic.path)
        with open(pic.path, "wb") as f:
            f.write(response.content)

    def getBlogerPic(self, blogger):
        self.getAllPic(blogger)


if __name__ == '__main__':
    usage = "python %prog -u/--uid <博主uid> -a/--albumID <专辑id> -t/--timeStamp <时间戳> -p/--path <保存路径>"
    parser = optparse.OptionParser(usage)  ## 写入上面定义的帮助信息
    parser.add_option('-u', '--uid',
                      dest='uid',
                      type='string',
                      help='微博博主的uid')
    parser.add_option('-a', '--albumID',
                      dest='albumID',
                      type='string',
                      help='要爬取的博主的专辑id',
                      default="")
    parser.add_option('-t', '--timeStamp',
                      dest='timeStamp',
                      type='int',
                      help='以前一个时间点的时间戳。若指定，程序会爬取从此时间点到现在发布的图片，否则为全部时间的照片',
                      default=0)
    parser.add_option('-p', '--path',
                      dest='path',
                      type='string',
                      help='要保存到的位置，默认./pic',
                      default="pic")
    options, args = parser.parse_args()
    if options.uid == None:
        print("warning: -u/--uid <博主uid> 为必须项")
        exit(1)
    # 微博博主ID
    uid = options.uid
    # 专辑ID
    albumID = options.albumID
    # endTimeStamp: 过去某个时间点的时间戳
    endTimeStamp = options.timeStamp
    # 图片保存到的目录
    dir = options.path
    if not os.path.exists(dir):
        os.mkdir(dir)
    # 自定义的COOKIE的处理
    if os.path.exists("COOKIE"):
        with open("COOKIE", "r", encoding="utf-8") as f:
            COOKIE = f.read()
    else:
        with open("COOKIE", "w", encoding="utf-8") as f:
            f.write("")
        print("请把你的微博cookie放在程序根目录的COOKIE文件内")
        exit(1)
    blogger = Blogger(uid, albumID, endTimeStamp)
    user = User(COOKIE=COOKIE)
    print("开始爬取")
    user.getBlogerPic(blogger)
