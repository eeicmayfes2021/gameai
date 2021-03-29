from gym.envs.registration import register

register(
    id='curlingenv-v0',
    entry_point='curlingenv.env:CurlingEnv'
)