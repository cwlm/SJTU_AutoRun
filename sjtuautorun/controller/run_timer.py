import os
import numpy as np
import time

from sjtuautorun.constants.data_roots import *

from .emulator import Emulator


class Timer(Emulator):
    """程序运行记录器, 用于记录和传递部分数据"""

    def __init__(self, config, logger):
        super().__init__(config, logger)

        if not self.config.PLAN_ROOT:
            self.logger.warning(
                f"No PLAN_ROOT specified, default value {os.path.join(DATA_ROOT, 'plans')} will be used")
            self.config.PLAN_ROOT = os.path.join(DATA_ROOT, "plans")

        self.app_name = "edu.sjtu.infoplus.taskcenter"

        # ========== 启动交我办 ==========
        if not self.Android.is_app_running():
            self.Android.start_app(self.app_name)

        # ========== 检查页面状态、进入跑步 ============
        # 还没做
        self.change_location(121.431588, 31.026867)
        time.sleep(10)
