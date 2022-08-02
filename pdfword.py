import os
import PySimpleGUI as sg
import sys
from pdf2docx import Converter

def pdf_to_word(pdf_file_path, word_file_path):
    cv = Converter(pdf_file_path)
    cv.convert(word_file_path)
    cv.close()

def pdf2doc(pdf_folder):
    word_folder = pdf_folder
    for file in os.listdir(pdf_folder):
            extension_name = os.path.splitext(file)[1]
            if extension_name != ".pdf":
                continue
            file_name = os.path.splitext(file)[0]
            pdf_file = pdf_folder + "/" + file
            word_file = word_folder + "/" + file_name + ".docx"
            print("正在处理: ", file)
            pdf_to_word(pdf_file, word_file)
    sg.popup('转换完成！word保存于同级目录下')
    sys.exit(0)

def gui():
    layout = [[sg.FolderBrowse('选择pdf文件夹', key='folder', target='file'), sg.Button('开始'), sg.Button('关闭')],
    [sg.Text('输出文件夹为:', font=("宋体", 10)), 
    sg.Text('', key='file', size=(50, 1), font=("宋体", 10))],
    [sg.Output(size=(70, 5), font=("宋体", 10))]]
    window = sg.Window('pdf转word -_-', layout, font=("宋体", 10), default_element_size=(50, 1), icon='./earth.ico')
    while True:
        event, values = window.read()
        if event in (None, '关闭'):  # 如果用户关闭窗口或点击`关闭`
            break
        if event == '开始':
            output = values['folder']
            pdf2doc(output)

if __name__ == '__main__':
    gui()      
