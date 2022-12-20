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

def create_img(cv2_img):
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    set_img = cv2.resize(cv2_img, (int(340), int(660)))
    return set_img

#画像選択、表示する関数
def getfile():
    global cv2_img
    global set_img
    global tk_img
    global img
    global pil_image
    f_paht = tk.filedialog.askopenfilename(title="ファイル選択", initialdir="C:\python\tkinter_ocr" ,filetypes=[("Image file", ".png .jpg .jpeg")])
    str_file_paht = str(f_paht)
    #OpenCVで画像を読み込む。各処理を行う。
    cv2_img = cv2.imread(str_file_paht)
    set_img = create_img(cv2_img)
    #cv2→PIL→tkに変換
    rgb_cv2_image = cv2.cvtColor(set_img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_cv2_image)
    tk_img = ImageTk.PhotoImage(pil_image)
    img = format(tk_img)
    #オリジナル画像
    canvas_org.create_image(0, 0, image=img, anchor=tk.NW)

#OCRpy、wordBoxの作成
def create_word_box():
    global word_box
    global word_box_img
    global tk_word_box_img
    pil_out = pil_image
    builder = pyocr.builders.WordBoxBuilder(tesseract_layout=6)
    results = tool.image_to_string(pil_out, lang="jpn", builder=builder)
    cv2_out = np.array(pil_out, dtype="uint8")
    for d in results:
        pt1 = (d.position[0])
        pt2 = (d.position[1])
        cv2_word_box = cv2.rectangle(cv2_out, tuple(pt1), tuple(pt2), (0, 0, 255), 2)
    pil_word_box_img = Image.fromarray(cv2_word_box)
    tk_word_box_img = ImageTk.PhotoImage(pil_word_box_img)
    word_box_img = format(tk_word_box_img)
    canvas_img.create_image(0, 0, image=word_box_img, anchor=tk.NW)

#OCRpy、テキストの作成
def crate_text():
    global text
    canvas_text.delete("ocr_text")
    texts = []
    builder = pyocr.builders.TextBuilder(tesseract_layout=6)
    respons = tool.image_to_string(pil_image, lang="jpn", builder=builder)
    res = re.subn('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', respons)
    texts.append(res)
    for text in texts:
        canvas_text.create_text(0, 0, text=text, anchor=tk.NW, tag="ocr_text")

def run_ocr():
    create_word_box()
    crate_text()

#ウインドウの作成
root = tk.Tk()
#ウインドウのタイトル
root.title("OCRpy test")
#ウインドウサイズと位置指定(幅、高さ、x座標、y座標)
root.geometry("1140x800+50+50")

#フレームの作成
frame = tk.Frame(root, width=1120, height=780, padx=10, pady=10, bg="#D9D9D9")
frame.place(x=10, y=10)

frame_org = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_org.place(x=10, y=30, width=360, height=680)

frame_img = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_img.place(x=380, y=30, width=360, height=680)

frame_text = tk.Frame(frame, relief=tk.FLAT, bg="#E6E6E6", bd=2)
frame_text.place(x=750, y=30, width=360, height=680)

#Labelの生成
l_org = tk.Label(frame,text="オリジナル", relief="flat")
l_org.place(x=155, y=720)

l_img = tk.Label(frame,text="OCR認識図", relief="flat")
l_img.place(x=535, y=720)

l_text = tk.Label(frame,text="読み込みテキスト", relief="flat")
l_text.place(x=895, y=720)


#ボタン作成
button = tk.Button(frame, text="ファイル選択", command=getfile)
button.place(x=10,y=0)

button = tk.Button(frame, text="OCR処理", command=run_ocr)
button.place(x=380,y=0)


#キャンバス作成・配置
canvas_org = tk.Canvas(frame_org, width=340, height=660)
canvas_org.place(x=10, y=10)

canvas_img = tk.Canvas(frame_img, width=340, height=660)
canvas_img.place(x=10, y=10)

canvas_text = tk.Canvas(frame_text, width=340, height=660)
canvas_text.place(x=10, y=10)

#イベントループ
root.mainloop()
#システムアウト
#sys.exit(1)


