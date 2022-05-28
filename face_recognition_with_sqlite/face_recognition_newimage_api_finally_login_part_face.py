import uvicorn
from fastapi import FastAPI
import sys
import base64
import os
import cv2
import time
import numpy as np
from numpy import average, dot, linalg
from PIL import Image
import sqlite3
from matplotlib import pyplot as plt
print("python版本：",sys.version)#3.9.7 (tags/v3.9.7:1016ef3, Aug 30 2021, 20:19:38) [MSC v.1929 64 bit (AMD64)]
print("sqlite3模块的版本号:",sqlite3.version)#2.6.0
print("sqlite3模块的版本号，元组:",sqlite3.version_info)#元组: (2, 6, 0)
print("使用中的 SQLite 库的版本号:",sqlite3.sqlite_version)#3.35.5
# 130481200005282111
# uvicorn face_recognition_newimage_api_finally:app --host '127.0.0.1' --port 5000 --reload


def refreshAge(id, conn, cur):
    global isAdult
    # 时星期
    t = time.localtime()
    hour = str(t.tm_hour)
    wday = str(t.tm_wday + 1)
    now = 2022
    Age = int(id[6:10:1])
    query = "SELECT * FROM People WHERE ID="+id
    user = cur.execute(query).fetchone() # 读出id对应的用户元祖
    user_revisable = list(user) # user_revisable是把元祖user列表化，以便修改
    user_revisable[2] = now-Age
    user = tuple(user_revisable)
    # print('用户的数据：', user)
    query = "UPDATE People SET Age= ? WHERE ID=?"
    data = (user_revisable[2], id)
    cur.execute(query, data, )
    conn.commit()
    print('已更新年龄')
    if user_revisable[2] >= 18:
        isAdult = 2
        print('您已成年，请登录！')
        b = str('您已成年，请登录！')
    elif 20 < int(hour) < 22 and (wday == 5 or wday == 6):
        isAdult = 1
        print('您未成年！但每周六周日的九点到十点可以登录，请登录！')
        b = str('您未成年！但每周六周日的九点到十点可以登录，请登录！')
    else:
        isAdult = 0
        b = str('您未成年！现在不可以登录，每周六周日的九点到十点可以登录。')
        print('您未成年！现在不可以登录，每周六周日的九点到十点可以登录。')
    return b


# base64转图片
def downloadimg(id, img_base64):
    img = base64.b64decode(img_base64)
    file = open("dataSet/inputface"+id+".jpg", 'wb')
    file.write(img)
    file.close()


# base64编码
def encode_base64(id):
    with open("dataSet/Uuser.{}.10.jpg".format(id), "rb") as f:
        img_data = f.read()
        base64_data = base64.b64encode(img_data)
        print(type(base64_data))
        base_str = str(base64_data, 'utf-8')
        print(base_str)
        return base64_data


# base64解码
def decode_base64(base64_data):
    # with open('dataSet/base64.jpg','wb') as file:
    img = base64.b64decode(base64_data)
    # cv2.imwrite('dataSet/user.' + str(id) + "." + str(sample_number) + ".jpg",
    # file.write(img)
    print(type(img))
    return img


# bytes转数组
def bytes_to_numpy(agoImg_bytes):
    image_np = np.frombuffer(agoImg_bytes, dtype=np.uint8)
    image_np2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image_np2


# 解决人脸匹配问题
def get_thum(image, size=(196,196), greyscale=False):
    # 利用image对图像大小重新设置, Image.ANTIALIAS为高质量的
    image = image.resize(size, Image.ANTIALIAS)
    if greyscale:
        # 将图片转换为L模式，其为灰度图，其每个像素用8个bit表示
        image = image.convert('L')
    return image


# 计算图片的余弦距离
def image_similarity_vectors_via_numpy(agoImg, img):
    agoImg = get_thum(agoImg)
    img = get_thum(img)
    images = [agoImg, img]
    vectors = []
    norms = []
    for image in images:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
        vectors.append(vector)
        # linalg=linear（线性）+algebra（代数），norm则表示范数
        # 求图片的范数？？
        norms.append(linalg.norm(vector, 2))
    a, b = vectors
    a_norm, b_norm = norms
    # dot返回的是点积，对二维数组（矩阵）进行计算
    res = dot(a / a_norm, b / b_norm)
    return res


