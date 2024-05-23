#tiledownload

```
output = output folder
shp = boundary shp data
zoom = map level (there may only be 16 in Gaodeshan District, arcgis is relatively complete, Google requires you to understand)
```

```
//Packaging command
Pyinstaller -F -w tiledonwload.py -i earth.ico
```

Please use it in the folder, exe running depends on the proj folder.

If it gets stuck, please leave it alone, because an error is thrown because the tiles are not acquired (personal level is limited).

Temporary files are saved under /temp. Remember to delete them. They will also be cleared next time you download them. ·

The actual measured 3 GB Amap map takes 20 minutes to download tiles and 20 minutes to splice into tif.

If the code is helpful to you, please follow the official account. ^-^

Mu who studied gis on a small island

## refer to

https://github.com/jimutt/tiles-to-tiff
#pdfword
40 lines of code to implement batch conversion of pdf to docx gadget
## refer to
https://github.com/python-fan/pdf2word
