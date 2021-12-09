#!/usr/bin/python3
import json
import logging
import asyncio
import signal

from datetime import datetime, timedelta, time
from ubrella_api import UmbrellaAPI
import time
import os
from os import getenv
from ise_api import apply_policy_ip,setup_sessions
"""
'categories':'109' << Potentially harmful
'categories':'67' << Malware
'categories':'150' << CRYPTOMINING
'
"""
if os.environ.get("UMBRELLA_ORG_ID") == None:
    print("Required environment variable: UMBRELLA_ORG_ID  not set")
    exit()
else:
    org_id = getenv("UMBRELLA_ORG_ID")

logging.basicConfig(format='%(asctime)s:[%(levelname)s]:%(message)s',level=logging.DEBUG)
logging.info("Starting App")

def get_dns_top(api,epoc_past,epoc_now):
    # Get token and make an API request
    params = {'from'   : epoc_past, 'to': epoc_now, 'limit': '100',
              'offset' : '0',
              'verdict': 'blocked', 'categories': getenv("UMBRELLA_CATEGORIES","109,67,150,403,24")}
    url = 'organizations/{}/activity/dns'.format(org_id)
    logging.debug(f"Request Params: {str(params)} Request URL: {url}")
    response = api.Query(url,params)
    logging.debug(response.json())
    return response.json()

def get_dns_categories(api):
    url = 'organizations/{}/categories'.format(org_id)
    response = api.Query(url)
    print(response.json())

async def umbrella_poll():
    api = UmbrellaAPI()
    api.GetToken()
    delay = int(getenv("POLL_TIMER"))
    now = datetime.now()
    past = now - timedelta(seconds=delay)
    epoc_past = int(time.mktime(past.timetuple())) * 1000
    while True:
        list_data = []
        now = datetime.now()
        epoc_now = int(time.mktime(now.timetuple())) * 1000
        report = get_dns_top(api,epoc_past, epoc_now)
        find = report
        l = 0
        # apply_policy_ip("192.168.8.122")
        print("Running Umbrella Pool")
        for i in report['data']:
            l += 1
            if i == report['data'][-1]:
                print(i['internalip'])
                print(i['time'])
                print(i['categories'][0]['label'])
                print(i['domain'])
                # print(i['identities'][1]['label'])
                list_data.append([i['internalip'], i['time'],
                                  i['categories'][0]['label'],
                                  i['domain']])
                apply_policy_ip(i['internalip'])
            elif i['internalip'] == report['data'][l]['internalip']:
                if i['domain'] == report['data'][l]['domain']:
                    pass
            else:
                print(i['internalip'])
                print(i['time'])
                print(i['categories'][0]['label'])
                print(i['domain'])
                # print(i['identities'][1]['label'])
                list_data.append([i['internalip'], i['time'],
                                  i['categories'][0]['label'],
                                  i['domain']])
                apply_policy_ip(i['internalip'])
        list_data.reverse()
        epoc_past = epoc_now
        await asyncio.sleep(delay)
        #time.sleep(delay)

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
    
