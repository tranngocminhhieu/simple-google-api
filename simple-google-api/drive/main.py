import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

drive_scopes = ["https://www.googleapis.com/auth/drive"]
drive_documents_scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']

def build_creds_from_service_account(scopes, google_sa_json):
    '''

    :param scopes: drive_scopes or drive_documents_scopes
    :param google_sa_json: Json (dict), not file
    :return: creds
    '''
    creds = service_account.Credentials.from_service_account_info(google_sa_json, scopes=scopes)
    return creds

def build_creds_from_client_secrets(scopes, client_secrets_file='client_secrets.json', save_token_file='token.json'):
    '''

    :param scopes: drive_scopes or drive_documents_scopes
    :param client_secrets_file: It should be .json
    :param save_token_file: It should be .json
    :return: creds
    '''
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(save_token_file):
        creds = Credentials.from_authorized_user_file(save_token_file, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(save_token_file, 'w') as token:
            token.write(creds.to_json())
    return creds

def build_gauth_from_service_account(google_sa_json):
    '''

    :param google_sa_json: Json (dict), not file
    :return: gauth
    '''
    gauth = GoogleAuth()
    scopes = ["https://www.googleapis.com/auth/drive"]
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_sa_json, scopes)
    return gauth

def build_gauth_from_client_secrets(client_secrets_file='client_secrets.json', save_creds_file='mycreds.txt'):
    '''

    :param client_secrets_file: It should be .json
    :param save_creds_file: It should be .txt
    :return: gauth
    '''
    # https://stackoverflow.com/questions/46978784/pydrive-google-drive-automate-authentication
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets_file
    # Try to load saved client credentials
    gauth.LoadCredentialsFile(save_creds_file)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(save_creds_file)
    return gauth

def create_folder(creds, new_folder_name, parent_folder_id=None):
    '''

    :param creds: Use build creds functions
    :param new_folder_name: string
    :param parent_folder_id: Without parent_folder_id new folder will be created in My Drive
    :return: folder_id
    '''

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        if parent_folder_id != None:
            file_metadata = {
                'name': new_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
        else:
            file_metadata = {
                'name': new_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder has created with ID: "{file.get("id")}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


def upload_file(gauth, local_file, folder_id=None, rename=None):
    '''

    :param gauth: Use build gauth functions
    :param local_file: Local file path
    :param folder_id: Without folder_id, file will be uploaded to My Drive.
    :param rename: Without rename, local_file will be used as file name.
    :return: No
    '''
    drive = GoogleDrive(gauth)

    title = rename if rename != None else os.path.split(local_file)[-1]
    parents = [{'id': folder_id}] if folder_id != None else None

    file = drive.CreateFile({'title': title, 'parents': parents})

    file.SetContentFile(local_file)
    file.Upload()
    print(f'Upload {local_file}{" as " + rename if rename != None else ""} to {"Drive folder " + folder_id if folder_id != None else "My Drive"} successfully!')

def check_usage(creds):
    '''

    :param creds: Use build creds functions
    :return: A usage information json
    '''
    service = build('drive', 'v3', credentials=creds)
    result = service.about().get(fields="*").execute()
    result = result.get("storageQuota", {})
    return result


def list_files(gauth, title_contains=None, owner_email=None):
    '''

    :param gauth: Use build gauth functions
    :param title_contains: string
    :param owner_email: Exactly email
    :return: A list of files, you can use Pandas to convert it to a data frame
    '''
    # https://stackoverflow.com/questions/56857760/list-of-files-in-a-google-drive-folder-with-python
    # https://stackoverflow.com/questions/61242051/google-drive-api-list-files-based-on-owners-in-shared-drive#comment108382909_61245232
    drive = GoogleDrive(gauth)

    filter_owner = f"'{owner_email}' in owners"
    filter_title = f"title contains '{title_contains}'"
    filters = []

    if title_contains != None:
        filters.append(filter_title)
    if owner_email != None:
        filters.append(filter_owner)

    param = {'q': ' and '.join(filters)} if len(filters) > 0 else None

    listed = drive.ListFile(param=param).GetList()
    return listed

def delete_file(creds, file_id):
    '''

    :param creds: Use build creds functions with drive scope
    :param file_id: ID in URL or use list_files function to get
    :return: No
    '''
    service = build('drive', 'v3', credentials=creds)
    service.files().delete(fileId=file_id).execute()
    print(f'{file_id} has been deleted!')

def move_file(creds, file_id, to_folder_id):
    service = build('drive', 'v3', credentials=creds)
    file = service.files().get(fileId=file_id, fields='id, name, parents').execute()
    remove_parents = file['parents'][0]
    moved = service.files().update(fileId = file_id,
                           addParents= to_folder_id,
                           removeParents = remove_parents,
                           fields = 'id, name, parents, owners',
                           ).execute()
    print(f'{file["name"]} has been moved to folder {to_folder_id}!')
    return moved

def copy_file(creds, file_id, same_name=True, prefix=None, suffix=None, to_folder_id=None):
    '''
    :param creds: Use build creds functions with drive scope
    :param file_id: ID in URL or use list_files function to get
    :param same_name: True = same old name, False = Copy of ...
    :param prefix: Add string at the begin of old name (space already), same_name have to = True
    :param suffix: Add string at the end of old name (space already), same_name have to = True
    :param to_folder_id: None = same folder, id string = copy to specific folder
    :return: New file information json
    '''
    service = build('drive', 'v3', credentials=creds)
    old_file = service.files().get(fileId=file_id, fields = 'id, name, parents, owners').execute()

    if same_name==True:
        new_name = f'{str(prefix) + " " if prefix != None else ""}{old_file["name"]}{" " + str(suffix) if suffix != None else ""}'
    else:
        new_name = f'Copy of {old_file["name"]}'

    body = {'name': new_name}

    copied = service.files().copy(fileId=file_id, body=body, fields = 'id, name, parents, owners').execute()

    if to_folder_id != None:
        copied = service.files().update(fileId=copied['id'],
                                       addParents=to_folder_id,
                                       removeParents=copied['parents'][0],
                                       fields='id, name, parents, owners',
                                       ).execute()

    print(f'{old_file["name"]} ({file_id}) has been copied to {body["name"]} ({copied["id"]}) {", folder " + to_folder_id if to_folder_id != None else ""}!')
    return copied


def rename_file(creds, file_id, new_name):
    '''

    :param creds: Use build creds functions with drive scope
    :param file_id: string
    :param new_name: string
    :return: New file information json
    '''
    service = build('drive', 'v3', credentials=creds)
    body = {'name': new_name}
    result = service.files().update(fileId=file_id, body=body, fields = 'id, name, parents, owners').execute()
    print(f'{file_id} has been renamed to {new_name}!')
    return result