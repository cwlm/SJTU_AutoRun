import numpy as np
import time

from .emulator import Emulator


class Timer(Emulator):
    """程序运行记录器, 用于记录和传递部分数据"""

    def __init__(self, config, logger):
        super().__init__(config, logger)

        self.app_name = "edu.sjtu.infoplus.taskcenter"

        # ========== 启动交我办 ==========
        if not self.Android.is_app_running():
            self.Android.start_app(self.app_name)

        # ========== 检查页面状态、进入跑步 ============
        # 还没做
        self.change_location(121.431588, 31.026867)
        time.sleep(20)

        # ========== 开始跑步 ============
        start_longitude = 121.431588
        end_longitude = 121.443628
        start_latitude = 31.026867
        end_latitude = 31.030699

        num_steps = 2501

        for i in range(1, num_steps):
            # 计算经纬度的插值
            current_longitude = np.interp(i, [1, num_steps - 1], [start_longitude, end_longitude])
            current_latitude = np.interp(i, [1, num_steps - 1], [start_latitude, end_latitude])

            # 调用位置变更函数
            self.change_location(current_longitude, current_latitude)

            # 等待0.5秒
            time.sleep(0.1)
