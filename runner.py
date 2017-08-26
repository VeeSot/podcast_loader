import json
import os
import re
from datetime import datetime, timedelta
from os.path import basename

import feedparser
import requests

from dropbox_client import dbx_upload
from yadisk_client import yadisk_upload

current_dir = os.path.dirname(os.path.realpath(__file__))

#Регулярка для вычленения имени файла,
#которое будет использоваться для последующего сохраения
regex = r"([\w\d\s\S]+.mp3)"
#Место сохранения, будет постоянно перезаписываться
path_local = '/tmp/podcast.mp3'
#User-Agent нужен потому что некоторые сервисы блокируют UA urlib и python-request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}


def upload_new_pod_casts(url, directory):
    f = feedparser.parse(url)
    #В любой RSS ленте есть вложеный элемент, который предоставляет доступ к записям
    entries = f['entries']
    #Забираем только те которые самые новые
    expected_publish_date = datetime.now() - timedelta(days=1)
    start_time = expected_publish_date.timetuple()
    records = filter(lambda entry:
                     entry.get('published_parsed', start_time) > start_time, entries)

    for record in records:
        for link in record['links']:
            type_link = link.get('type', '')
            #Забираем только аудиозаписи игнорируя видео и текст.
            if 'audio' in type_link:
                try:
                    #Выделяем название файла для лучше читаемости.
                    #Зачастую аудиофайлы бывают без тегов,
                    #так что имя файла - единственное на что мы може расчитывать
                    location = link.get('href')
                    matches = re.findall(regex, basename(location))
                    file_name = matches[-1]
                    #Пробуем загрузить файл по ссылке которую выдрали из RSS
                    pod_cast_file = requests.get(location, headers=headers, stream=True)
                    #Сохраняем в файл-времянку, перезаписывается на каждой итерации
                    with open(path_local, 'wb') as f:
                        for chunk in pod_cast_file:
                            f.write(chunk)
                        f.close()

                    path_for_disk = 'podcasts/{1}/{0}/{2}'.format(
                        directory, datetime.now().strftime("%d-%m-%y"), file_name)

                    yadisk_upload(path_local, path_for_disk)
                    #or you can use dropbox
                    #dbx_upload(path_local, path_for_disk)
                except:
                    pass


#Обрабатываем файл с конифгурацией
with open('{}/podcasts.json'.format(current_dir)) as data_file:
    podcasts = json.load(data_file)

for podcast in podcasts:
    directory = podcast['dir']
    for url in podcast['urls']:
        upload_new_pod_casts(url, directory)
