import argparse
import ssl
from os import getenv

class Config:
    def __init__(self,hostname=None,nodename=None,password=None,description=None,clientcert=None,clientkey=None,clientkeypassword=None,servercert=None):
        self.hostname = getenv("ISE_HOSTNAME",hostname)
        self.nodename = getenv("SERVICE_NODENAME",nodename)
        self.password = getenv("PXGRID_PASSWORD",password)
        self.description = getenv("PXGRID_DESCRIPTION",description)
        self.clientcert = getenv("PXGRID_CERT",clientcert)
        self.clientkey = getenv("PXGRID_KEY",clientkey)
        self.clientkeypassword = getenv("PXGRID_KEY_PASSWORD",clientkeypassword)
        self.servercert = getenv("ISE_CA_CHAIN",servercert)
    def get_host_name(self):
        return self.hostname

    def get_node_name(self):
        return self.nodename

    def get_password(self):
        if self.password is not None:
            return self.password
        else:
            return ''

    def get_description(self):
        return self.description

    def get_ssl_context(self):
        context = ssl.create_default_context()
        if self.clientcert is not None:
            context.load_cert_chain(certfile=self.clientcert,
                                    keyfile=self.clientkey,
                                    password=self.clientkeypassword)
        context.load_verify_locations(cafile=self.servercert)
        return context
