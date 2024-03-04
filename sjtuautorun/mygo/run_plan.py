import os
import random
import time
import numpy as np

from sjtuautorun.constants.data_roots import DATA_ROOT
from sjtuautorun.controller.run_timer import Timer
from sjtuautorun.utils.io import yaml_to_dict, recursive_dict_update
from sjtuautorun.utils.math_functions import calculate_geo_distance
from sjtuautorun.constants.image_templates import IMG


class RunPlan:
    def __init__(self, timer: Timer, user_plan_path=None):
        self.timer = timer
        self.config = timer.config

        plan_args = yaml_to_dict(os.path.join(self.config.PLAN_ROOT, "default.yaml"))
        if user_plan_path is None:
            self.timer.logger.warning(f"No run plan specified, default plan "
                                      f"{os.path.join(DATA_ROOT, 'plans', 'default.yaml')} will be used")
        else:
            user_plan = yaml_to_dict(user_plan_path)
            plan_args = recursive_dict_update(plan_args, user_plan)

        self.plan_args = plan_args
        assert len(plan_args["points"]) >= 2, "请输入两个以上途径点"

    def start_run(self):

        time.sleep(5)
        # 初始化位置
        self.timer.change_location(self.plan_args["points"][0][0], self.plan_args["points"][0][1])

        pos = self.timer.wait_image(IMG.run_image[1])
        self.timer.Android.click(pos[0], pos[1])

        if self.timer.wait_image(IMG.run_image[2]) is not None:
            self.run()

    def run(self):
        time.sleep(3)
        for i in range(len(self.plan_args["points"]) - 1):

            start_longitude = self.plan_args["points"][i][0]
            end_longitude = self.plan_args["points"][i + 1][0]
            start_latitude = self.plan_args["points"][i][1]
            end_latitude = self.plan_args["points"][i + 1][1]

            total_distance = calculate_geo_distance(start_latitude, start_longitude, end_latitude, end_longitude)
            interval = 0.5
            running_pace = random.uniform(3.5, 4)
            step_distance = 1000 * interval / (60 * running_pace)
            num_steps = round(total_distance / step_distance)

            for j in range(1, num_steps):
                start_time = time.time()

                # 计算经纬度的插值
                current_longitude = np.interp(j, [1, num_steps - 1], [start_longitude, end_longitude])
                current_latitude = np.interp(j, [1, num_steps - 1], [start_latitude, end_latitude])

                # 调用位置变更函数
                self.timer.change_location(current_longitude, current_latitude)
                self.timer.logger.debug(current_longitude, current_latitude)

                # 等待0.1秒
                elapsed_time = time.time() - start_time
                time.sleep(max(0.0, interval - elapsed_time))
