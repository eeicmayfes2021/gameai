from libc.math cimport sin,cos,pi,sqrt
cpdef int WIDTH=600
cpdef int HEIGHT=1000
cpdef int BALL_RADIUS=30
cpdef float FRICTION=0.008

cdef class Stone:
    cdef public str camp
    cdef public double x[2]
    cdef public double v[2]
    cdef public int radius
    cdef public double angle
    def __init__(self,camp,v,theta):
        self.camp=camp
        self.x=[WIDTH/2.0,0.0]
        if self.camp=="AI":
            self.x=[WIDTH/2,HEIGHT]
        self.v=[v*cos(theta*pi/180),v*sin(theta*pi/180)]
        self.radius=BALL_RADIUS
        self.angle=0
    cpdef move(self):
        vnorm= sqrt(self.v[0]*self.v[0]+self.v[1]*self.v[1])
        if vnorm>FRICTION:
            self.v=[self.v[0]*(vnorm-FRICTION)/vnorm,self.v[1]*(vnorm-FRICTION)/vnorm] #0.05減速
        else:
            self.v=[0,0]#停止
            return False
        self.x[0]+=self.v[0]
        self.x[1]+=self.v[1]
        if self.x[0]>WIDTH-self.radius: #x軸方向に反転
            self.x[0]=2*(WIDTH-self.radius)-self.x[0]
            self.v[0]=-self.v[0]
        elif self.x[0]<0+self.radius: #x軸方向に反転
            self.x[0]=2*(0+self.radius)-self.x[0]
            self.v[0]=-self.v[0]
        if self.x[1]>HEIGHT-self.radius: #y軸方向に反転
            self.x[1]=2*(HEIGHT-self.radius)-self.x[1]
            self.v[1]=-self.v[1]
        elif self.x[1]<0+self.radius: #y軸方向に反転
            self.x[1]=2*(0+self.radius)-self.x[1]
            self.v[1]=-self.v[1]
        self.angle+=3
        return True
    cpdef collision(self,other):
        dist=sqrt( (self.x[0]-other.x[0])*(self.x[0]-other.x[0])+(self.x[1]-other.x[1])*(self.x[1]-other.x[1]))
        if dist>self.radius+other.radius or dist==0:
            return
        #衝突している時
        #運動方程式解いた
        e= [(self.x[0]-other.x[0])/dist,(self.x[1]-other.x[1])/dist]
        t=(self.v[0]*e[0]+self.v[1]*e[1])-(other.v[0]*e[0]+other.v[1]*e[1])
        self.v=[self.v[0]-t*e[0],self.v[1]-t*e[1]]
        other.v=[other.v[0]+t*e[0],other.v[1]+t*e[1]]
    cpdef return_dist(self):
        center=[WIDTH/2,HEIGHT/2]
        dist=sqrt( (self.x[0]-center[0])*(self.x[0]-center[0])+(self.x[1]-center[1])*(self.x[1]-center[1]))
        return dist
    cpdef encode(self):
        return {'x': str(self.x[0]),
            'y': str(self.x[1]),
            'radius':self.radius,
            'camp':self.camp,
            'angle':str(self.angle)}

def calculatePoint(stones):
    score=0
    player1_min_dist=1001001001
    player2_min_dist=1001001001
    for stone in stones:
        dist=stone.return_dist()
        if stone.camp=='you':
            player1_min_dist=min(player1_min_dist,dist)
        else:
            player2_min_dist=min(player2_min_dist,dist)
    score=0
    if player1_min_dist<player2_min_dist : #win player 1
        for stone in stones:
            if stone.camp=='you' and stone.return_dist()<player2_min_dist:
                score+=1 #player1のreward
    else: #win player 2
        for stone in stones:
            if stone.camp=='AI' and stone.return_dist()<player1_min_dist:
                score-=1 #player1のreward
    return score

cpdef movestones(list stones):#ボトルネック#400ループぐらいする
    while True:
        isend=True
        iscollisionlist=[]
        for i in range(len(stones)):
            ismove=stones[i].move()
            if ismove:
                isend=False
                for j in range(len(stones)):
                    if i!=j and (j,i) not in iscollisionlist:
                        stones[i].collision(stones[j])
        if isend:
            return