# 登录功能模块
def login(uid, keyword, id, name, img_base64):
    global isuid, iskeyword
    conn = sqlite3.connect("FaceBase")
    cur = conn.cursor()
    query = "SELECT * FROM People WHERE uid=" + uid
    usertuple = cur.execute(query).fetchone()
    # print("用户的元祖数据：", usertuple)
    isuidExist = 0
    if usertuple is not None:
        isuidExist = 1
        user = np.asarray(usertuple)
        # print("用户的数组数据：", user)
    if isuidExist == 1:
        if keyword == user[6]:
            print("密码匹配成功！")
            isuid = True
            iskeyword = True
            realName(id, name, conn, cur, user, img_base64)
        else:
            print("密码错误！")
            isuid = True
            iskeyword = False
            return iskeyword
    else:
        print("账号不存在，已为您用此账号注册！")
        isuid = False
        # return isuid
        # 注册
        query = "INSERT INTO People(uid, keyword) VALUES(?,?)"
        data = (uid, keyword)
        cur.execute(query, data)
        conn.commit()
        # 查询
        query = "SELECT * FROM People WHERE uid=" + uid
        usertuple = cur.execute(query).fetchone()
        user = np.asarray(usertuple)
        realName(id, name, conn, cur, user, img_base64)
    conn.commit()
    cur.close()
    conn.close()


# 实名认证
def realName(id, name, conn, cur, user, img_base64):
    global isid, isidone
    print("idlx", type(id))#str
    # print("user", user)#数组
    print("user[0]lx", type(user[0]))#int
    print("user[0]", user[0])
    user_id = str(user[0])
    print("user_id", type(user_id))#str
    if user_id == id:
        print("身份证号码与先前绑定一致！")
        isid = 1
        isidone = True
        faceRecognition(id, img_base64)
        # 新录入人脸-----------------------------------------------------------------------------------
        # img_base64 = face
        img = cv2.imread("dataSet/inputface"+id+".jpg", cv2.IMREAD_GRAYSCALE)
        faceMatching(id, conn, cur, user, img)
        insertFacetoDB(id, conn, cur, img_base64)
        # 身份证号码唯一性
    elif user[0] is None:
        print("您未绑定身份证，正在为您用此身份证号码绑定！")
        isid = 0
        # return isid
        try:
            query = "UPDATE People SET ID=?, Name=? WHERE uid=?"
            # user[5]和uid一样吧？
            data = (id, name, user[5])
            cur.execute(query, data)
            conn.commit()
        except Exception as IDError:
            print("此身份证号码已经被使用，请重新输入！")
            isidone = False
            # return isid
        else:
            isidone = True
            # print("人脸识别前的人脸base64码：", img_base64)
            faceRecognition(id, img_base64)
            # print("调用插入数据库前的人脸base64码：", img_base64)
            insertFacetoDB(id, conn, cur, img_base64)
            refreshAge(id, conn, cur)
    elif user_id != id:
        print("身份证号码与先前绑定不一致！", id, user_id)
        isid = 2


# 人脸识别 img_base64是base64
def faceRecognition(id, img_base64):
    global isfacerecognition
    # sample_number = 0
    # 这里可以按照后续需求添加一个判断语句
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 摄像头，0为电脑内置摄像头 必须指定CAP_DSHOW(Direct Show)参数初始化摄像头,否则无法使用更高分辨率
    # while True:
    # 将+号替换为空格
    # downloadimg(id, face + "==")
    # img_base64 = face.replace(' ', '+')
    # print("写入前一句被执行！", type(img_base64), img_base64)
    downloadimg(id, img_base64)
    img = base64.b64decode(img_base64)
    # print("写入后一句被执行！", type(img))# base64解码的时候出错了
    # byte转数组
    img_np2 = bytes_to_numpy(img)
    # print("byte转数组成功！", img_np2)
    gray = cv2.cvtColor(img_np2, cv2.COLOR_BGR2GRAY)  # BGR转GRAY
    # print("gray成功！", gray)
    # opencv2检测人脸 函数介绍：参数1：image--待检测图片，一般为灰度图像加快检测速度；参数2：objects--被检测物体的矩形框向量组；
    # 参数3：scaleFactor--表示在前后两次相继的扫描中，搜索窗口的比例系数。默认为1.1即每次搜索窗口依次扩大10%;
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    print("识别人脸情况：", faces, type(faces))
    if faces is not None:
        for (x, y, w, h) in faces:
            if not os.path.exists('dataSet'):
                os.makedirs('dataSet')
                # 旧id新人脸存入User中
                print("写入前一句被执行！!", type(img_base64))
                cv2.imwrite('dataSet/Uuser.' + str(id) + ".jpg", gray[y:y + h, x:x + w])  # 保存图像 # 保存路径
                print("写入后一句被执行！!", type(img))
            # cv2.rectangle(img_np2, (x - 50, y - 50), (x + w + 50, y + h + 50), (0, 255, 0),2)  # 绘制方框的图像，起始坐标，终止坐标，颜色，粗细
            roi_gray = gray[y:y + h, x:x + w]  # GRAY   分片
            roi_color = img_np2[y:y + h, x:x + w]  # img分片
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex - 50, ey - 50), (ex + ew + 50, ey + eh + 50), (0, 0, 255), 2)
                print("人脸识别成功！！")
                isfacerecognition = True
                return isfacerecognition
    else:
        print("人脸识别失败，请重试！")
        isfacerecognition = False
        return isfacerecognition


