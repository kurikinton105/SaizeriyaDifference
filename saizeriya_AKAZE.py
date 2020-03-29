import cv2
import numpy as np

img = cv2.imread('diff2.png') #画像の読み込み
height, width, d = img.shape #高さ、幅、深さ
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # グレースケール化
r, binary = cv2.threshold(gray, 0, 255,cv2.THRESH_OTSU)  #しきい値200で2値化
contours = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

#輪郭の抽出、余白の削除
x1 = [] #x座標の最小値
y1 = [] #y座標の最小値
x2 = [] #x座標の最大値
y2 = [] #y座標の最大値
for i in range(1, len(contours)):
    ret = cv2.boundingRect(contours[i])
    x1.append(ret[0])
    y1.append(ret[1])
    x2.append(ret[0] + ret[2])
    y2.append(ret[1] + ret[3])
x1_min = min(x1)
y1_min = min(y1)
x2_max = max(x2)
y2_max = max(y2)

img = img[0:height, x1_min:x2_max]

height, width,d= img.shape #高さ、幅、深さ(切り出したものの大きさ)
midle = int(width/2)
print(midle)
img1 = img[0:height,0:midle]
img2 = img[0:height,midle:width] #実は、横幅が少し違う...
#img[y:height,x,width]

"""
#差分を表示
result = np.copy(img1) #結果の画像を格納する配列
add = np.copy(img1) #結果の画像を格納する配列
#result = img1-img2 # 差分の計算
result = cv2.absdiff(img1, img2) # 差分の計算

img3 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY) # グレースケール化
img3 = cv2.cvtColor(img3,cv2.COLOR_GRAY2BGR)
print(img3.shape)
print(result.shape)
add = cv2.add(img3,result)
"""

detector = cv2.AKAZE_create()
keypoints1, descriptor1 = detector.detectAndCompute(img1, None)
keypoints2, descriptor2 = detector.detectAndCompute(img2, None)

matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = matcher.match(descriptor1, descriptor2)
dst = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches, None, flags=2)
    
#画像の表示
cv2.imshow('image',dst)
#cv2.imshow('image2',img2)
#cv2.imshow('result',result)
cv2.waitKey(0) #何かしらのキーが押されるまで待つ
cv2.destroyAllWindows() #すべてのWindowを破棄
