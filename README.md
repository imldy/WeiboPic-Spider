# 微博博主图片爬取

## 功能

根据微博博主的UID，下载其发布的所有图片。可以限制只下载从过去某个时间点到现在的图片。

运行环境：python3+requests

## 运行

使用方式：

```
Usage: python mian.py -u/--uid <博主uid> -a/--albumID <专辑id> -t/--timeStamp <时间戳> -p/--path <保存路径>

Options:
  -h, --help            显示此程序帮助信息并退出
  -u UID, --uid=UID     微博博主的uid
  -a ALBUMID, --albumID=ALBUMID
                        要爬取的博主的专辑id
  -t TIMESTAMP, --timeStamp=TIMESTAMP
                        以前一个时间点的时间戳。若指定，程序会爬取从此时间点到现在发布的图片，否则为全部时间的照片
  -p PATH, --path=PATH  要保存到的位置，默认./pic
```

## 图片保存

图片保存名为：`年-月-日-图片ID+后缀名`，例如：`2020-11-15-4571658324410718.jpg`

优点是文件浏览时与微博图片显示的顺序相同。

## 已知问题：

1. 指定专辑貌似没效果，都是下载的微博配图专辑。
2. 程序功能为每次获取100张图片的信息，但实际有时微博服务器只返回90+张，原因暂时未知。