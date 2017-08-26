import webdav.client as wc

options = {
    'webdav_hostname': "https://webdav.yandex.ru",
    'webdav_login': 'tour_login',
    'webdav_password': 'your_pass'
}
client = wc.Client(options)


def yadisk_upload(podcast, remote_path):
    client = wc.Client(options)
    try:
        client.upload_sync(local_path=podcast, remote_path=remote_path)
    except wc.RemoteParentNotFound as e:
        if 'parent' in str(e):
            # We create  structure!
            path_dirs = remote_path.split('/')[:-1]
            levels = []
            for directory in path_dirs:
                levels.append(directory)
                try:
                    client.mkdir('/'.join(levels))
                except:
                    pass
            # Try upload again
            client.upload_sync(local_path=podcast, remote_path=remote_path)

