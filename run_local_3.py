import numpy as np
import time
from flatland.envs.rail_generators import complex_rail_generator

from flatland.envs.schedule_generators import complex_schedule_generator
from flatland.envs.rail_env import RailEnv
from flatland.utils.rendertools import RenderTool
from flatland.envs.observations import GlobalObsForRailEnv
from flatland.envs.malfunction_generators import malfunction_from_params
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.schedule_generators import sparse_schedule_generator
import random
from flatland.core.grid.grid4_utils import get_new_position
import r2_solver
from flatland.envs.predictions import ShortestPathPredictorForRailEnv
from flatland.envs.observations import TreeObsForRailEnv
import copy
from collections import defaultdict


from src.graph_observations import GraphObsForRailEnv
from src.predictions import ShortestPathPredictorForRailEnv
from src.optimizer import optimize, get_action_dict
from itertools import groupby

import cv2

#test_list = [1, 4, 4, 4, 5, 6, 7, 4, 3, 3, 9]
#res = [[i, len(list(i_list))] for i, i_list in groupby(test_list)]
#print(res)

if __name__ == "__main__":
    NUMBER_OF_AGENTS = 7
    width = 40
    height = 40
    max_prediction_depth = 200
    NUM_CITIES = 4

    rail_generator = sparse_rail_generator(max_num_cities=NUM_CITIES,
                                           grid_mode=True,
                                           max_rails_between_cities=2,
                                           max_rails_in_city=3,
                                           seed=1500)

    observation_builder = GraphObsForRailEnv(predictor=ShortestPathPredictorForRailEnv(max_depth=max_prediction_depth),
                                             bfs_depth=200)

    env = RailEnv(
        width=width, height=height,
        rail_generator=rail_generator,
        obs_builder_object=observation_builder,
        schedule_generator=sparse_schedule_generator(),
        number_of_agents=NUMBER_OF_AGENTS
    )

    env_renderer = RenderTool(env)
    obs, _ = env.reset()

    for step in range(8 * (width + height + 20)):

        obs = optimize(observation_builder, obs)
        _action = get_action_dict(observation_builder, obs)

        next_obs, all_rewards, done, _ = env.step(_action)

        #print("Rewards: {}, [done={}]".format(all_rewards, done))

        img = env_renderer.render_env(show=True,
                                      show_inactive_agents=False,
                                      show_predictions=True,
                                      show_observations=True,
                                      frames=True,
                                      return_image= True)

        #cv2.imwrite("./env_images/"+str(step).zfill(3)+".jpg", img)

        #time.sleep(1.0)

        obs = copy.deepcopy(next_obs)
        if obs is None or done['__all__']:
            break
