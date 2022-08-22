import logging
from re import X
import jieba
from PIL import ImageDraw,Image
import face_recognition
from paddleocr import PaddleOCR,draw_ocr
import numpy as np

logging.getLogger("ppocr").setLevel(logging.INFO)
l = logging.getLogger("图片隐私遮盖程序")
l.setLevel(logging.DEBUG)

def black_highlighter(img_path,secret=("住址","公民身份证号")):
    img_narray = face_recognition.load_image_file(img_path)
    l.info("开始加载人脸识别模型")
    face_locations = face_recognition.face_locations(img_narray)
    l.info("人脸识别定位完成：检测到"+str(len(face_locations))+"张人脸")
    top, right, bottom, left = face_locations[0]
    scale = 0.4
    top -= int((bottom-top)*scale)
    left -=int((right-left)*scale)
    right += int((right-left)*scale)
    bottom += int((bottom-top)*scale)
    level = 30
    img = Image.fromarray(img_narray)
    face_image = Image.fromarray(img_narray[top:bottom:level,left:right:level]).resize((right-left,bottom-top),
                                resample = Image.NEAREST)
    img.paste(face_image,(left,top))
    # ImageDraw.Draw(img).rectangle((left,top,right,bottom),outline=(255,0,0))
    l.info("人脸马赛克完成")
    l.info("开始遮盖隐私文字："+str(secret))
    l.info("开始加载OCR模型")
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    result = ocr.ocr(np.asarray(img),cls=True)
    l.info("OCR识别完成")
    lines = [line for line in result]
    
    for index,line in enumerate(lines):
        text = line[1][0]
        print(text)
        # l.info(list(jieba.cut(text)))
        if text == "出生":
            ImageDraw.Draw(img).rectangle(lines[index+1][0][0]+lines[index+1][0][-2],fill=(0,0,0))
        elif text.startswith("出生"):
            left,top,right,bottom = lines[index][0][0]+lines[index][0][-2]
            import math
            print(left)
            left += int((right-top)*(6/len(text)))
            print(left)
            ImageDraw.Draw(img).rectangle((left,top,right,bottom),fill=(0,0,0))
        elif text == "住址":
            left,top,right,bottom = lines[index+1][0][0]+lines[index+1][0][-2]
            x = int((bottom-top)*0.3)
            top -= x
            bottom += x
            ImageDraw.Draw(img).rectangle((left,top,right,bottom),fill=(0,0,0))
            ImageDraw.Draw(img).rectangle(lines[index+2][0][0]+lines[index+2][0][-2],fill=(0,0,0))

        elif text=="公民身份号码":
            left,top,right,bottom = lines[index+1][0][0]+lines[index+1][0][-2]
            x = int((bottom-top)*0.3)
            top -= x
            bottom += x
            ImageDraw.Draw(img).rectangle((left,top,right,bottom),fill=(0,0,0))
            break
    l.info("隐私文字遮盖完毕")
    import os
    l.info("处理完成:"+os.path.join(os.getcwd(),"out.png"))
    img.show()
    img.save("out.png")

if __name__ == "__main__":
    img_path = "身份证.jpg"
    Image.open(img_path).show()
    black_highlighter(img_path)