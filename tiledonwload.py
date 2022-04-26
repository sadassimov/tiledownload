import PySimpleGUI as sg
import urllib.request
import os
import glob
import shutil
from osgeo import gdal
from math import log, tan, radians, cos, pi, floor, degrees, atan, sinh

temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
os.environ['PROJ_LIB'] = r'./proj'


def sec(x):
    return (1 / cos(x))


def latlon_to_xyz(lat, lon, z):
    tile_count = pow(2, z)
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return (tile_count * x, tile_count * y)


def bbox_to_xyz(lon_min, lon_max, lat_min, lat_max, z):
    x_min, y_max = latlon_to_xyz(lat_min, lon_min, z)
    x_max, y_min = latlon_to_xyz(lat_max, lon_max, z)
    return (floor(x_min), floor(x_max),
            floor(y_min), floor(y_max))


def mercatorToLat(mercatorY):
    return (degrees(atan(sinh(mercatorY))))


def y_to_lat_edges(y, z):
    tile_count = pow(2, z)
    unit = 1 / tile_count
    relative_y1 = y * unit
    relative_y2 = relative_y1 + unit
    lat1 = mercatorToLat(pi * (1 - 2 * relative_y1))
    lat2 = mercatorToLat(pi * (1 - 2 * relative_y2))
    return (lat1, lat2)


def x_to_lon_edges(x, z):
    tile_count = pow(2, z)
    unit = 360 / tile_count
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return (lon1, lon2)


def tile_edges(x, y, z):
    lat1, lat2 = y_to_lat_edges(y, z)
    lon1, lon2 = x_to_lon_edges(x, z)
    return [lon1, lat1, lon2, lat2]


def fetch_tile(x, y, z, tile_source):
    url = tile_source.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))

    if not tile_source.startswith("http"):
        return url.replace("file:///", "")

    path = f'{temp_dir}/{x}_{y}_{z}.png'
    urllib.request.urlretrieve(url, path)
    return path


def merge_tiles(input_pattern, output_path):
    vrt_path = temp_dir + "/tiles.vrt"
    gdal.BuildVRT(vrt_path, glob.glob(input_pattern))
    gdal.Translate(output_path, vrt_path)


def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    gdal.Translate(os.path.join(temp_dir, f'{temp_dir}/{x}_{y}_{z}.tif'),
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)


def donwload(tile_source, output_dir, bounding_box, zoom):
    lon_min, lat_min, lon_max, lat_max = bounding_box

    # Script start:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    x_min, x_max, y_min, y_max = bbox_to_xyz(
        lon_min, lon_max, lat_min, lat_max, zoom)
    alltiles = (x_max - x_min + 1) * (y_max - y_min + 1)
    print(f"总共：{alltiles} 瓦片")
    i = 0
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            try:
                i = i + 1
                png_path = fetch_tile(x, y, zoom, tile_source)
                print(f"{x},{y} 下载进度{i}/{alltiles}")
                georeference_raster_tile(x, y, zoom, png_path)
            except OSError:
                print(f"错误, failed to get {x},{y}")
                pass

    print("下载与转换瓦片成功")
    print("整合瓦片中请稍后。。。")
    merge_tiles(temp_dir + '/*.tif', output_dir + '/out.tif')
    print(f"整合完成！输出至{output_dir}/out.tif'")
    shutil.rmtree(temp_dir)


def gui():
    layout = [
        [sg.FolderBrowse('选择输出文件夹', key='folder', target='file'), sg.Button('开始'), sg.Button('关闭')],
        [sg.Text('输出文件夹为:', font=("宋体", 10)), sg.Text('', key='file', size=(50, 1), font=("宋体", 10))],
        [sg.Combo(['高德地图', '谷歌地图', 'arcgis地图'], key='tile_source', default_value='高德地图', size=(21, 1)),
         sg.Text('下载地图级别'),
         sg.InputText(size=(20, 1), key='zoom')],
        [sg.Text('lng_min'), sg.InputText(size=(19, 1), key='lng_min'), sg.Text('lat_min'),
         sg.InputText(size=(19, 1), key='lat_min')],
        [sg.Text('lng_max'), sg.InputText(size=(19, 1), key='lng_max'), sg.Text('lat_max'),
         sg.InputText(size=(19, 1), key='lat_max')],
        [sg.Output(size=(70, 5), font=("宋体", 10))]
    ]

    window = sg.Window('在线地图下载器 -_-', layout, font=("宋体", 10), default_element_size=(50, 1), icon='./proj/earth.ico')

    while True:
        event, values = window.read()
        if event in (None, '关闭'):  # 如果用户关闭窗口或点击`关闭`
            break
        if event == '开始':
            if values['tile_source'] == '高德地图':
                tile_source = 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
            elif values['tile_source'] == '谷歌地图':
                tile_source = 'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
            elif values['tile_source'] == 'arcgis地图':
                tile_source = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
            output = values['folder']
            lng_min = int(values['lng_min'])
            lat_min = int(values['lat_min'])
            lng_max = int(values['lng_max'])
            lat_max = int(values['lat_max'])
            zoom = int(values['zoom'])
            donwload(tile_source, output, [lng_min, lat_min, lng_max, lat_max], zoom)



if __name__ == '__main__':
    gui()
