# SaizeriyaDifference
saizeriya_difference

Qiita投稿記事[サイゼリヤの間違い探しを解く（ヒントになる）プログラムを作ってみた]()のソースコードです。








#サイゼリヤの間違い探しを解く（ヒントになる）プログラムを作ってみた
こんにちは。初投稿です。
先日サイゼリヤに行った際の待ち時間20分ぐらい数人でサイゼリヤの間違い探しをやって、見つけられませんでした...(ムズすぎる...)
ということで、画像処理で解けないかな〜と思い、やってみました。OpenCVのいい勉強にもなりました。


#やりたいこと
OpenCVのライブラリを使って、サイゼリヤが公式で出している画像データ[（https://www.saizeriya.co.jp/entertainment/) ](https://www.saizeriya.co.jp/entertainment/)を加工して間違い探しを自動化したい！！！
実際にやることは、

- 画像を加工する（余白の削除、半分に分割）
- 画像の差分を計算
- 差分情報を元の画像に表示

という感じです。
コードは[GitHub](https://github.com/kurikinton105/SaizeriyaDifference)にあげてみました。

#実行環境
macOS Mojave 10.14.4
Python 3.6.7
OpenCV 4.

#画像を加工する
ダウンロードすると、「比較する画像がくっついている」＋「謎の余白がある」ということに気がつきます。
![diff2.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/febd9c06-842f-a4df-f597-73a5027d3a71.png)
*（周りも白なのでわかりづらい...)　サイゼリヤのサイトより引用*

まずはじめに余白部分の削除からしたいと思います。
空白の削除の流れは、
- グレースケール画像にする
- ２値化する
- 輪郭を抽出する
- 輪郭の中から座標が最小になるものと最大になるものをx,yそれぞれ取得して切り取る

[https://qiita.com/trami/items/e25eb70a59a51ae4f7ba#どのようにして余白削除を行うのか](https://qiita.com/trami/items/e25eb70a59a51ae4f7ba#%E3%81%A9%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%81%97%E3%81%A6%E4%BD%99%E7%99%BD%E5%89%8A%E9%99%A4%E3%82%92%E8%A1%8C%E3%81%86%E3%81%AE%E3%81%8B)の記事を参考にさせていただいております。

OpenCVでのグレースケール化の関数が

```python:gray.py
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # グレースケール化
```
２値化の関数が

```python:binary.py
r, binary = cv2.threshold(gray, 0, 255,cv2.THRESH_OTSU)  #2値化
```


画像の切り取りの関数が

```python:cut_img.py
img = img[y1:y2,x1,x2] #(x1,y1)から(x2,y2)を切り取る
```
という感じです。
これらを組み合わせていくとここまでのコードが

```python:saizeriya.py
import cv2
import numpy as np

img = cv2.imread('diff.png') #画像の読み込み
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
img = img[0:600, x1_min:x2_max]
```
実行結果が以下の通りです。うまくカットできていることがわかります。
<img width="1145" alt="スクリーンショット 2020-03-29 19.03.18.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/fcecb7ad-44e6-78c2-4d54-dbcbece1ec49.png">

###次に画像を半分にカットします。

```python:saizeriya.py
height, width,d= img.shape #高さ、幅、深さ(切り出したものの大きさ)
midle = int(width/2)

img1 = img[0:height,0:midle-3]
img2 = img[0:height,midle-8:width-11] #実は、横幅が少し違う... 
```
ここでやばかったのは、実は２つの画像の端のキレている部分が若干違うということでした。
その調整は結局手作業でカットする部分を調整しました。

#画像の差分を計算
次に画像の差分を計算します。
画像の差分はnumpy配列同士の引き算でもできますが、実際に実行してみると差分がわかりづらい（少しの色の違い、場所の少しのずれも差分として表示してしまう）ので、今回はOpenCVの**absdiff**関数を使いました。

**absdiff**関数は、二つの画像の差の絶対値を求めることができます。

```python:saizeriya.py
#差分を表示
result = np.copy(img1) #結果の画像を格納する配列
add = np.copy(img1) #結果の画像を格納する配列
#result = img1-img2 # 差分の計算
result = cv2.absdiff(img1, img2) # 差分の計算(absdiff)
```

実行結果
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/34e4b86e-bf02-5ca0-da34-01327f9be312.png)

参考に配列同士の引き算で実行した時の結果です。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/1aa54469-640c-4f80-5527-e384bf10f11e.png)
*流石にこれはどこが違うのかわからない...*

#差分情報を元の画像に表示
これでは、どこに差があるかわからないので、元の画像と合成したいと思います。
元のグレー画像＋差分画像（カラー）を合成します。

使う関数は**add**関数です。また、**cvtCOLOR**関数で元のカラー画像を

######カラー３次元配列→グレー２次元配列→グレー２次元配列
で処理します。

```python:saizeriya.py
img3 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY) # グレースケール化
img3 = cv2.cvtColor(img3,cv2.COLOR_GRAY2BGR) # グレースケールのままカラー画像にする
print(img3.shape)
print(result.shape)
add = cv2.add(img3,result) # 画像を合成する

#画像の表示
cv2.imshow('all',img)
cv2.imshow('image',add)
cv2.imshow('result',result)
cv2.waitKey(0) #何かしらのキーが押されるまで待つ
cv2.destroyAllWindows() #すべてのWindowを破棄
```

実行結果
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/7ffe07bc-6096-8c67-bb94-7520f603a661.png)


これでだいたいどこが違うかわかるようになりました。

###って８個しか見つからない！！！！
あと２つ教えてください...

あくまで、補助するツールでした。

#12月の間違い探しは９個見つけれました
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/548598/28198e0b-4325-ab5f-fa2a-7e67d7fd08b2.png)
