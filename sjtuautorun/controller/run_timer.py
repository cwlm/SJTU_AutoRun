import os
import time

from sjtuautorun.constants.data_roots import *

from .emulator import Emulator
from .windows_controller import check_network
from ..constants.custom_exceptions import CriticalErr, NetworkErr, ImageNotFoundErr
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

        # 识别是否存在搜索框
        ret = self.wait_image(IMG.start_image[1])
        if ret is None:
            self.set_text_size()
            self.restart()
            return

        pos = self.wait_image(IMG.start_image[2], timeout=0.5)

        if pos:
            self.logger.info("Close the update window")
            self.Android.click(pos[0], pos[1])

        pos = self.wait_image(IMG.start_image[1])
        if not pos:
            raise ImageNotFoundErr("Cannot find the searching bar")

        self.Android.click(pos[0], pos[1])
        self.text('去跑步')

        pos = self.wait_image(IMG.start_image[3])
        if pos is None:
            raise ImageNotFoundErr("Cannot find the go running icon")
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

            elif not check_network():
                for i in range(11):
                    time.sleep(10)
                    if check_network():
                        break
                    if i == 10:
                        raise NetworkErr()

            elif self.Android.is_app_running():
                raise CriticalErr("CriticalErr on restart function")

            self.Windows.connect_android()
            self.restart(times + 1)

    def confirm(self, must_confirm=0, delay=0.5, confidence=0.9, timeout=0):
        """等待并点击弹出在屏幕中央的各种确认按钮

        Args:
            must_confirm (int, optional): 是否必须按. Defaults to 0.
            delay (float, optional): 点击后延时(秒). Defaults to 0.5.
            timeout (int, optional): 等待延时(秒),负数或 0 不等待. Defaults to 0.

        Raises:
            ImageNotFoundErr: 如果 must_confirm = True 但是 timeout 之内没找到确认按钮排除该异常
        Returns:
            bool:True 为成功,False 为失败
        """
        ret = self.wait_images(IMG.confirm_image[1:], confidence=confidence, timeout=timeout)
        if ret is None:
            if must_confirm == 1:
                raise ImageNotFoundErr("no confirm image found")
            else:
                return False
        pos = self.get_image_position(IMG.confirm_image[ret + 1], confidence=confidence, need_screen_shot=0)
        self.Android.click(pos[0], pos[1], delay=delay)
        return True

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
        self.confirm(must_confirm=1, timeout=10)
        return True
