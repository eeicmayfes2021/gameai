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
pip install git+https://github.com/openai/gym
$ pip install torch
$ pip install tensorflow
$ python server.py
```

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

