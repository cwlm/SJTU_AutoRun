import os

from sjtuautorun.constants.data_roots import DATA_ROOT
from sjtuautorun.controller.run_timer import Timer
from sjtuautorun.utils.io import yaml_to_dict, recursive_dict_update


class RunPlan:
    def __init__(self, timer: Timer, user_plan_path=None):
        self.timer = timer
        self.config = timer.config

        plan_args = yaml_to_dict(os.path.join(self.config.PLAN_ROOT, "default.yaml"))
        if user_plan_path is None:
            print("========Warning========")
            print(f"No run plan specified, default plan "
                  f"{os.path.join(DATA_ROOT, 'plans', 'default.yaml')} will be used")
            print("=========End===========")
        else:
            user_plan = yaml_to_dict(user_plan_path)
            plan_args = recursive_dict_update(plan_args, user_plan)

        self.plan_args = plan_args
