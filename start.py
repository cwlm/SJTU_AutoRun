import os

from sjtuautorun.scripts.main import start_script
start_script(f"{os.path.dirname(os.path.abspath(__file__))}/settings.yaml")
