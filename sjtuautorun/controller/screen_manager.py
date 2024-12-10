import cv2
import numpy as np
import subprocess
import logging

from sjtuautorun.controller.emulator import Emulator


class ScreenManager:
    def __init__(self, emulator: Emulator):
        self.emulator = emulator
        self.screen = None
        self.resolution = None

    def get_resolution(self):
        result = self.emulator.adb_run(['shell', 'wm', 'size'])
        if result.returncode != 0:
            logging.error("Getting screen resolution failed")
            return False
        output = result.stdout.strip()
        if "Physical size" in output:
            resolution = output.split(":")[1].strip()
            x,y = list(map(int, resolution.split("x")))
            self.resolution = (y, x) # The resolution is in the format of "height x weight"
            return True
        else:
            raise ValueError("Failed to parse screen resolution.")

    def update_screen(self):
        try:
            result = subprocess.run(
                [self.emulator.adb, 'exec-out', 'screencap', '-p'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB command failed with return code {e.returncode}")
            logging.error(f"ADB stderr: {e.stderr.decode().strip()}")
            return
        except FileNotFoundError:
            logging.critical("ADB executable not found. Check your PATH or emulator configuration.")
            return
        except Exception as e:
            logging.critical(f"Unexpected error occurred: {str(e)}")
            return

        try:
            data = np.frombuffer(result.stdout, dtype=np.uint8)
            self.screen = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if self.screen is None:
                raise ValueError("Failed to decode screen image. The data might be corrupted.")
        except ValueError as e:
            logging.error(str(e))
            return
        except Exception as e:
            logging.critical(f"Unexpected error during image decoding: {str(e)}")
            return

        logging.info("Screen successfully updated.")

    def find_template_in_screen(self, template: np.ndarray, template_resolution: (int, int) = (1920, 1080), threshold: float = 0.99):
        self.update_screen()
        if self.resolution is None:
            self.get_resolution()
        screen_resized = cv2.resize(self.screen, None,
                                    fx=template_resolution[0] / self.resolution[0],
                                    fy=template_resolution[1] / self.resolution[1],
                                    interpolation=cv2.INTER_AREA)
        screen_gray = cv2.cvtColor(screen_resized, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCORR_NORMED )
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < threshold:
            return None
        start_x, start_y = max_loc
        centre_x, centre_y = (start_x + template.shape[1] // 2, start_y + template.shape[0] // 2)

        # Calculate the start and end points of the bounding box
        start_x, start_y = max_loc

        # end_x = start_x + template.shape[1]
        # end_y = start_y + template.shape[0]
        # # Draw the rectangle on the screen image
        # cv2.rectangle(screen_resized, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
        #
        # # Optionally show the image with the rectangle
        # cv2.imshow("Matched Screen", screen_resized)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return centre_x, centre_y


import yaml

if __name__ == '__main__':
    with open('../data/default_settings.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    logging.basicConfig(level=logging.INFO)

    emulator = Emulator(config['emulator'])

    emulator.start()

    emulator.start_app("edu.sjtu.infoplus.taskcenter")

    emulator.adb_connect()

    screen_manager = ScreenManager(emulator)

    screen_manager.get_resolution()

    print(screen_manager.find_template_in_screen(cv2.imread('../data/images/start_image/1.png')))
