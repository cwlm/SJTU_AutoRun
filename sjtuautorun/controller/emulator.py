import os
import cv2
import numpy as np
import subprocess
import json
import time
import logging
from typing import Callable, Any

from enum import Enum


class AppState(Enum):
    STOPPED = 'stopped'
    RUNNING = 'running'
    NOT_INSTALLED = 'not_installed'


class Emulator:
    def __init__(self, config):
        self.emulator_dir = config['emulator_dir']
        self.emulator_index = config['emulator_index']
        self.manager = os.path.join(self.emulator_dir, 'shell', 'mumuManager.exe')
        self.adb = os.path.join(self.emulator_dir, 'shell', 'adb')

        self.__refresh_info__()

    def __refresh_info__(self):
        result = self.manager_run(['info'])
        if result.returncode != 0:
            logging.error("Getting emulator info failed")
        else:
            self.info = json.loads(result.stdout)

    def manager_run(self, command: list[str]):
        return subprocess.run([self.manager, *command, '-v', str(self.emulator_index)], capture_output=True, text=True,
                              encoding='utf-8')

    def check_running(self) -> bool:
        self.__refresh_info__()
        return self.info['is_android_started']

    def get_app_state(self, app_name) -> AppState:
        result = self.manager_run(['control', 'app', 'info', '-pkg', app_name])
        if result.returncode != 0:
            logging.error("Getting app state failed")
        else:
            return AppState(json.loads(result.stdout)['state'])

    @staticmethod
    def __execute_with_retries__(
            action: Callable[[], Any],
            condition: Callable[[], bool],
            max_retries: int,
            timeout: int,
            success_msg: str,
            failure_msg: str
    ) -> bool:
        retry_count = 0
        if condition():
            logging.info(success_msg)
            return True
        while retry_count < max_retries:
            action()
            start_time = time.time()
            while time.time() - start_time < timeout:
                if condition():
                    logging.info(success_msg)
                    return True
                time.sleep(0.1)
            retry_count += 1
        logging.error(failure_msg)
        return False

    def start(self, max_retries=3) -> bool:
        logging.info("Starting emulator...")
        return self.__execute_with_retries__(
            action=lambda: self.manager_run(['control', 'launch']),
            condition=self.check_running,
            max_retries=max_retries,
            timeout=10,
            success_msg="Manager started successfully.",
            failure_msg="Failed to start the manager after maximum retries."
        )

    def shutdown(self, max_retries=3) -> bool:
        logging.info("Shutting down emulator...")
        return self.__execute_with_retries__(
            action=lambda: self.manager_run(['control', 'shutdown']),
            condition=lambda: not self.check_running(),
            max_retries=max_retries,
            timeout=3,  # 停机可以更快地重试
            success_msg="Manager stopped successfully.",
            failure_msg="Failed to stop the manager after maximum retries."
        )

    def start_app(self, app_name: str, max_retries=3) -> bool:
        logging.info(f"Starting app {app_name}...")
        return self.__execute_with_retries__(
            action=lambda: self.manager_run(['control', 'app', 'launch', '-pkg', app_name]),
            condition=lambda: self.get_app_state(app_name) == AppState.RUNNING,
            max_retries=max_retries,
            timeout=10,
            success_msg=f"App {app_name} started successfully.",
            failure_msg=f"Failed to start app {app_name} after maximum retries."
        )

    def close_app(self, app_name: str, max_retries=3) -> bool:
        logging.info(f"Stopping app {app_name}...")
        return self.__execute_with_retries__(
            action=lambda: self.manager_run(['control', 'app', 'close', '-pkg', app_name]),
            condition=lambda: self.get_app_state(app_name) == AppState.STOPPED,
            max_retries=max_retries,
            timeout=3,
            success_msg=f"App {app_name} stopped successfully.",
            failure_msg=f"Failed to stop app {app_name} after maximum retries."
        )

    def adb_run(self, command: list[str]):
        return subprocess.run([self.adb, *command], capture_output=True, text=True, encoding='utf-8')

    def adb_connect(self) -> bool:
        self.__refresh_info__()
        ip = f"{self.info['adb_host_ip']}:{self.info['adb_port']}"
        return self.adb_run(['connect', ip]).returncode == 0


import yaml

if __name__ == '__main__':
    with open('../data/default_settings.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    logging.basicConfig(level=logging.INFO)

    emulator = Emulator(config['emulator'])

    emulator.start()

    emulator.start_app("edu.sjtu.infoplus.taskcenter")

    emulator.adb_connect()

    result = subprocess.run([emulator.adb, 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True)
    png_data = np.frombuffer(result.stdout, dtype=np.uint8)
    image = cv2.imdecode(png_data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to decode the screenshot image. Check adb output.")
    # 缩小图像
    scale_percent = 50  # 将图像缩小为原来的 50%
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)

    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    cv2.imshow("Screenshot", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
