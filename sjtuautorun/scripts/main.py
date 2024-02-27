import datetime
import os
from types import SimpleNamespace

import sjtuautorun
from sjtuautorun.controller.run_timer import Emulator, Timer
from sjtuautorun.utils.io import recursive_dict_update, yaml_to_dict
from sjtuautorun.utils.new_logger import Logger

event_pressed = set()
script_end = 0


def initialize_logger_and_config(settings_path):
    config = yaml_to_dict(os.path.join(os.path.dirname(sjtuautorun.__file__), "data", "default_settings.yaml"))
    if settings_path is not None:
        user_settings = yaml_to_dict(settings_path)
        config = recursive_dict_update(config, user_settings)
    else:
        print("========Warning========")
        print(f"No user_settings file specified, default settings "
              f"{os.path.join(os.path.dirname(sjtuautorun.__file__), 'data', 'default_settings.yaml')}"
              f" will be used.")
        print("=========End===========")

    # set logger
    config["log_dir"] = os.path.join(config["LOG_PATH"], datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(config["log_dir"], exist_ok=True)
    logger = Logger(config)
    config = SimpleNamespace(**config)
    config_str = logger.save_config(config)
    logger.reset_level()
    return config, logger


def start_script(settings_path):
    """启动脚本, 返回一个 Timer 记录器.
    :如果模拟器没有运行, 会尝试启动模拟器,
    :如果游戏没有运行, 会自动启动交我办,
    :如果交我办在后台, 会转到前台
    Returns:
        Timer: 该模拟器的记录器
    """
    config, logger = initialize_logger_and_config(settings_path)
    timer = Timer(config, logger)
    return timer


def start_script_emulator(settings_path):
    """启动脚本, 返回一个 Emulator 记录器, 用于操作模拟器
    Returns:
        Emulator: 该模拟器的记录器
    """
    config, logger = initialize_logger_and_config(settings_path)
    emulator = Emulator(config, logger)
    return emulator
