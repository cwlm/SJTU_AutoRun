import numpy as np
import time
from PIL import Image

from .emulator import Emulator
from ..constants.custom_exceptions import CriticalErr, NetworkErr
from sjtuautorun.constants.image_templates import IMG


class Timer(Emulator):
    """程序运行记录器, 用于记录和传递部分数据"""

    def __init__(self, config, logger):
        super().__init__(config, logger)

        self.app_name = "edu.sjtu.infoplus.taskcenter"
        self.start()

    def start(self):
        if not self.Android.is_app_running():
            self.Android.start_app(self.app_name)
        else:
            self.restart()
        res = self.wait_image(IMG.start_image[1])
        if res is None:
            return
        #     if self.image_exist(IMG.setting_image[1]):
        #         pass
        #         # To be done: modify the text size or languages
        #     else:
        #         self.restart()

        self.Android.click(res[0], res[1])
        self.text('去跑步')

        res = self.wait_image(IMG.start_image[2])
        if res is None:
            return
        self.Android.click(res[0], res[1])
        self.logger.info("Start successfully!")

    def restart(self, times=0, *args, **kwargs):
        try:
            self.Android.ShellCmd(f"am force-stop {self.app_name}")
            self.Android.ShellCmd("input keyevent 3")
            self.start()
        except:
            if not self.Windows.is_android_online():
                pass

            elif times == 1:
                raise CriticalErr("on restart,")

            elif not self.Windows.check_network():
                for i in range(11):
                    time.sleep(10)
                    if self.Windows.check_network():
                        break
                    if i == 10:
                        raise NetworkErr()

            elif self.Android.is_app_running():
                raise CriticalErr("CriticalErr on restart function")

            self.Windows.connect_android()
            self.restart(times + 1, *args, **kwargs)

    def run(self):
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
