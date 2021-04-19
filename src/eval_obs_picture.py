import sys
import math
import numpy as np
import itertools
import random
import tensorflow as tf
import copy
import matplotlib.pyplot as plt
from cdefinitions import *
from variables import *


episode_num=1000
match_per_episode=100
SAVE_NUM=10 #モデルを保存する
EVAL_NUM=10 #モデルを評価する

#ランダムと
epsilon_begin = 1.0
epsilon_end = 0.3
epsilon_decay = episode_num
epsilon_func = lambda step: max(epsilon_end, epsilon_begin - (epsilon_begin - epsilon_end) * (step / epsilon_decay))

model = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten(),
  tf.keras.layers.InputLayer(input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(64, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(STONE_NUM*2+1, activation=tf.nn.softmax)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

def stonesToObs(stones): #Stoneの塊をobs(numpy.ndarray)に変換する
    obs=np.array([[[0 for k in range(2)] for j in range(WIDTH//20)] for i in range(HEIGHT//20)],dtype=np.uint8)
    i_you=0
    i_AI=STONE_NUM
    for stone in stones:
        w=int( min((WIDTH//20)-1,stone.x[0]//20) )
        h=int( min((HEIGHT//20)-1,stone.x[1]//20) )
        if stone.camp=='you':
            obs[h][w][0]=1
        else:
            obs[h][w][1]=1
    return obs

def choiceSecond(stones):#後攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            temp_stones=copy.deepcopy(stones)
            temp_stones.append(Stone("AI",velocity,theta))
            movestones(temp_stones)
            obs=stonesToObs(temp_stones)
            obs_list.append(obs)
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    next_score_probs=model.predict(np.asarray(obs_list))
    itr=0
    for velocity in velocity_choices:
        for theta in theta_choices:
            next_score=0.0
            for i in range(STONE_NUM*2+1):
                next_score+=next_score_probs[itr][i]*(i-STONE_NUM)
            #print(next_score)
            if next_score>max_score:
                max_score=next_score
                max_theta=theta
                max_velocity=velocity
            itr+=1
    return max_velocity,max_theta

def choiceFirst(stones):#先攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            temp_stones=copy.deepcopy(stones)
            temp_stones.append(Stone("you",velocity,theta))
            movestones(temp_stones)
            obs=stonesToObs(temp_stones)
            obs_list.append(obs)
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    next_score_probs=model.predict(np.asarray(obs_list))
    itr=0
    for velocity in velocity_choices:
        for theta in theta_choices:
            next_score=0.0
            for i in range(STONE_NUM*2+1):
                next_score+=next_score_probs[itr][i]*(i-STONE_NUM)
            next_score=-next_score #先攻なので！
            #print(next_score)
            if next_score>max_score:
                max_score=next_score
                max_theta=theta
                max_velocity=velocity
            itr+=1
    return max_velocity,max_theta


scores_list=[]
for episode in range(episode_num):
    print("episode:",episode)
    obs_list=[]
    scores=[]
    for match in range(match_per_episode):
        #一回プレイする
        stones=[]
        side=-1
        while len(stones)<STONE_NUM*2:
            camp= "you" if side==1 else "AI"
            if random.random()<epsilon_func(episode):#Stoneをランダムに追加
                velocity=random.choice( velocity_choices )
                theta=random.choice( theta_choices )
            else: #評価関数に従って追加
                velocity,theta= choiceFirst(stones) if side==1 else choiceSecond(stones)    
            stones.append(Stone(camp,velocity,theta))
            #運動
            movestones(stones)
            #obs_listに記録
            obs_list.append(stonesToObs(stones))
            side=-side
        #(後攻にとっての)終局時の得点を計算
        score=calculatePoint(stones)
        score=-score#後攻にとってのreward
        #終局時の点数と各状況を紐付けてネットワークを学習させる
        for i in range(STONE_NUM*2):
            scores.append(score+STONE_NUM)
    obs_list=np.asarray(obs_list,dtype=np.float32)
    scores=np.asarray(scores)
    model.fit(obs_list,scores,epochs=3)
    #EVAL_NUMエピソードごとに10回プレイした平均点を記録してplot
    if episode%EVAL_NUM==0:
        print("evaluating...",episode)
        total_score=0
        plays=10
        for play in range(plays):
            stones=[]
            side=-1
            while len(stones)<STONE_NUM*2:
                camp= "you" if side==1 else "AI"
                if side==1:
                    #先手はランダム
                    velocity=random.choice(velocity_choices )
                    theta=random.choice(theta_choices )
                    stones.append(Stone(camp,velocity,theta))
                else:
                    velocity,theta=choiceSecond(stones)
                    stones.append(Stone(camp,velocity,theta))
                movestones(stones) 
                side=-side
            score=-calculatePoint(stones)
            total_score+=score
        print("average_score:",total_score/plays)
        scores_list.append(total_score/plays)
        x=[i*EVAL_NUM for i in range(len(scores_list))]
        plt.plot(x,scores_list,'b+')
        plt.savefig("graphs/eval_obs.png")
    #SAVE_NUMエピソードごとにモデルを保存 https://www.tensorflow.org/guide/saved_model
    if episode%SAVE_NUM==0:
        tf.saved_model.save(model, 'models/eval_obs_{:0=6}/'.format(episode))
        print("saved ",'models/eval_obs_{:0=6}/'.format(episode))
