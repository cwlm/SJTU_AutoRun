import datetime
import os
import shutil
import winreg
from types import SimpleNamespace

import sjtuautorun
from sjtuautorun.controller.run_timer import Emulator, Timer
from sjtuautorun.utils.io import recursive_dict_update, yaml_to_dict, dict_to_yaml
from sjtuautorun.utils.new_logger import Logger

event_pressed = set()
script_end = 0


def initialize_logger_and_config(settings_path):
    config = yaml_to_dict(os.path.join(os.path.dirname(sjtuautorun.__file__), "data", "default_settings.yaml"))
    if settings_path is not None:
        user_settings = yaml_to_dict(settings_path)
        if user_settings["emulator"]["emulator_dir"] == "":
            print("No emulator directory provided, reading the registry")
            user_settings["emulator"]["emulator_dir"] = get_emulator_path()
            print("The emulator directory is " + user_settings["emulator"]["emulator_dir"])
        config = recursive_dict_update(config, user_settings)
    else:
        print("========Warning========")
        print(f"No user_settings file specified, default settings "
              f"{os.path.join(os.path.dirname(sjtuautorun.__file__), 'data', 'default_settings.yaml')}"
              f" will be used.")
        print("=========End===========")
        if config["emulator"]["emulator_dir"] == "":
            config["emulator"]["emulator_dir"] = get_emulator_path()

    # set logger
    mian_log_dir = os.path.join(os.path.dirname(sjtuautorun.__file__), config["LOG_PATH"])
    current_datetime = datetime.datetime.now()
    config["log_dir"] = os.path.join(mian_log_dir, current_datetime.strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(config["log_dir"], exist_ok=True)

    # delete old log (if found)
    one_month_ago = current_datetime - datetime.timedelta(days=30)

    try:
        # 遍历日志目录中的文件夹
        for folder_name in os.listdir(mian_log_dir):
            folder_path = os.path.join(mian_log_dir, folder_name)

            # 检查是否是一个月前的文件夹
            if os.path.isdir(folder_path):
                folder_date = datetime.datetime.strptime(folder_name, "%Y-%m-%d_%H-%M-%S")
                if folder_date < one_month_ago:
                    shutil.rmtree(folder_path)
                    print(f"Deleted old log folder: {folder_name}")
    except Exception as e:
        print(f"Error while deleting old log folders: {e}")

    logger = Logger(config)
    config = SimpleNamespace(**config)
    config_str = logger.save_config(config)
    logger.reset_level()
    return config, logger


def start_script(settings_path=None):
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


def get_emulator_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\leidian\ldplayer9")
        try:
            path, _ = winreg.QueryValueEx(key, "InstallDir")
            return os.path.join(path, "dnplayer.exe")
        except FileNotFoundError:
            print("Path not found")
        finally:
            winreg.CloseKey(key)

    except FileNotFoundError:
        print("Emulator not found")
        return None
