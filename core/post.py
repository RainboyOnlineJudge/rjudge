import requests
from config import *

@celery.task
def post_data(data,r_url,revert):
    if r_url[:7] != 'http://':
        r_url = 'http://'+r_url

    __data = {}

    if(isinstance(data,list)):
        __data = {
                "result":data,
                "verdict":0,
                "revert":revert
            }
    else:
        __data = {
                "result":data["message"],
                "verdict":data["verdict"],
                "revert":revert
            }
    requests.post(r_url,json=__data)
    return

