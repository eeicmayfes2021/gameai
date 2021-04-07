import sys

import gym
import numpy as np
import gym.spaces
import math
import itertools

WIDTH=600
HEIGHT=1000
BALL_RADIUS=30
FRICTION=0.01
STONE_NUM=5
#対戦型の環境にする方法がわからない…
class Stone:
    def __init__(self,camp,x,y,v,theta):
        self.camp=camp
        self.y=y
        self.x=x
        if v==0:
            self.v=np.array([0,0])
        else:
            self.v=np.array([v*math.cos(math.radians(theta)),v*math.sin(math.radians(theta))])
        self.radius=BALL_RADIUS
    def move(self):
        vnorm=np.linalg.norm(self.v, ord=2)
        if vnorm>FRICTION:
            self.v=self.v*(vnorm-FRICTION)/vnorm #0.05減速
        else:
            self.v=np.array([0,0])#停止
        self.x+=self.v[0]
        self.y+=self.v[1]
        if self.x>WIDTH: #x軸方向に反転
            self.x=2*WIDTH-self.x
            self.v[0]=-self.v[0]
        if self.x<0: #x軸方向に反転
            self.x=-self.x
            self.v[0]=-self.v[0]
        if self.y>HEIGHT: #y軸方向に反転
            self.y=2*HEIGHT-self.y
            self.v[1]=-self.v[1]
        if self.y<0: #y軸方向に反転
            self.y=-self.y
            self.v[1]=-self.v[1]
    def collision(self,other):
        dist=math.sqrt( (self.x-other.x)**2+(self.y-other.y)**2 )
        if dist>self.radius+other.radius:
            return
        #衝突している時
        #運動方程式解いた
        if dist==0:
            e=np.array([0,0])
        else:
            e=np.array([self.x-other.x,self.y-other.y])/dist
        t=np.dot(self.v,e)-np.dot(other.v,e)
        self.v=self.v-t*e
        other.v=other.v+t*e
    def return_dist(self):
        dist=math.sqrt( (self.x-WIDTH/2)**2+(self.y-HEIGHT/2)**2 )
        return dist
    def encode(self):
        return {'x': self.x,
            'y': self.y,
            'radius':self.radius,
            'camp':self.camp}

