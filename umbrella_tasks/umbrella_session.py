import time
import asyncio
import logging
import os
from .ubrella_api import UmbrellaAPI
from os import getenv
from ise_tasks.ise_api import apply_policy_ip
from datetime import datetime, timedelta

if os.environ.get("UMBRELLA_ORG_ID") == None:
    print("Required environment variable: UMBRELLA_ORG_ID  not set")
    exit()
else:
    org_id = getenv("UMBRELLA_ORG_ID")
    
def get_dns_categories(api):
    url = 'organizations/{}/categories'.format(org_id)
    response = api.Query(url)
    logging.debug(response.json())


def get_security_activity(api,epoc_past,epoc_now):
    # Get token and make an API request
    params = {'from'   : epoc_past, 'to': epoc_now, 'limit': '100',
              'offset' : '0',
              'verdict': 'blocked', 'categories': getenv("UMBRELLA_CATEGORIES","109,67,150,403,24")}
    url = 'organizations/{}/activity/dns'.format(org_id)
    logging.debug(f"Request Params: {str(params)} Request URL: {url}")
    response = api.Query(url,params)
    logging.debug(response.json())
    return response.json()

async def umbrella_poll():
    api = UmbrellaAPI()
    api.GetToken()
    delay = int(getenv("POLL_TIMER"))
    now = datetime.now()
    past = now - timedelta(seconds=delay)
    epoc_past = int(time.mktime(past.timetuple())) * 1000
    while True:
        now = datetime.now()
        epoc_now = int(time.mktime(now.timetuple())) * 1000
        report = get_security_activity(api,epoc_past, epoc_now)
        l = 0
        print("Running Umbrella Report")
        for i in report['data']:
            l += 1
            if i == report['data'][-1]:
                #print(f"Internal IP: {i['internalip']} Time: {i['time']} Violation Category,{i['categories'][0]['label']} Domain: {i['domain']} \n")
                logging.info(f"Internal IP: {i['internalip']} Time: {i['time']} Violation Category,{i['categories'][0]['label']} Domain: {i['domain']}")
                apply_policy_ip(i['internalip'])
            elif i['internalip'] == report['data'][l]['internalip']:
                if i['domain'] == report['data'][l]['domain']:
                    pass
            else:
                #print(f"Internal IP: {i['internalip']} Time: {i['time']} Violation Category,{i['categories'][0]['label']} Domain: {i['domain']} \n")
                logging.info(f"Internal IP: {i['internalip']} Time: {i['time']} Violation Category,{i['categories'][0]['label']} Domain: {i['domain']}")
                apply_policy_ip(i['internalip'])
        epoc_past = epoc_now
        await asyncio.sleep(delay)
        #time.sleep(delay)