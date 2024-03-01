import os
import numpy as np
import time
from PIL import Image

from sjtuautorun.constants.data_roots import *

from .emulator import Emulator
from ..constants.custom_exceptions import CriticalErr, NetworkErr
from sjtuautorun.constants.image_templates import IMG


class Timer(Emulator):
    """程序运行记录器, 用于记录和传递部分数据"""

    def __init__(self, config, logger):
        super().__init__(config, logger)

        if not self.config.PLAN_ROOT:
            self.logger.warning(
                f"No PLAN_ROOT specified, default value {os.path.join(DATA_ROOT, 'plans')} will be used")
            self.config.PLAN_ROOT = os.path.join(DATA_ROOT, "plans")

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
        time.sleep(10)
