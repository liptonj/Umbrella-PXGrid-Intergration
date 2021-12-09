import sys
import json
from ise import ERS
sys.path.append('pxgrid-rest-ws/python')
import time
import asyncio
import signal
from pxgrid import PxgridControl,Config,subscribe_loop
from os import getenv,environ

for var in ['ISE_HOSTNAME', 'ISE_ERS_USERNAME', 'ISE_ERS_PASSWORD','ISE_POLICY']:
    if environ.get(var) == None:
        print("Required ISE ERS environment variablse: {} not set".format(var))
        exit()
        
config = Config()
pxgrid_obj = PxgridControl(config=config)

while pxgrid_obj.account_activate()['accountState'] != 'ENABLED':
    time.sleep(60)


ise_obj = ERS(ise_node=getenv("ISE_HOSTNAME"),ers_user=getenv("ISE_ERS_USERNAME"),ers_pass=getenv("ISE_ERS_PASSWORD"),
              verify=False,disable_warnings=True)
async def setup_sessions():
# lookup for pubsub service
    service_lookup_response = pxgrid_obj.service_lookup('com.cisco.ise.session')
    service = service_lookup_response['services'][0]
    pubsub_service_name = service['properties']['wsPubsubService']
    topic = service['properties']['sessionTopic']


    # lookup for pubsub service
    service_lookup_response = pxgrid_obj.service_lookup(pubsub_service_name)
    pubsub_service = service_lookup_response['services'][0]
    pubsub_node_name = pubsub_service['nodeName']
    secret = pxgrid_obj.get_access_secret(pubsub_node_name)['secret']
    ws_url = pubsub_service['properties']['wsUrl']

    await subscribe_loop(config, secret, ws_url, topic,pubsub_node_name)



#function for populate a list of endpoint in the database
def endpoint_list():
    endpoints = ise_obj.get_endpoints()
    print(ise_obj.get_endpoints['response'])

#function for polling the endpoint details and print out the group name '00:D6:FE:EC:12:A9'

def endpoint_details(mac):
    device = ise_obj.get_endpoint(mac_address= mac)['response']
    print(json.dumps(device, indent = 4))
    groupid = device['groupId']
    for i in ise_obj.get_endpoint_groups()['response']:
        groupname = i[0]
        if i[1] == groupid:
            print ("{0:22s} {1:36s}".format('Endpoint Group:', groupname))
        else:
            pass

def get_session_px(pxgrid_obj,ip_address):
    service_lookup_response = pxgrid_obj.service_lookup('com.cisco.ise.session')
    service = service_lookup_response['services'][0]
    node_name = service['nodeName']
    secret = pxgrid_obj.get_access_secret(node_name)['secret']
    url = service['properties']['restBaseUrl'] + '/getSessionByIpAddress'
    payload ={}
    payload.update({"ipAddress": ip_address})
    payload = str.encode(json.dumps(payload))
    pxgrid_obj.query(secret, url, payload)

def apply_policy_ip(ip_address):
    service = pxgrid_obj.get_service('com.cisco.ise.config.anc')
    node_name = service['nodeName']
    secret = pxgrid_obj.get_access_secret(node_name)['secret']
    url = service['properties']['restBaseUrl'] + '/applyEndpointByIpAddress'
    payload=json.dumps({"policyName":getenv("ISE_POLICY"), "ipAddress": ip_address})

    pxgrid_obj.query(secret,url,str.encode(payload))
    
if __name__ == "__main__":
 # lookup for session service
 service_lookup_response = pxgrid_obj.service_lookup('com.cisco.ise.config.anc')
 service = service_lookup_response['services'][0]
 node_name = service['nodeName']
 secret = pxgrid_obj.get_access_secret(node_name)['secret']
 get_session_px(pxgrid_obj,"192.168.8.122")
 apply_policy_ip(pxgrid_obj,"192.168.8.122")