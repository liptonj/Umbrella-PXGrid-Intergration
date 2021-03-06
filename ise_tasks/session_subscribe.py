import asyncio
import json
import logging
from asyncio.tasks import FIRST_COMPLETED
from websockets import ConnectionClosed
from pxgrid.ws_stomp import WebSocketStomp

async def future_read_message(ws, future):
    try:
        message = await ws.stomp_read_message()
        future.set_result(message)
    except ConnectionClosed:
        logging.error('Websocket connection closed')

async def clear_policy(pxgrid_obj,mac_address):
    service = pxgrid_obj.get_service('com.cisco.ise.config.anc')
    node_name = service['nodeName']
    secret = pxgrid_obj.get_access_secret(node_name)['secret']
    url = service['properties']['restBaseUrl'] + '/clearEndpointByMacAddress'
    payload=json.dumps({"macAddress": mac_address})
    pxgrid_obj.query(secret,url,str.encode(payload))
    
async def subscribe_loop(config,pxgrid_obj, secret, ws_url, topic,pubsub_node_name):
    ws = WebSocketStomp(ws_url, config.get_node_name(), secret, config.get_ssl_context())
    await ws.connect()
    await ws.stomp_connect(pubsub_node_name)
    await ws.stomp_subscribe(topic)
    print("Ctrl-C to disconnect...")
    while True:
        future = asyncio.Future()
        future_read = future_read_message(ws, future)
        try:
            await asyncio.wait([future_read], return_when=FIRST_COMPLETED)
        except asyncio.CancelledError:
            await ws.stomp_disconnect('123')
            # wait for receipt
            await asyncio.sleep(3)
            await ws.disconnect()
            break
        else:
            messages = json.loads(future.result())
            if "sessions" in messages.keys():
                for message in messages["sessions"]:
                    if "ancPolicy" in message.keys() and "postureStatus" in message.keys():
                        #print(f"ANC Policy: {message['ancPolicy']}")
                        logging.info(f"{message['macAddress']} has ANC Policy {message['ancPolicy']} attached")
                        if message['ancPolicy'] == "NYIT_Quarantine" and message["postureStatus"] == "Compliant":
                            #print("message=" + json.dumps(message))
                            logging.info(f"Removing Device From Quarantine Username: {message['userName']} MAC Addres:{message['macAddress']} IP Address {str(message['ipAddresses'])} Device Propfile: {message['endpointProfile']}")
                            await clear_policy(pxgrid_obj,message["macAddress"])
        
