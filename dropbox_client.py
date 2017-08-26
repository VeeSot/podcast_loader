import os

import dropbox
from dropbox.client import DropboxClient

token = 'your_token'
dbx = dropbox.Dropbox(token)
dbx_client = DropboxClient(token)


def dbx_upload(path_local, remote_path):
    podcast = open(path_local, 'rb')
    size = os.path.getsize(path_local)
    uploader = dbx_client.get_chunked_uploader(podcast, size)

    while uploader.offset < size:
        try:
            uploader.upload_chunked()
            uploader.finish(remote_path)
        except:
            break
