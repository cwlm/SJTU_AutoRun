import os
import time

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
            return

        ret = self.wait_images(IMG.start_image[1:3])
        # 打开应用后可能会出现的状态:
        # None: 打开失败或者字体不正确
        # 0: 预期结果
        # 1: 出现交我办更新，这里选择直接叉掉更新页
        if ret is None:
            self.set_text_size()
            self.restart()
            return
        elif ret == 0:
            pass
        elif ret == 1:
            pos = self.wait_image(IMG.start_image[2])
            self.click(pos[0], pos[1])

        pos = self.wait_image(IMG.start_image[1])
        if not pos:
            raise CriticalErr("Cannot find the searching bar")

        self.Android.click(pos[0], pos[1])
        self.text('去跑步')

        pos = self.wait_image(IMG.start_image[3])
        if pos is None:
            raise CriticalErr("Cannot find the go running icon")
        self.Android.click(pos[0], pos[1])
        self.logger.info("Start successfully!")

    def restart(self, times=0):
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
            self.restart(times + 1)

    def run(self):
        self.change_location(121.431588, 31.026867)
        time.sleep(10)

    def set_text_size(self):
        # 点击设置
        pos = self.wait_image(IMG.setting_image[1])
        if not pos:
            return False
        self.Android.click(pos[0], pos[1])

        # 点击调节字体
        pos = self.wait_image(IMG.setting_image[2])
        if not pos:
            raise CriticalErr("Set text size failed!")
        self.Android.click(pos[0], pos[1])

        # 点击小号字体
        pos = self.wait_image(IMG.setting_image[3])
        if not pos:
            raise CriticalErr("Set text size failed!")
        self.Android.click(pos[0], pos[1])

        # 点击返回
        pos = self.wait_image(IMG.setting_image[4])
        if not pos:
            raise CriticalErr("Set text size failed!")
        self.Android.click(pos[0], pos[1])

        # 点击确定
        pos = self.wait_image(IMG.setting_image[5])
        if not pos:
            raise CriticalErr("Set text size failed!")
        self.Android.click(pos[0], pos[1])
        return True
