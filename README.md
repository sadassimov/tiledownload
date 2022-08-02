# tiledownload

```
output = 输出文件夹
shp = 边界shp数据
zoom = 地图级别(高德山区可能只有16、arcgis的比较全、google需要你懂的)
```

```
//打包命令
Pyinstaller -F -w tiledonwload.py -i earth.ico
```

请在文件夹中使用，exe 运行依赖于proj 文件夹。

如果卡死，请放着不管，是因为瓦片没有获取到在抛出错误（个人水平有限）。

临时文件保存在/temp下面，记得删除哦，下次下载也会清空的。·

实测3 GB 高德地图需要20分钟瓦片下载，20分钟拼接成tif。

若代码对您有帮助可关注下公众号哦。^-^

在小岛学gis的穆

## 参考

https://github.com/jimutt/tiles-to-tiff
# pdfword
40行代码实现pdf批量转docx小工具
## 参考
https://github.com/python-fan/pdf2word