class  CurlingEnv(gym.Env):
    metadata = {'render.modes': ['human', 'ansi']}
    MAX_STEPS = 100
    def __init__(self):
        super().__init__()
        # action_space, observation_space, reward_range を設定する
        self.WIDTH=600
        self.HEIGHT=1000
        self.action_space =gym.spaces.Tuple((
            gym.spaces.Discrete(2), #どっちが打つか
            gym.spaces.Box(
                low=np.array([2,45]),#velocity
                high=np.array([4,135]),#theta
                dtype=np.float
            )
            ))
        """
        #Discreteにする方がいいか？
        gym.spaces.Tuple((
            gym.spaces.Discrete(2), #どっちが打つか
            gym.spaces.Discrete(10),#velocity
            gym.spaces.Discrete(161) ))#theta
        """
        """
        #continuousにする方がいいか？
        gym.spaces.Box(
            low=np.array([10,0]),
            high=np.array([170,5]),
            dtype=np.float
        )  # 10度~170度,速さ0~5
        """
        #状態はSTONE_NUM*2個のカーリングの球のx,y,x,y,....(最初のSTONE_NUMつがyou,最後のSTONE_NUMつがAI)
        HIGH=np.array([1000 if i%2 else 600 for i in range(STONE_NUM*4)])
        self.observation_space = gym.spaces.Box(
            low=-1,
            high=HIGH,
            shape=(STONE_NUM*4,),
            dtype=np.int
        )
        self.reward_range = [-STONE_NUM,STONE_NUM]#相手の一番近くにあるストーンより近くにあるストーンの数
        self.reset()

    def reset(self):
        # 諸々の変数を初期化する
        self.stone_position=np.array([-1 for i in range(STONE_NUM*4)])
        return self.stone_position

    def step(self, action):
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)
        #theta=10+action//10 #10,11,...,170
        #velocity=(action%10+1)*0.5 #0.5,1.0,1.5,...,5
        camp,hit=action
        velocity,theta=hit
        #print(camp,velocity,action)
        #状態をStonesにコピー
        self.stones=[]
        for i in range(STONE_NUM):#player1
            if self.stone_position[i*2] >= 0:
                self.stones.append(Stone(
                    'you',
                    self.stone_position[i*2],
                    self.stone_position[i*2+1],
                    0,
                    0))
        for i in range(STONE_NUM,STONE_NUM*2):#player2
            if self.stone_position[i*2] >= 0:
                self.stones.append(Stone(
                    'AI',
                    self.stone_position[i*2],
                    self.stone_position[i*2+1],
                    0,
                    0))
        #新しいコマを配置
        self.stones.append(Stone(
                    "you" if camp==1 else "AI",
                    WIDTH/2,
                    HEIGHT if camp==-1 else 0,
                    velocity,
                    theta))
        #moveする
        while True:
            stillmove = False
            for stone in self.stones:
                stone.move()
                if stone.v[0]!=0 or stone.v[1]!=0:
                    stillmove=True
            for pair in itertools.combinations(self.stones, 2): #衝突判定
                pair[0].collision(pair[1])
            if not stillmove:
                break
        #stone_positionに移す
        self.stone_position=np.array([-1 for i in range(STONE_NUM*4)])
        i_you=0
        i_AI=STONE_NUM
        for stone in self.stones:
            if stone.camp=='you' and i_you<STONE_NUM:
                self.stone_position[i_you*2]=stone.x
                self.stone_position[i_you*2+1]=stone.y
                i_you+=1
            if stone.camp=='AI' and i_AI<STONE_NUM*2:
                self.stone_position[i_AI*2]=stone.x
                self.stone_position[i_AI*2+1]=stone.y
                i_AI+=1

        observation = self.stone_position
        reward = 0 #todo:一番近いストーンの近さに比例したreward
        self.done = ( len(self.stones)==STONE_NUM*2 ) #STONE_NUM*2個全部埋まってたらdone
        #print(len(self.stones),self.done)
        if self.done: #check:self.doneからTrue変更してみて報酬を密にしてみても良い？
            player1_min_dist=1001001001
            player2_min_dist=1001001001
            for i in range(STONE_NUM):#player1
                dist=np.sqrt( (self.stone_position[i*2]-WIDTH/2)**2+(self.stone_position[i*2+1]-HEIGHT/2)**2 )
                player1_min_dist=min(player1_min_dist,dist)
            for i in range(STONE_NUM,STONE_NUM*2):#player1
                dist=np.sqrt( (self.stone_position[i*2]-WIDTH/2)**2+(self.stone_position[i*2+1]-HEIGHT/2)**2 )
                player2_min_dist=min(player2_min_dist,dist)
            if player1_min_dist<player2_min_dist : #win player 1
                for i in range(STONE_NUM):
                    dist=np.sqrt( (self.stone_position[i*2]-WIDTH/2)**2+(self.stone_position[i*2+1]-HEIGHT/2)**2 )
                    if dist<player2_min_dist:
                        reward+=1 #player1のreward
            else: #win player 2
                for i in range(STONE_NUM,STONE_NUM*2):
                    dist=np.sqrt( (self.stone_position[i*2]-WIDTH/2)**2+(self.stone_position[i*2+1]-HEIGHT/2)**2 )
                    if dist<player1_min_dist:
                        reward-=1 #player1のreward
        return observation, camp*reward, self.done, {"stonesize":len(self.stones)}

    def render(self, mode='human', close=False):
        # human の場合はコンソールに出力。ansiの場合は StringIO を返す
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile.write(','.join(self.stone_position) + '\n')
        return outfile

    def close(self):
        pass
    def move_generator(self):
        moves = []
        for theta in range (161):
            for velocity in range(10):
                moves.append(theta*10+velocity)
        return moves