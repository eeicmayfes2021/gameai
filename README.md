# mayfes20201-gameai
## 開発方法
models以下に
https://drive.google.com/drive/folders/1vk-7_WMdSPf_ULpmY1LY4dX0Ek6Ebx1S?usp=sharing
から好きなモデルを持ってきて配置する．

```bash
$ npm install
$ npm run build
$ pip install aiohttp
$ pip install python-socketio
pip install git+https://github.com/openai/gym
$ pip install torch
$ python server.py
```

## 機械学習によるモデルの生成
```
$ python ddqn_curling_discrete.py #(機械学習によるmodel.ptの生成)
```
生成したモデルを使うときは
server.pyの
```
net_load =  torch.load("models/model_003000.pt")
```
部分の変更を忘れずに！
## メモ
以下のことはまだやらなくても動きます（後で追加したいのでメモ）
[three.js](http://threejs.org/build/three.js)をダウンロードしてstaticに配置する

[フォント](https://raw.githubusercontent.com/mrdoob/three.js/master/examples/fonts/helvetiker_bold.typeface.json)をダウンロードしてstaticに配置する。

