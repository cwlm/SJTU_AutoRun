import os

from sjtuautorun.mygo import RunPlan
from sjtuautorun.scripts.main import start_script

timer = start_script(f"{os.path.dirname(os.path.abspath(__file__))}/settings.yaml")
run_plan = RunPlan(timer)
run_plan.start_run()
