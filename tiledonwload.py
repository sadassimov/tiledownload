import PySimpleGUI as sg
import urllib.request
import os
import glob
import shutil
from osgeo import gdal
from osgeo import ogr, osr
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
    print(f"?????????{alltiles} ??????")
    i = 0
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            try:
                i = i + 1
                png_path = fetch_tile(x, y, zoom, tile_source)
                print(f"{x},{y} ????????????{i}/{alltiles}")
                georeference_raster_tile(x, y, zoom, png_path)
            except OSError:
                print(f"??????, failed to get {x},{y}")
                pass

    print("???????????????????????????")
    print("?????????????????????????????????")
    merge_tiles(temp_dir + '/*.tif', output_dir + '/out.tif')
    print(f"????????????????????????{output_dir}/out.tif'")
    shutil.rmtree(temp_dir)


def VectorTranslategetexent(
        shapeFilePath,
        format="GeoJSON",
        accessMode=None,
        dstSrsESPG=4326,
        selectFields=None,
        geometryType="POLYGON",
        dim="XY",
):
    ogr.RegisterAll()
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
    data = ogr.Open(shapeFilePath)
    layer = data.GetLayer()
    spatial = layer.GetSpatialRef()
    layerName = layer.GetName()
    data.Destroy()
    dstSRS = osr.SpatialReference()
    dstSRS.ImportFromEPSG(int(dstSrsESPG))
    dataname = layerName + ".shp"
    saveFolderPath = shapeFilePath.replace(dataname, '')
    if format == "GeoJSON":
        destDataName = layerName + ".json"
        destDataPath = os.path.join(saveFolderPath, destDataName)
        print(destDataName)
    elif format == "ESRI Shapefile":
        destDataName = os.path.join(saveFolderPath, layerName)
        flag = os.path.exists(destDataName)
        os.makedirs(destDataName) if not flag else None
        destDataPath = os.path.join(destDataName, layerName + ".shp")
    else:
        print("?????????????????????")
        return
    options = gdal.VectorTranslateOptions(
        format=format,
        accessMode=accessMode,
        srcSRS=spatial,
        dstSRS=dstSRS,
        reproject=True,
        selectFields=selectFields,
        layerName=layerName,
        geometryType=geometryType,
        dim=dim
    )
    gdal.VectorTranslate(
        destDataPath,
        srcDS=shapeFilePath,
        options=options
    )

    return extent


def gui():
    layout = [
        [sg.FolderBrowse('?????????????????????', key='folder', target='file'), sg.Button('??????'), sg.Button('??????')],
        [sg.Text('??????????????????:', font=("??????", 10)), sg.Text('', key='file', size=(50, 1), font=("??????", 10))],
        [sg.Combo(['????????????', '????????????', '?????????xyz??????'], key='tile_source', default_value='?????????xyz??????', size=(21, 1)),
         sg.Text('??????????????????'),
         sg.InputText(size=(20, 1), key='zoom')],
        [sg.InputText(size=(70, 1), key='xyzlink')],
        [sg.FileBrowse('????????????shp', key='fileshp', target='shp')],
        [sg.Text('????????????shp???:', font=("??????", 10)), sg.Text('', key='shp', size=(50, 1), font=("??????", 10))],
        [sg.Output(size=(70, 5), font=("??????", 10))]
    ]

    window = sg.Window('????????????????????? -_-', layout, font=("??????", 10), default_element_size=(50, 1), icon='./proj/earth.ico')

    while True:
        event, values = window.read()
        if event in (None, '??????'):  # ?????????????????????????????????`??????`
            break
        if event == '??????':
            if values['tile_source'] == '????????????':
                tile_source = 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
            elif values['tile_source'] == '????????????':
                tile_source = 'http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}'
            elif values['tile_source'] == '?????????xyz??????':
                tile_source = values['xyzlink']
            output = values['folder']
            zoom = int(values['zoom'])
            fileshp = values['fileshp']
            jsonFilePath = fileshp.replace('.shp', '.json')
            data = ogr.Open(jsonFilePath)
            layer = data.GetLayer()
            extent = layer.GetExtent()
            donwload(tile_source, output, [extent[0], extent[2], extent[1], extent[3]], zoom)


if __name__ == '__main__':
    gui()

VectorTranslategetexent(fileshp)
