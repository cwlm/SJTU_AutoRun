import os

from sjtuautorun.mygo import RunPlan
from sjtuautorun.scripts.main import start_script

timer = start_script()
run_plan = RunPlan(timer)
run_plan.start_run()
