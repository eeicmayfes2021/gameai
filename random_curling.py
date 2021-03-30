import math
import random
import curlingenv

import gym

env = gym.make('curlingenv-v0')


num_episodes = 300
num_steps_per_episode = 20

collected_rewards = []
for i in range(num_episodes):
    s = env.reset()
    total_reward = 0
    done = False

    for j in range(num_steps_per_episode):
        m = random.uniform(10,170),random.uniform(0,5)
        #print ("m: ", m)
        s1, reward, done, info = env.step(m)
        total_reward += reward
        s = s1
        if done:
            break
    # env.render()
    #total_reward *= oom;
    collected_rewards.append(total_reward)

    print("after " + str(i + 1) + " episodes:")
    average = sum(collected_rewards) / len(collected_rewards)
    score = collected_rewards[-1]
    print("average score: ", average)
    print("score:", score)
    print()
print("#########")
