import requests
from config import ya_token

token = ya_token

file_path = '/EBSH/photo.jpg'


upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'


headers = {
    'Authorization': f'OAuth {token}'
}

params = {
    'path': file_path,
    'overwrite': 'true'
}
response = requests.get(upload_url, headers=headers, params=params)

if response.status_code == 200:
    upload_link = response.json().get('href')
    print(f'Ссылка для загрузки: {upload_link}')

    local_file_path = 'photo.jpg'

    with open(local_file_path, 'rb') as file:
        upload_response = requests.put(upload_link, headers=headers, files={'file': file})

    if upload_response.status_code == 201:
        print('Файл успешно загружен на Яндекс.Диск!')
    else:
        print(f'Ошибка при загрузке файла: {upload_response.status_code}')
else:
    print(f'Ошибка при получении ссылки для загрузки: {response.status_code}')


