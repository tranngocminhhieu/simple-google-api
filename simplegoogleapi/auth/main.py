import json
import os
import os.path

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth


class BuildAuth:
    def __init__(self, client_secrets_file=None, credentials_file=None, service_account_json=None):
        '''

        :param client_secrets_file: client_secrets.json string
        :param credentials_file: credentials.json string
        :param service_account_json: service_account.json string or a dict
        '''
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.service_account_json = service_account_json

        self.drive_scopes = ["https://www.googleapis.com/auth/drive"]
        self.drive_documents_scopes = ['https://www.googleapis.com/auth/drive',
                                       'https://www.googleapis.com/auth/documents']

    def load_service_account(self, service_account_json):
        if type(service_account_json) == dict:
            pass
        elif type(service_account_json) == str:
            with open(service_account_json, 'r') as f:
                service_account_json = json.load(f)
        else:
            raise Exception('Please input a file path string or a dict')
        return service_account_json

    def build_creds_from_service_account(self, scopes=None, service_account_json=None):
        '''

        :param scopes: drive_scopes or drive_documents_scopes
        :param service_account_json: file string or dict variable are acceptable
        :return: creds
        '''

        if scopes == None:
            scopes = self.drive_scopes
        if service_account_json == None:
            service_account_json = self.service_account_json

        service_account_json = self.load_service_account(service_account_json)

        creds = service_account.Credentials.from_service_account_info(service_account_json, scopes=scopes)
        return creds

    def build_creds_from_client_secrets(self, scopes=None, client_secrets_file=None,
                                        credentials_file=None):
        '''

        :param scopes: drive_scopes or drive_documents_scopes
        :param client_secrets_file: It should be .json
        :param credentials_file: It should be .json
        :return: creds
        '''

        if scopes == None:
            scopes = self.drive_scopes
        if client_secrets_file == None:
            client_secrets_file = self.client_secrets_file
        if credentials_file == None:
            credentials_file = self.credentials_file

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(credentials_file):
            creds = Credentials.from_authorized_user_file(credentials_file, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(credentials_file, 'w') as token:
                token.write(creds.to_json())
        return creds

    def build_gauth_from_service_account(self, service_account_json=None):
        '''

        :param service_account_json: file string or dict variable are acceptable
        :return: gauth
        '''
        if service_account_json == None:
            service_account_json = self.service_account_json

        service_account_json = self.load_service_account(service_account_json)

        gauth = GoogleAuth()
        scopes = self.drive_scopes
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_json, scopes)
        return gauth

    def build_gauth_from_client_secrets_manually(self, client_secrets_file=None, credentials_file=None):
        '''
        This method should be run on a desktop because it has manual steps (100%)
        :param client_secrets_file:
        :param credentials_file:
        :return:
        '''
        if client_secrets_file == None:
            client_secrets_file = self.client_secrets_file
        if credentials_file == None:
            credentials_file = self.credentials_file

        gauth = GoogleAuth()
        gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_file
        gauth.GetFlow()
        # This is what solved the issues: https://stackoverflow.com/a/55876179
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(credentials_file)

        return gauth

    def build_gauth_from_client_secrets(self, client_secrets_file=None, credentials_file=None):
        '''
        This method should be run on a desktop because it has manual steps (50% auto, 50% manual)
        :param client_secrets_file: It should be .json
        :param credentials_file: It should be .json
        :return: gauth
        '''

        if client_secrets_file == None:
            client_secrets_file = self.client_secrets_file
        if credentials_file == None:
            credentials_file = self.credentials_file

        # https://stackoverflow.com/questions/46978784/pydrive-google-drive-automate-authentication
        gauth = GoogleAuth()

        gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_file

        # Try to load saved credentials
        gauth.LoadCredentialsFile(credentials_file)

        # If the file does not exist -> Start new authentication
        if gauth.credentials is None:
            gauth = self.build_gauth_from_client_secrets_manually(client_secrets_file=client_secrets_file, credentials_file=credentials_file)

        # If the file exist but token has expired -> Try to refresh. If it can not be refreshed -> Start new authentication
        elif gauth.access_token_expired:
            try:
                # Refresh them if expired
                gauth.Refresh()
            except:
                gauth = self.build_gauth_from_client_secrets_manually(client_secrets_file=client_secrets_file, credentials_file=credentials_file)

        # If the file exists and has not expired -> Authorize the credentials by the file
        else:
            # Initialize the saved creds
            gauth.Authorize()

        # Save the current credentials to a file
        gauth.SaveCredentialsFile(credentials_file)
        return gauth

    def get_auth_from_raw(self, client_secrets_raw=None, credentials_raw=None, service_account_raw=None,
                          save_client_secrets_file='client_secrets.json', save_credentials_file='credentials.json',
                          save_service_account_file='service_account.json'):
        '''

        :param client_secrets_raw: link string
        :param credentials_raw: link string
        :param service_account_raw: link string
        :param save_client_secrets_file: file string
        :param save_credentials_file: file string
        :param save_service_account_file: file string
        :return:
        '''
        if client_secrets_raw != None:
            client_secrets = requests.get(client_secrets_raw).text
            with open(save_client_secrets_file, 'w') as f:
                f.write(client_secrets)
            print('Client secrets has been saved')
        if credentials_raw != None:
            credentials = requests.get(credentials_raw).text
            with open(save_credentials_file, 'w') as f:
                f.write(credentials)
            print('Credentials has been saved')
        if service_account_raw != None:
            sa = requests.get(service_account_raw).text
            with open(save_service_account_file, 'w') as f:
                f.write(sa)
            print('Service account has been saved')

    def build_gauth_auto_anyway(self, client_secrets_file=None, credentials_file=None,
                                credentials_raw=None, service_account_json=None):
        '''
        This method can run on a Server or Desktop, auto 100% but all parameters should be provided.

        Use credentials file -> use credentials raw link -> use service account.
        :param client_secrets_file: string
        :param credentials_file: string
        :param credentials_raw: string
        :param service_account_json: string or dict
        :return: gauth
        '''

        if client_secrets_file == None:
            client_secrets_file = self.client_secrets_file
        if credentials_file == None:
            credentials_file = self.credentials_file
        if service_account_json == None:
            service_account_json = self.service_account_json
            if service_account_json != None:
                service_account_json = self.load_service_account(service_account_json)

        gauth = GoogleAuth()
        gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_file

        # Try to load saved credentials
        gauth.LoadCredentialsFile(credentials_file)

        if gauth.credentials is None:
            print('No credentials file')
            if credentials_raw != None:
                print('Get credential from raw link')
                self.get_auth_from_raw(credentials_raw=credentials_raw)
                gauth.LoadCredentialsFile(credentials_file)
                if gauth.access_token_expired:
                    print('Get credential from raw link has expired, try to refresh')
                    try:
                        # Refresh them if expired
                        gauth.Refresh()
                        gauth.Authorize()
                        gauth.SaveCredentialsFile(credentials_file)
                        print('Refresh success')
                        return gauth
                    except:
                        print('Can not refresh, build gauth from Service Account')
                        gauth = self.build_gauth_from_service_account(service_account_json)
                        return gauth
                else:
                    print('Credentials from raw link is good')
                    gauth.Authorize()
                    gauth.LoadCredentialsFile(credentials_file)
                    return gauth

            elif service_account_json != None:
                print('No credentials raw link, build gauth from Service Account')
                gauth = self.build_gauth_from_service_account(service_account_json)
                return gauth

            else:
                print('Build gauth fail: No file, No link, No service account')

        elif gauth.access_token_expired:
            print('Get credential has expired, try to refresh')
            try:
                # Refresh them if expired
                gauth.Refresh()
                gauth.Authorize()
                gauth.SaveCredentialsFile(credentials_file)
                print('Refresh success')
                return gauth
            except:
                print('Can not refresh')
                if credentials_raw != None:
                    print('Get credentials from raw link')
                    self.get_auth_from_raw(credentials_raw=credentials_raw)
                    gauth.LoadCredentialsFile(credentials_file)
                    if gauth.access_token_expired:
                        print('Credentials from raw link also expired, try to refresh')
                        try:
                            # Refresh them if expired
                            gauth.Refresh()
                            gauth.Authorize()
                            gauth.SaveCredentialsFile(credentials_file)
                            print('Refresh success')
                            return gauth
                        except:
                            print('Can not refresh, build gauth from Service Account')
                            gauth = self.build_gauth_from_service_account(service_account_json)
                            return gauth

                elif service_account_json != None:
                    print('No credentials raw link, build gauth from Service Account')
                    gauth = self.build_gauth_from_service_account(service_account_json)
                    return gauth
        else:
            print('Credentials file is good')
            gauth.Authorize()
            gauth.LoadCredentialsFile(credentials_file)
            return gauth