# 人脸匹配
def faceMatching(id, conn, cur, user, img):
    global isfacematching
    # 先前图片的base64码
    agoImg_base64 = user[3]
    # 先前图片
    agoImg_bytes = decode_base64(agoImg_base64)
    # base64转到了bytes数据类型，还需要把bytes数据类型转数组
    image_np2 = bytes_to_numpy(agoImg_bytes)
    print("image_np2的数据类型是", type(image_np2))
    agoImg_PIL = Image.fromarray(np.uint8(image_np2))
    # img表示新录入的人脸图像，agoImg表示数据库已存人脸图像
    img_PIL = Image.fromarray(np.uint8(img))
    print("agoImg_PIL和img_PIL的数据类型是", type(agoImg_PIL), type(img_PIL))
    # 余弦相似度
    cosin = image_similarity_vectors_via_numpy(agoImg_PIL, img_PIL)
    print('图片余弦相似度', cosin)
    if cosin > 0.8:
        query = "UPDATE People SET Face_img=? WHERE ID=?"
        data = (agoImg_base64, id)
        cur.execute(query, data)
        conn.commit()
        print('人脸匹配成功，系统正在检测是否未成年')
        isfacematching = True
        # return isfacematching
        refreshAge(id, conn, cur)
    else:
        print('人脸匹配未成功，请重试！')
        isfacematching = False
        return isfacematching


# 直接把第十张图片作为该用户的人脸数据
def insertFacetoDB(id, conn, cur, img_base64):
    # print("插入数据库的人脸base64码：", img_base64)  此处已出错！！！
    query = "UPDATE People SET Face_img=? WHERE ID=?"
    data = (img_base64, id)
    cur.execute(query, data)
    conn.commit()


def delete(uid):
    conn = sqlite3.connect("FaceBase")
    cur = conn.cursor()
    query = "SELECT * FROM People WHERE uid=" + uid
    usertuple = cur.execute(query).fetchone()
    # print("用户的元祖数据：", usertuple)
    user = np.asarray(usertuple)
    # print("用户的数组数据：", user)
    if user[3] is None:
        query = "DELETE FROM People WHERE uid=" + uid
        cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()


face_cascade = cv2.CascadeClassifier('Classifiers/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('Classifiers/haarcascade_eye.xml')

app = FastAPI()
# global isuid, iskeyword


isuid = False
iskeyword = False
isid = 0
isidone = False
isfacerecognition = False
isfacematching = False
isAdult = 0
@app.get("/index/")
def useridname(uid, keyword, id, name, face):
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 摄像头，0为电脑内置摄像头 必须指定CAP_DSHOW(Direct Show)参数初始化摄像头,否则无法使用更高分辨率
    global isuid, iskeyword, isid, isidone, isfacerecognition, isfacematching, isAdult
    try:
        # img_base64正确
        img_base64 = face.replace(' ', '+')
        login(uid, keyword, id, name, img_base64)
        # isuid, iskeyword, isid, isidone, isfacerecognition, isfacematching, isAdult
        print("返回的结果是：", isuid, iskeyword, isid, isidone, isfacerecognition, isfacematching, isAdult)
        return{"isuid": isuid, "iskeyword": iskeyword, "isid": isid, "isidone": isidone, "isfacerecognition": isfacerecognition, "isfacematching": isfacematching, "isAdult": isAdult}
    finally:
        delete(uid)
        isuid = False
        iskeyword = False
        isid = 0
        isidone = False
        isfacerecognition = False
        isfacematching = False
        isAdult = 0
    # res = "成功传给后台并运行完成！"
    # return{res}
    # res = insertOrUpdate(id, name, cap)
    # return{"id": res[0], "name": res[1]}


if __name__ == '__main__':
    uvicorn.run(app='face_recognition_newimage_api_finally_login_part_face:app', reload=True, debug=True)
# 修改为：http://0.0.0.0:5000
# 运行服务器指令为：
# uvicorn face_recognition_newimage_api_finally_login_part_face:app --host '127.0.0.1' --port 5000 --reload

# 130481200005282111
# uvicorn face_recognition_newimage_api_finally:app --host '127.0.0.1' --port 5000 --reload


