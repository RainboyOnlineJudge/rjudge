from config import *
from .utils import mq_emit


# 发送
@celery.task
def post_data(data,sid,revert):
    if not isinstance(data,list):
        data = [data]
    mq_emit(sid,{
        "status":0,
        "mid":END_JUDGE,
        "result":sorted(data,key= lambda x:x["count"]),
        # "result":data,
        "revert":revert
        })
    return

