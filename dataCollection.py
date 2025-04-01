#Imports
import envlogger
from envlogger.testing import catch_env
from envlogger.backends import tfds_backend_writer
import numpy as np
import time
import tensorflow as tf
import tensorflow_datasets as tfds
import os

#where we save logs
log_directory = r"C:\Users\caitl\arm_position_tracking\logs"
os.makedirs(log_directory, exist_ok=True)

#input desired values to record in an episode here
def step_fn(timestep, action, env):
    physics = env.physics  #doesnt work on prelimary run, should work for our environment since it has a .physics attribute
    joint_names = physics.model.body_names
    joint_positions = {
        name: physics.named.data.xpos[name].tolist() for name in joint_names

    }
    return {
        'timestep': time.time(),
        #do we need reward and discount? are we given these
        'reward': float(timestep.reward),
        'discount': float(timestep.discount),
        'joint_torques': action.tolist(), #assuming the action is the joint torques
        'joint_positions': joint_positions,
    }

def episode_fn(timestep, action, env):
    if timestep.first():
        return {
            'start_time': time.time()
        }
    return None

#write in what my policy needs, add onto this later
def policy(timestep):
    obs = timestep.observation
    return obs

dataset_config = tfds.rlds.rlds_base.DatasetConfig(
    name='catch_example',
    observation_info=tfds.features.Tensor(
        shape=(10, 5), dtype=tf.float32,
        encoding = tfds.features.Encoding.ZLIB),
    action_info = tf.int64,
    reward_info = tf.float64,
    discount_info = tf.float64)

#create envlogger instance
env = catch_env.Catch()
with envlogger.EnvLogger(
    env,
    step_fn = step_fn,
    episode_fn = episode_fn,
    backend = tfds_backend_writer.TFDSBackendWriter(
        data_directory = log_directory,
        ds_config = dataset_config),
) as env: #interact with env here
    timestep = env.reset()
    while not timestep.last():
        action = policy(timestep)
        timestep = env.step(action)

