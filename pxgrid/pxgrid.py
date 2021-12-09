import base64
import json
import urllib.request
import logging

class PxgridControl:
    def __init__(self, config):
        self.config = config

    def send_rest_request(self, url_suffix, payload):
        url = 'https://' + \
            self.config.get_host_name() + \
            ':8910/pxgrid/control/' + url_suffix
        logging.debug("pxgrid url=" + url)
        json_string = json.dumps(payload)
        logging.debug('  request=' + json_string)
        handler = urllib.request.HTTPSHandler(
            context=self.config.get_ssl_context())
        opener = urllib.request.build_opener(handler)
        rest_request = urllib.request.Request(
            url=url, data=str.encode(json_string))
        rest_request.add_header('Content-Type', 'application/json')
        rest_request.add_header('Accept', 'application/json')
        b64 = base64.b64encode((self.config.get_node_name(
        ) + ':' + self.config.get_password()).encode()).decode()
        rest_request.add_header('Authorization', 'Basic ' + b64)
        rest_response = opener.open(rest_request)
        response = rest_response.read().decode()
        logging.info('PXGrid Send Rest Request Response:' + response)
        return json.loads(response)

    def account_activate(self):
        payload = {}
        if self.config.get_description() is not None:
            payload['description'] = self.config.get_description()
        return self.send_rest_request('AccountActivate', payload)

    def service_lookup(self, service_name):
        payload = {'name': service_name}
        return self.send_rest_request('ServiceLookup', payload)

    def service_register(self, service_name, properties):
        payload = {'name': service_name, 'properties': properties}
        return self.send_rest_request('ServiceRegister', payload)

    def get_access_secret(self, peer_node_name):
        payload = {'peerNodeName': peer_node_name}
        return self.send_rest_request('AccessSecret', payload)

    def get_service(self,service_name):
        service_lookup_response = self.service_lookup(service_name)
        return service_lookup_response['services'][0]
    
    def query(self, secret, url, payload):
        logging.debug('query url=' + url)
        logging.debug('request=' + str(payload))
        handler = urllib.request.HTTPSHandler(
            context=self.config.get_ssl_context())
        opener = urllib.request.build_opener(handler)
        rest_request = urllib.request.Request(url=url,
                                              data=payload)
        rest_request.add_header('Content-Type', 'application/json')
        rest_request.add_header('Accept', 'application/json')
        b64 = base64.b64encode(
            (self.config.get_node_name() + ':' + secret).encode()).decode()
        rest_request.add_header('Authorization', 'Basic ' + b64)
        rest_response = opener.open(rest_request)
        logging.info('PXGrid query response code: ' + str(rest_response.getcode()))
        logging.info('PXGrid query response: ' + rest_response.read().decode())
