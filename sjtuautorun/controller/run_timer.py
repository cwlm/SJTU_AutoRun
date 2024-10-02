import os
import time

from sjtuautorun.constants.data_roots import *

from .emulator import Emulator
from .windows_controller import check_network
from ..constants.custom_exceptions import CriticalErr, NetworkErr, ImageNotFoundErr
from sjtuautorun.constants.image_templates import IMG
from ..utils.new_logger import Logger


class Timer(Emulator):
    """程序运行记录器, 用于记录和传递部分数据"""

    def __init__(self, config, logger):
        super().__init__(config, logger)

        if not self.config.PLAN_ROOT:
            self.logger.info(
                f"No PLAN_ROOT specified, default value {os.path.join(DATA_ROOT, 'plans')} will be used")
            self.config.PLAN_ROOT = os.path.join(DATA_ROOT, "plans")

        self.app_name = "edu.sjtu.infoplus.taskcenter"
        self.start()

    def start(self, times=0):
        if times >= 3:
            raise CriticalErr("Critical Err when starting.")

        # 如果app没有运行,则启动app；否则重启app
        if not self.Android.is_app_running():
            self.Android.start_app(self.app_name)
        else:
            self.Android.ShellCmd(f"am force-stop {self.app_name}")
            self.Android.ShellCmd("input keyevent 3")
            self.start(times)
            return

        # 等待app启动
        ret = self.wait_images(
            [IMG.start_image[1], IMG.update_image[1]], timeout=20 + 15 * times)
        if ret is None:
            self.logger.warning(
                "Cannot find the searching bar, restarting..." + f"Restarting trial {times}.")
            self.start(times + 1)
            return

            # 检查更新窗口
        ret = self.wait_image(IMG.update_image[1], timeout=5)
        if ret:
            self.logger.info("Update Pop-up found, restarting...")
            self.start(times)
            return

            # 检测搜索框
        ret = self.wait_image(IMG.start_image[1], timeout=5)
        if not ret:
            self.logger.warning("Cannot find the searching bar, restarting...")
            self.start(times + 1)
            return
        else:
            self.Android.click(ret[0], ret[1])

        # 输入
        self.text("去跑步")

        # 检测跑步图标
        ret = self.wait_image(IMG.start_image[2], timeout=5)
        if not ret:
            self.logger.warning("Cannot find the go running icon in searching bar, restarting..." +
                                f"Restarting trial {times}.")
            self.start(times + 1)
            return
        else:
            self.Android.click(ret[0], ret[1])

        # ret = self.wait_image(IMG.start_image[3], timeout=5)
        # if not ret:
        #     self.logger.warning("Cannot find the go running icon, restarting..." +
        #                         f"Restarting trial {times}.")
        #     self.start(times + 1)
        #     return
        # else:
        #     self.Android.click(ret[0], ret[1])
            self.logger.info("Started successfully!")

    def confirm(self, must_confirm=0, delay=0.5, confidence=0.9, timeout=0):
        """等待并点击弹出在屏幕中央的各种确认按钮

        Args:
            must_confirm (int, optional): 是否必须按. Defaults to 0.
            delay (float, optional): 点击后延时(秒). Defaults to 0.5.
            confidence (float, optional): 置信度. Defaults to 0.9.
            timeout (int, optional): 等待延时(秒),负数或 0 不等待. Defaults to 0.

        Raises:
            ImageNotFoundErr: 如果 must_confirm = True 但是 timeout 之内没找到确认按钮排除该异常
        Returns:
            bool:True 为成功,False 为失败
        """
        ret = self.wait_images(
            IMG.confirm_image[1:], confidence=confidence, timeout=timeout)
        if ret is None:
            if must_confirm == 1:
                raise ImageNotFoundErr("no confirm image found")
            else:
                return False
        pos = self.get_image_position(
            IMG.confirm_image[ret + 1], confidence=confidence, need_screen_shot=0)
        self.Android.click(pos[0], pos[1], delay=delay)
        return True
