import os
import time
import sys
import requests


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
        # # 如果含"日"，则代表要修改日期显示的格式
        # if "日" in self.createdTime:
        #     self.createdTime = "{}-{}".format("", self.createdTime.replace("日", "").replace("月", "-"))
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
    def __init__(self, COOKIE, uid, albumID, endTimeStamp):
        self.username = ""
        self.password = ""
        self.session = requests.session()
        self.session.headers = {
            "cookie": COOKIE,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        }
        # 目标博主
        self.objBlogger = Blogger(uid, albumID, endTimeStamp)
        self.countNum = 0

    def getAllPic(self):
        for p in range(1, self.objBlogger.maxPage + 1):
            print("正在进行第 {} 页".format(p))
            self.getPicListResponse(p)

    def getPicListResponse(self, page):
        url = "https://photo.weibo.com/photos/get_all?uid={}&album_id={}&count=100&page={}&type=3".format(
            self.objBlogger.uid, self.objBlogger.albumID, page)
        response = self.session.get(url=url)
        self.weiboPicResponse = response
        self.extractPic(page)

    def extractPic(self, currentPage):
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
        if len(picList) == 0 or picList[-1].picTimeStamp < self.objBlogger.endTimeStamp:
            print("已到达设定的时间点或已经到最后，程序停止")
            exit(0)

    def downloadPic(self, picList, currentPage):
        num = 0
        for pic in picList:
            num += 1
            self.countNum += 1
            print("正在下载第 {}/{}/{} 个图片。".format(num, currentPage, self.countNum), end="")
            url = "{}/large/{}".format(pic.picHost, pic.picName)
            print(url, end=" ")
            pic.path = "{}/{}".format(self.objBlogger.path, pic.picEntireName)
            if self.fileExists(pic):
                print("已存在：{}".format(pic.picEntireName))
            else:
                response = self.session.get(url)
                self.savePic(response, pic)

    def fileExists(self, pic):
        if os.path.exists(pic.path):
            return True
        else:
            return False

    def savePic(self, response, pic):
        print(pic.path)
        with open(pic.path, "wb") as f:
            f.write(response.content)


if __name__ == '__main__':
    dir = "pic"
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
    # endTimeStamp: 过去某个时间点的时间戳
    # 程序思路：爬从当前到过去某个时间点发布的微博的照片
    # 1584015741: 2020/3/12 20:22:21
    # 根据参数长度判断启动时有没有输入参数
    if len(sys.argv) == 1:
        # 启动时没输入参数
        # 正常模式启动
        uid = input("请输入微博博主UID: ")
        albumID = input("请输入博主专辑ID(不输入则视为所有专辑): ")
        print("本程序会爬取历史时间到当前时间之间发布的图片")
        endTimeStamp = input("请输入历史时间的时间戳(为空则视为所有图片): ")
    else:
        # 启动时输入了参数
        uid = sys.argv[1]
        # 根据参数长度判断是否指定了专辑ID和截至时间戳
        if len(sys.argv) >= 3:
            # 指定了两个或以上个数的参数
            albumID = sys.argv[2]
            # 判断是不是指定了三个或以上个参数
            if len(sys.argv) >= 4:
                # 如果是，即第三个指定了
                endTimeStamp = sys.argv[3]
            else:
                # 如果第三个没指定
                endTimeStamp = ""
        else:
            # 只指定了一个参数，那么另外俩就是空
            albumID = ""
            endTimeStamp = ""

    if endTimeStamp == "":
        endTimeStamp = 0
    else:
        endTimeStamp = int(endTimeStamp)
    user = User(COOKIE=COOKIE, uid=uid, albumID=albumID, endTimeStamp=endTimeStamp)
    print("开始爬取")
    user.getAllPic()
