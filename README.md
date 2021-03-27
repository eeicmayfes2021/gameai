# mayfes20201-gameai
## 開発方法
[three.js](http://threejs.org/build/three.js)をダウンロードしてstaticに配置する
[フォント](https://raw.githubusercontent.com/mrdoob/three.js/master/examples/fonts/helvetiker_bold.typeface.json)をダウンロードしてstaticに配置する。
$ npm install
$ node server.js
$ pip install aiohttp
$ pip install python-socketio
### 参考
https://paiza.hatenablog.com/entry/paizacloud_online_multiplayer_game
を参考にして作りました。

クライアント部分でゲームのほぼ全てを動かし、サーバー側からは相手の動かし方（現在はランダム）を伝えるという形でやっています。
相手の動かし方をいずれは機械学習で学習したものに置き換えようと思っています。
