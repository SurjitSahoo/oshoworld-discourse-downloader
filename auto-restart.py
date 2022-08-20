from subprocess import run
from time import sleep

script = "scrape.py"

restart_timer = 2

def start_script():
	try:
		run("python " + script, check=True)
	except:
		sleep(restart_timer)
		start_script()

start_script()