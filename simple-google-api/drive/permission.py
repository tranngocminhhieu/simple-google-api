from .main import copy_file, delete_file

def transfer_owner_by_copy(creds_from, creds_to, file_id):
    '''
    Copy the old file to a new file > Delete the old file
    :param creds_from: Use build creds functions
    :param creds_to: Use build creds functions
    :param file_id: ID in URL or use list_files function to get
    :return: New file information json
    '''
    result = copy_file(creds=creds_to, file_id=file_id)
    result['deleted_file'] = file_id
    delete_file(creds=creds_from, file_id=file_id)
    return result