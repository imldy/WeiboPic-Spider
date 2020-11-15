import os
import time

import requests


class Blogger(object):
    def __init__(self, uid, endTimeStamp):
        '''
        :param uid: 博主uid
        :param endTimeStamp: 过去某个时间点的时间戳
        '''
        self.uid = uid
        # 给此博主创建目录
        self.path = "{}/{}".format(dir, self.uid)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.albumID = 3561598992750714
        self.endTimeStamp = endTimeStamp
        self.maxPage = 100


class Picture(object):
    def __init__(self, createdTime, picName, picTimeStamp, picHost):
        # # 如果含"日"，则代表要修改日期显示的格式
        # if "日" in self.createdTime:
        #     self.createdTime = "{}-{}".format("", self.createdTime.replace("日", "").replace("月", "-"))
        self.picName = picName
        self.picHost = picHost
        self.picTimeStamp = picTimeStamp
        self.createdTime = time.strftime("%Y-%m-%d", time.localtime(self.picTimeStamp))
        self.picEntireName = "{}-{}".format(self.createdTime, self.picName)
        self.path = ""


class Json(object):
    pars = {
        "false": False,
        "true": True,
        "null": None
    }


class User(object):
    def __init__(self, uid, endTimeStamp):
        self.username = ""
        self.password = ""
        self.session = requests.session()
        self.session.headers = {
            "cookie": "SINAGLOBAL=626278599611.878.1605254150631; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhN.S1EjWebU_fzrPf2LSo_5JpX5KMhUgL.Fo-XehBpehnN1hn2dJLoI7L1K0ylKLYEeh5t; ALF=1636955046; SSOLoginState=1605419047; SCF=ApIIV-qu85xls9BcJJUkgACkGJTOIfweVBxh8S3vv2Diu1gMaLAO-dGZKXsyOcFAvUwWZ83T5UeT5RmFcIQd5NA.; SUB=_2A25ytLB3DeRhGeNK61YQ8CbLwzSIHXVRw6a_rDV8PUNbmtAKLXTfkW9NSTDnXgKO1X670ZYVUsf0s7ZznwKUEgtX; _s_tentry=login.sina.com.cn; Apache=5963842306642.673.1605419053838; ULV=1605419053906:3:3:2:5963842306642.673.1605419053838:1605417871665; UOR=tophub.today,s.weibo.com,www.google.com; webim_unReadCount=%7B%22time%22%3A1605423319378%2C%22dm_pub_total%22%3A8%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A53%2C%22msgbox%22%3A0%7D",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        }
        # 目标博主
        self.objBlogger = Blogger(uid, endTimeStamp)

    def getAllPic(self):
        for p in range(1, self.objBlogger.maxPage + 1):
            print("正在进行第 {} 页".format(p))
            self.getPicListResponse(p)

    def getPicListResponse(self, page):
        url = "https://photo.weibo.com/photos/get_all?uid={}&album_id={}&count=100&page={}&type=3".format(
            self.objBlogger.uid, self.objBlogger.albumID, page)
        response = self.session.get(url=url)
        self.weiboPicResponse = response
        self.extractPic()

    def extractPic(self):
        info = eval(self.weiboPicResponse.text, Json.pars)
        picList = []
        num = 0
        for photo in info["data"]["photo_list"]:
            # print(i)
            # print(type(i))
            num += 1
            print("正在提取第 {} 个图片".format(num))
            pic = Picture(photo["created_at"], photo["pic_name"], photo["timestamp"],
                          photo["pic_host"].replace("\\", ""))
            picList.append(pic)
        self.downloadPic(picList)
        if picList[-1].picTimeStamp < self.objBlogger.endTimeStamp:
            print("已到达设定的时间点，程序停止")
            exit(0)

    def downloadPic(self, picList):
        num = 0
        for pic in picList:
            num += 1
            print("正在下载第 {} 个图片。".format(num), end="")
            url = "{}/large/{}".format(pic.picHost, pic.picName)
            print(url, end=" ")
            response = self.session.get(url)
            self.savePic(response, pic)

    def savePic(self, response, pic):
        pic.path = "{}/{}".format(self.objBlogger.path, pic.picEntireName)
        print(pic.path)
        with open(pic.path, "wb") as f:
            f.write(response.content)


if __name__ == '__main__':
    dir = "pic"
    if not os.path.exists(dir):
        os.mkdir(dir)
    # endTimeStamp: 过去某个时间点的时间戳
    # 程序思路：爬从当前到过去某个时间点发布的微博的照片
    # 1584015741: 2020/3/12 20:22:21
    uid = input("请输入微博博主UID")
    endTimeStamp = input("请输入历史时间的时间戳")
    user = User(uid=uid, endTimeStamp=endTimeStamp)
    print("开始爬取")
    user.getAllPic()
