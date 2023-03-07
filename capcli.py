# caption client

import requests


server_ip = '10.6.8.2'
server_port = 14500
endpoint = 'caption'


def get_caption(im):
    # send image to server
    files = {'image': im}
    response = requests.post(f'http://{server_ip}:{server_port}/{endpoint}', files=files)
    # get caption
    caption = response.json()['caption']
    return caption
