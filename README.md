# mayfes20201-gameai
## 開発方法
```bash
$ npm install
$ pip install aiohttp
$ pip install python-socketio
pip install git+https://github.com/openai/gym
$ pip install torch
$ python ddqn_curling_discrete.py #(機械学習によるmodel.ptの生成)
$ python server.py
```

model_xxxxxx.ptは生成に時間がかかるので，フロントエンドの動きだけ見たい時などはddqn_curling_discrete.pyを実行してepisode1が終わったらすぐ終了して，model_000000.ptを使ってやってもいいでしょう．

server.pyの
```
net_load =  torch.load("models/model_003000.pt")
```
の変更を忘れずに！
## メモ
以下のことはまだやらなくても動きます（後で追加したいのでメモ）
[three.js](http://threejs.org/build/three.js)をダウンロードしてstaticに配置する

[フォント](https://raw.githubusercontent.com/mrdoob/three.js/master/examples/fonts/helvetiker_bold.typeface.json)をダウンロードしてstaticに配置する。

