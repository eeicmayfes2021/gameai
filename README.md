# mayfes20201-gameai
## 開発方法
models以下に
https://drive.google.com/drive/folders/1vk-7_WMdSPf_ULpmY1LY4dX0Ek6Ebx1S?usp=sharing
から好きなモデルの**フォルダ**を持ってきて配置する．

```bash
$ npm install
$ npm run build
$ pip install aiohttp
$ pip install python-socketio
$ pip install tensorflow
$ pip install cpython
$ pip install --upgrade cython
$ python setup.py build_ext --inplace
$ python server.py
```

## ゲームバランスの調整の仕方
球の個数や摩擦力や速度・角度の制限などを変えるときは，サーバ側では`cdefinitions.pyx`と`variables.py`，クライアント側では`index.js`を変更する必要があります（cpdefの変数がpython側から認識できないため…）
## 機械学習によるモデルの生成
```
$ python eval_obs.py
```
生成したモデルを使うときは
server.pyの
```
model_load= tf.keras.models.load_model('models/eval_obs_000010')
```
部分の変更を忘れずに！
## メモ
以下のことはまだやらなくても動きます（後で追加したいのでメモ）
[three.js](http://threejs.org/build/three.js)をダウンロードしてstaticに配置する

[フォント](https://raw.githubusercontent.com/mrdoob/three.js/master/examples/fonts/helvetiker_bold.typeface.json)をダウンロードしてstaticに配置する。

```
python setup.py build_ext --inplace
```

