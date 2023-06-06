# Simple Google API
Python package simple Google API for non-technical users

## How to install
### Install with Pip

Install new package.

```
pip install simplegoogleapi
```

Upgrade to the latest version.

```
pip install simplegoogleapi --upgrade
```

### Install with GitHub

Install new package.

```
pip install git+https://github.com/tranngocminhhieu/simplegoogleapi.git
```

Upgrade to the latest version.

```
pip install git+https://github.com/tranngocminhhieu/simplegoogleapi --upgrade
```

## How to use SimpleDrive

### Import packages

```python
from simplegoogleapi.drive import SimpleDrive
from simplegoogleapi.auth import BuildAuth
```
### Build auth
Build auth with a service account
```python
gauth = BuildAuth(service_account='service_account.json').build_gauth_from_service_account()
```
Build auth with client secrets and credentials
```python
gauth = BuildAuth(client_secrets_file='client_secrets.json', credentials_file='credentials.json').build_gauth_from_client_secrets()
```
Build auth automation anyway
```python
gauth = BuildAuth().build_gauth_auto_anyway(client_secrets_file='client_secrets.json', credentials_file='credentials.json', credentials_raw='https://rentry.co/example/raw', service_account_json='service_account.json')
```

### Use functions
```python
my_drive = SimpleDrive(gauth=gauth)
```
Upload a file
```python
my_drive.upload_file(local_file='your-file-path', folder_id=None, rename=None)
```
Create a folder
```python
my_drive.create_folder(new_folder_name='New folder', parent_folder_id=None)
```
Check usage limit
```python
my_drive.check_usage()
```
List files
```python
files = my_drive.list_files(title_contains=None, owner_email=None)
```
Delete a file
```python
my_drive.delete_file(file_id='your-file-id')
```
Move a file
```python
my_drive.move_file(file_id='your-file-id', to_folder_id='your-folder-id')
```
Copy a file
```python
my_drive.copy_file(file_id='your-file-id', same_name=True, prefix=None, suffix=None, to_folder_id=None)
```
Rename a file
```python
my_drive.rename_file(file_id='your-file-id', new_name='A new name')
```
Add a permission
```python
my_drive.add_permission(file_id='your-file-id', email='example@mail.com', role='reader')
```
Delete a permission
```python
# With a permission ID
my_drive.delete_permission(file_id='your-file-id', permission_id='a-permission-id', email=None)
# With an email
my_drive.delete_permission(file_id='your-file-id', permission_id=None, email='example@mail.com')
```
### Transfer ownership

#### Transfer ownership with different organization
Method: Copy the old file to a new file > Delete the old file
```python
from simplegoogleapi.drive.help import transfer_owner_by_copy
```
```python
gauth_from = BuildAuth(service_account='service_account.json').build_gauth_from_service_account()
gauth_to = BuildAuth(client_secrets_file='client_secrets.json', credentials_file='credentials.json').build_gauth_from_client_secrets()
```
```python
transfer_owner_by_copy(gauth_from, gauth_to, file_id='your-file-id', same_name=True)
```