import os
import re
import subprocess
import time
from subprocess import check_output

import airtest.core.android.android
from airtest.core.api import connect_device

from constants.custom_exceptions import CriticalErr
from constants.data_roots import ADB_ROOT
from utils.function_wrapper import try_for_times


# Win 和 Android 的通信
# Win 向系统写入数据


class WindowsController:
    def __init__(self, config, logger) -> None:
        self.logger = logger

        self.emulator = config["type"]  # 模拟器类型
        self.emulator_name = config["emulator_name"]
        self.emulator_dir = config["emulator_dir"]  # 模拟器路径
        if self.emulator == "蓝叠 Hyper-V":
            assert config["config_file"], "Bluestacks 需要提供配置文件"
            self.emulator_config_file = config["config_file"]

        self.exe_name = os.path.basename(self.emulator_dir)  # 自动获得模拟器的进程名

    # ======================== 网络 ========================
    def check_network(self):
        """检查网络状况

        Returns:
            bool:网络正常返回 True,否则返回 False
        """
        return os.system("ping www.moefantasy.com") == 0

    def wait_network(self, timeout=1000):
        """等待到网络恢复"""
        start_time = time.time()
        while time.time() - start_time <= timeout:
            if self.check_network():
                return True
            time.sleep(10)

        return False

    # ======================== 模拟器 ========================

    # @try_for_times()
    def connect_android(self) -> airtest.core.android.android.Android:
        """连接指定安卓设备
        Returns:
            dev: airtest.
        """
        if not self.is_android_online():
            self.restart_android()
            time.sleep(15)

        if self.emulator == "雷电":
            dev_name = f"ANDROID:///{self.emulator_name}"
        elif self.emulator == "蓝叠 Hyper-V":
            with open(self.emulator_config_file, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith("bst.instance.Pie64.status.adb_port="):
                    port = line.split("=")[-1].strip()[1:-1]
                    dev_name = f"ANDROID:///127.0.0.1:{port}"

        from logging import ERROR, getLogger

        getLogger("airtest").setLevel(ERROR)

        start_time = time.time()
        while time.time() - start_time <= 30:
            try:
                dev = connect_device(dev_name)
                self.logger.info("Android Connected!")
                return dev
            except:
                pass

        self.logger.error("连接模拟器失败！")
        raise CriticalErr("连接模拟器失败！")

    def is_android_online(self):
        """判断 timer 给定的设备是否在线
        Returns:
            bool: 在线返回 True, 否则返回 False
        """
        raw_res = check_output(f'tasklist /fi "ImageName eq {self.exe_name}').decode(
            "gbk")
        return "PID" in raw_res

    def kill_android(self):
        try:
            subprocess.run(["taskkill", "-f", "-im", self.exe_name])
        except:
            pass

    def start_android(self):
        emulator_index = (int(re.search(r'\d+', self.emulator_name).group()) - 5554) / 2
        try:
            console_dir = os.path.join(os.path.dirname(self.emulator_dir), "ldconsole.exe")
            os.popen(console_dir + " launch --index " + str(emulator_index))
            start_time = time.time()
            while not self.is_android_online():
                time.sleep(1)
                if time.time() - start_time > 120:
                    raise TimeoutError("模拟器启动超时！")
        except Exception as e:
            self.logger.error(f"{e} 请检查模拟器路径!")
            raise CriticalErr("on Restart Android")

    def restart_android(self):
        self.kill_android()
        self.start_android()
