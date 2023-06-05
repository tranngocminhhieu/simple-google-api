from .main import SimpleDrive
from googleapiclient.discovery import build
import pandas as pd

def transfer_owner_by_copy(gauth_from, gauth_to, file_id, same_name=True):
    '''
    Copy the old file to a new file > Delete the old file
    :param creds_from: Use build creds functions
    :param creds_to: Use build creds functions
    :param file_id: ID in URL or use list_files function to get
    :return: New file information json
    '''
    drive_from = SimpleDrive(gauth_from)
    drive_to = SimpleDrive(gauth_to)
    result = drive_to.copy_file(file_id=file_id, same_name=same_name)
    result['deleted_file'] = file_id
    drive_from.delete_file(file_id=file_id)
    return result


# def add_permission(gauth, file_id, email, role='reader'):
#     '''
#     https://developers.google.com/drive/api/v3/reference/permissions/create
#     - owner
#     - organizer
#     - fileOrganizer
#     - writer
#     - commenter
#     - reader
#     '''
#     credentials = gauth.credentials
#     service = build('drive', 'v3', credentials=credentials)
#     permission = {'type': 'user', 'role': role, 'emailAddress': email}
#     try:
#         service.permissions().create(fileId=file_id, body=permission).execute()
#         print('Success!')
#         return True
#     except Exception as e:
#         print(f'Fail!\n{e}')
#         return False
#
# def delete_permission_by_email(gauth, file_id, email):
#     credentials = gauth.credentials
#     service = build('drive', 'v3', credentials=credentials)
#     list_permission = service.permissions().list(fileId=file_id, fields='*').execute()['permissions']
#     df_permission = pd.DataFrame(list_permission)
#     if email not in df_permission['emailAddress'].values.tolist():
#         print('This email is not in permission!')
#         return False
#     try:
#         permissionId = df_permission[df_permission['emailAddress']==email]['id'].values[0]
#         service.permissions().delete(fileId=file_id, permissionId=permissionId).execute()
#         print('Success!')
#         return True
#     except:
#         print('Fail!')
#         return False