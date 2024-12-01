import os
import cv2
import numpy as np
import subprocess
import json
import time
import logging


class Emulator:
    def __init__(self, config):
        self.emulator_dir = config['emulator_dir']
        self.emulator_index = config['emulator_index']
        self.manager = os.path.join(self.emulator_dir, 'shell', 'mumuManager.exe')
        self.adb = os.path.join(self.emulator_dir, 'shell', 'adb')

        self.__refresh_info__()

    def __refresh_info__(self):
        self.info = json.loads(self.manager_run(['info']).stdout)

    def manager_run(self, command: list[str]):
        return subprocess.run([self.manager, *command, '-v', str(self.emulator_index)], capture_output=True, text=True,
                              encoding='utf-8')

    def check_running(self) -> bool:
        self.__refresh_info__()
        return self.info['is_process_started']

    def start(self, max_retries=3) -> bool:
        retry_count = 0
        if self.check_running():
            logging.info("Manager started successfully.")
            return True
        while retry_count <= max_retries:
            logging.info("Starting the manager...")
            self.manager_run(['control', 'launch'])
            time.sleep(10)
            if self.check_running():
                logging.info("Manager started successfully.")
                return True
            retry_count += 1
        logging.error("Failed to start the manager after maximum retries.")
        return False

    def shutdown(self) -> bool:
        if not self.check_running():
            logging.info("Manager stopped successfully.")
            return True
        self.manager_run(['control', 'shutdown'])
        time.sleep(3)
        if not self.check_running():
            logging.info("Manager stopped successfully.")
            return True
        return False


import yaml

if __name__ == '__main__':
    with open('../data/default_settings.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    logging.basicConfig(level=logging.INFO)

    emulator = Emulator(config['emulator'])

    emulator.start()
