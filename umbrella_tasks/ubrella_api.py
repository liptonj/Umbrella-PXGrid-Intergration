import logging
import requests
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from os import getenv


class UmbrellaAPI:
    def __init__(self, url=None, client_id=None, client_secret=None):
        self.url = getenv('UMBRELLA_TOKEN_URL',url)
        self.ident = getenv("UMBRELLA_CLIENT_ID",client_id)
        self.secret = getenv("UMBRELLA_CLIENT_SECERET",client_secret)
        self.token = None

    def GetToken(self):
        auth = HTTPBasicAuth(self.ident, self.secret)
        client = BackendApplicationClient(client_id=self.ident)
        oauth = OAuth2Session(client=client)
        self.token = oauth.fetch_token(token_url=self.url, auth=auth)
        return self.token

    def Query(self, end_point,params=None):
        success = False
        req = None
        if self.token == None:
            self.GetToken()
        while not success:
            try:
                api_headers = {'Authorization': "Bearer " + self.token['access_token']}
                req = requests.get('https://reports.api.umbrella.com/v2/{}'.format(end_point), headers=api_headers, params=params)
                req.raise_for_status()
                success = True
            except TokenExpiredError:
                self.token = self.GetToken()
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                self.token = self.GetToken()
        return req

# Exit out if the require client_id, client_secret and org_id are not set
"""
for var in ['API_SECRET', 'API_KEY', 'ORG_ID']:
    if os.environ.get(var) == None:
        print("Required environment variable: {} not set".format(var))
        exit()
"""
