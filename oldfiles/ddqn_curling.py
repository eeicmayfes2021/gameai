import random

import gym
import matplotlib.pyplot as plt
import numpy as np

import torch
from torch import nn, optim
import math
from IPython.display import HTML
import curlingenv

env = gym.make('curlingenv-v0')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
STONE_NUM=5 #envのstone_numと合わせる

class PrioritizedReplayBuffer(object):
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size 
        self.index = 0                 
        self.buffer = []                
        self.priorities = np.zeros(buffer_size, dtype=np.float32)
        self.priorities[0] = 1.0         
    
    def __len__(self):
        return len(self.buffer)
    def push(self, experience):
        if len(self.buffer) < self.buffer_size:
            self.buffer.append(experience)
        else:
            self.buffer[self.index] = experience
        self.priorities[self.index] = self.priorities.max()
        self.index = (self.index + 1) % self.buffer_size
    def sample(self, batch_size, alpha=0.6, beta=0.4):
        priorities = self.priorities[: self.buffer_size if len(self.buffer) == self.buffer_size else self.index] #>入っている経験の数まで取り出す
        priorities = priorities ** alpha
        prob = priorities / priorities.sum()
        indices = np.random.choice(len(self.buffer),size=batch_size,p=prob)
        weights = (len(self.buffer)*prob[indices])**(-beta) 
        weights = weights / max(weights)
        obs, action, reward, next_obs, done = zip(*[self.buffer[i] for i in indices])
        return (torch.stack(obs),
                torch.as_tensor(action), 
                torch.as_tensor(reward, dtype=torch.float32),
                torch.stack(next_obs), 
                torch.as_tensor(done, dtype=torch.uint8),
                indices,
                torch.as_tensor(weights, dtype=torch.float32))

    def update_priorities(self, indices, priorities):
        self.priorities[indices] = priorities + 1e-4

def sigmoid(a):
    s = 1 / (1 + math.e**-a)
    return s
def zerotoone(x,a,b): #(0,1)でxなのを(a,b)に拡張
    return  x*(b-a)+a

class CNNQNetwork(nn.Module):
    def __init__(self, state_shape, n_action):
        super(CNNQNetwork, self).__init__()
        self.state_shape = state_shape
        self.n_action = n_action
        
        self.fc_state = nn.Sequential(
            nn.Linear(STONE_NUM*4, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

        self.fc_advantage = nn.Sequential(
            nn.Linear(STONE_NUM*4, 16),
            nn.ReLU(),
            nn.Linear(16, n_action)
        )
    
    def forward(self, obs):
        feature = obs
        feature = feature.view(feature.size(0), -1)

        state_values = self.fc_state(feature)
        advantage = self.fc_advantage(feature) 
        action_values = state_values + advantage - torch.mean(advantage, dim=1, keepdim=True)
        return action_values

    def act(self, obs, epsilon):
        if random.random() < epsilon:
            action = env.action_space.sample() 
            cmp,act=action
            action=act
        else:
            with torch.no_grad():
                action = self.forward(obs.unsqueeze(0))[0]
                #出力をvelocity=0.5~5,theta=10~170に制限する
                action[0]=zerotoone(sigmoid(action[0]/10),2,4)
                action[1]=zerotoone(sigmoid(action[1]/10),10,170)
                action=action.to(device).detach().numpy().copy()
                #print("action:",action)
        #print("action:",action)
        return action


buffer_size = 100000 
initial_buffer_size = 10000 
replay_buffer = PrioritizedReplayBuffer(buffer_size)

net = CNNQNetwork(env.observation_space.shape, n_action=2).to(device)
target_net = CNNQNetwork(env.observation_space.shape, n_action=2).to(device)
target_update_interval = 2000


optimizer = optim.Adam(net.parameters(), lr=1e-4) 
loss_func = nn.SmoothL1Loss(reduction='none') 

gamma = 0.99
batch_size = 32
n_episodes = 30000 #100000とかでやりたい
SAVE_NUM=1000

beta_begin = 0.4
beta_end = 1.0
beta_decay = 16*n_episodes
beta_func = lambda step: min(beta_end, beta_begin + (beta_end - beta_begin) * (step / beta_decay))

epsilon_begin = 1.0
epsilon_end = 0.01
epsilon_decay = 16*n_episodes
epsilon_func = lambda step: max(epsilon_end, epsilon_begin - (epsilon_begin - epsilon_end) * (step / epsilon_decay))

def update(batch_size, beta):
    obs, action, reward, next_obs, done, indices, weights = replay_buffer.sample(batch_size, beta)
    obs, action, reward, next_obs, done, weights \
        = obs.float().to(device), action.to(device), reward.to(device), next_obs.float().to(device), done.to(device), weights.to(device)

    q_values = net(obs)
    
    with torch.no_grad():
        greedy_action_next = net(next_obs)
        q_values_next = target_net(next_obs)

    reward_np=reward.to(device).detach().numpy().copy()
    two_reward=[]
    for r in reward_np:
        two_reward.append([r,r])
    two_reward=torch.Tensor(two_reward )
    target_q_values = two_reward + gamma * q_values_next #* (1 - done) #ここでバグ
    
    two_weights=[]
    for r in weights:
        two_weights.append([r,r])
    two_weights=torch.Tensor(two_weights )
    optimizer.zero_grad()
    loss = (two_weights * loss_func(q_values, target_q_values)).mean()
    loss.backward()
    optimizer.step()
    
    replay_buffer.update_priorities(indices, (target_q_values - q_values).mean().abs().detach().cpu().numpy())

    return loss.item()

if __name__=="__main__":
    step = 0
    rewards=[]
    for episode in range(n_episodes):
        obs = env.reset()
        done = False
        total_reward = 0
        camp=1
        while not done:
            if camp==1:
                action = env.action_space.sample()
                cmp,act=action
                action=(camp,act)
                #print(action)
                next_obs, reward, done, _ = env.step(action)
                #total_reward += reward
                obs = next_obs
            else:#後手について学習する
                action = net.act(torch.from_numpy(obs.astype(np.float32)).clone().float().to(device), epsilon_func(step))
                action=(camp,action)
                #print(action)
                next_obs, reward, done, _ = env.step(action)
                total_reward += reward
                replay_buffer.push([torch.from_numpy(obs.astype(np.float32)).clone(), action[1], reward, torch.from_numpy(next_obs.astype(np.float32)).clone(), done])
                obs = next_obs

            # ネットワークを更新            
            if len(replay_buffer) > initial_buffer_size:
                #print("update")
                update(batch_size, beta_func(step))

            # ターゲットネットワークを定期的に同期させる
            if (step + 1) % target_update_interval == 0:
                target_net.load_state_dict(net.state_dict())
            
            step += 1
            camp=-camp

        print('Episode: {},  Step: {},  Reward: {}'.format(episode + 1, step + 1, total_reward))
        rewards.append(total_reward)
        if episode%SAVE_NUM==0:
            x=[i for i in range(len(rewards))]
            plt.plot(x,rewards,"bo")
            plt.savefig("graphs/continuous_{:0=6}.png".format(episode))
            torch.save(net, 'models/continuous_model_{:0=6}.pt'.format(episode))
            torch.save(target_net, 'models/continuous_target_model_{:0=6}.pt'.format(episode))