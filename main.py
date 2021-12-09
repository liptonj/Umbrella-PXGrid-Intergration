#!/usr/bin/python3
import logging
import asyncio
import signal
import os
from logformatter import setup_logging
from umbrella_tasks.umbrella_session import umbrella_poll
from os import getenv
from ise_tasks.ise_api import setup_sessions

"""
'categories':'109' << Potentially harmful
'categories':'67' << Malware
'categories':'150' << CRYPTOMINING
'
"""

setup_logging(console_log_output="stdout",
              console_log_level=getenv("CONSOLE_LOG_LEVEL","INFO"),
              console_log_color=True,
              logfile_file=getenv("LOG_FILE_LOCATION","logs/debug.log"),
              logfile_log_level=getenv("LOGFILE_LOG_LEVEL","INFO"),
              logfile_log_color=False,
              log_line_template="%(color_on)s%(asctime)s:[%(levelname)s]:%(message)s%(color_off)s")
logging.info("Starting App")


async def run_all_tasks():
	task_list = [setup_sessions(), umbrella_poll()]
	res = await  asyncio.gather(*task_list, return_exceptions=True)
	return res


if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	subscribe_task = asyncio.ensure_future(setup_sessions())
	
	# Setup signal handlers
	loop.add_signal_handler(signal.SIGINT, subscribe_task.cancel)
	loop.add_signal_handler(signal.SIGTERM, subscribe_task.cancel)
	
	# Event loop
	loop.run_until_complete(run_all_tasks())
