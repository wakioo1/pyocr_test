# coding:utf-8
import sys
import os
import re

import tkinter as tk
import tkinter.filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np

import pyocr
import pyocr.builders



TESSERACT_PATH = 'C:\Program Files\Tesseract-OCR'
TESSDATA_PATH = 'C:\Program Files\Tesseract-OCR\\tessdata'

os.environ["PATH"] += os.pathsep + TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

#OCRpyのbuilder
tools = pyocr.get_available_tools()
tool = tools[0]

#各関数
#画像表示の前処理
def conversion_data(imgdata):
    rgb_cv2_image = cv2.cvtColor(imgdata, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_cv2_image)
    tk_img2 = ImageTk.PhotoImage(pil_image)
    return tk_img2

#アスペクト比を維持してresize
def keepAspectResize(org_img):
    re_length = 660
    h, w = org_img.shape[:2]
    re_h = re_w = re_length/max(h,w)
    cv2_img2 = cv2.resize(org_img, dsize=None, fx=re_h , fy=re_w)
    h2, w2 = cv2_img2.shape[:2]
    return cv2_img2

#OCR読み込み用の画像のリサイズ
def ocr_keepAspectResize(org_img):
    re_length = 2400
    h, w = org_img.shape[:2]
    re_h = re_w = re_length/max(h,w)
    ocr_img = cv2.resize(cv2_img, dsize=None, fx=re_h , fy=re_w)
    h2, w2 = ocr_img.shape[:2]
    return ocr_img

#画像の二値化
def threshold_img(img):
    # 元画像をグレースケールに変換
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # グレースケール画像を白黒に変換
    ret, bw_img = cv2.threshold(gray_img, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return bw_img

#画像選択、表示する関数
def getfile():
    global cv2_img
    global tk_img
    f_paht = tk.filedialog.askopenfilename(title="ファイル選択", initialdir="C:\python\tkinter_ocr" ,filetypes=[("Image file", ".png .jpg .jpeg")])
    str_file_paht = str(f_paht)
    #OpenCVで画像を読み込む。各処理を行う。
    cv2_img = cv2.imread(str_file_paht)
    set_img = keepAspectResize(cv2_img)
    #cv2→PIL→tkに変換
    pil_image = Image.fromarray(set_img)
    tk_img = ImageTk.PhotoImage(pil_image)
    #オリジナル画像
    canvas_org.create_image(0, 0, image=tk_img, anchor=tk.NW)

#OCRpy、wordBoxの作成
def create_word_box():
    global pil_out
    global word_box_img
    ocr_resize_img = ocr_keepAspectResize(cv2_img)
    bw_img2 = threshold_img(ocr_resize_img)
    pil_out = Image.fromarray(bw_img2)
    builder = pyocr.builders.WordBoxBuilder(tesseract_layout=3)
    results = tool.image_to_string(pil_out , lang="jpn", builder=builder)
    cv2_out = np.array(pil_out, dtype="uint8")
    for d in results:
        pt1 = (d.position[0])
        pt2 = (d.position[1])
        rectangle_img = cv2.rectangle(cv2_out, tuple(pt1), tuple(pt2), (255, 255, 255), 3)
    tk_word_box_img = keepAspectResize(rectangle_img)
    pil_image = Image.fromarray(tk_word_box_img)
    word_box_img = ImageTk.PhotoImage(pil_image)
    canvas_img.create_image(0, 0, image=word_box_img, anchor=tk.NW)

#OCRpy、テキストの作成
def crate_text():
    global text
    canvas_text.delete("ocr_text")
    texts = []
    builder = pyocr.builders.TextBuilder(tesseract_layout=3)
    respons = tool.image_to_string(pil_out, lang="jpn", builder=builder)
    res = re.subn('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', respons)
    texts.append(res)
    for text in texts:
        canvas_text.create_text(10, 0, text=text, anchor=tk.NW, tag="ocr_text")

def run_ocr():
    create_word_box()
    crate_text()

#ウインドウの作成
root = tk.Tk()
#ウインドウのタイトル
root.title("OCRpy test")
#ウインドウサイズと位置指定(幅、高さ、x座標、y座標)
root.geometry("1820x800+50+50")

#フレームの作成
frame = tk.Frame(root, width=1800, height=780, padx=10, pady=10, bg="#D9D9D9")
frame.place(x=10, y=10)

frame_org = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_org.place(x=10, y=30, width=690, height=680)

frame_img = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_img.place(x=710, y=30, width=690, height=680)

frame_text = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_text.place(x=1410, y=30, width=370, height=680)

#Labelの生成
l_org = tk.Label(frame,text="オリジナル", relief="flat")
l_org.place(x=325, y=720)

l_img = tk.Label(frame,text="OCR認識図", relief="flat")
l_img.place(x=1025, y=720)

l_text = tk.Label(frame,text="読み込みテキスト", relief="flat")
l_text.place(x=1555, y=720)


#ボタン作成
button = tk.Button(frame, text="ファイル選択", command=getfile)
button.place(x=10,y=0)

button = tk.Button(frame, text="OCR処理", command=run_ocr)
button.place(x=710,y=0)


#キャンバス作成・配置
canvas_org = tk.Canvas(frame_org, width=660, height=660)
canvas_org.place(x=10, y=10)

canvas_img = tk.Canvas(frame_img, width=660, height=660)
canvas_img.place(x=10, y=10)

canvas_text = tk.Canvas(frame_text, width=340, height=660)
canvas_text.place(x=10, y=10)

#イベントループ
root.mainloop()