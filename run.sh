#!/bin/sh
# Running now

if [ `id -u` -ne 0 ]; then
    echo "Please re-run ${this_file} as root."
    exit 1
fi

# crontab
service cron restart
# token
# 修改token为你自己的token
echo "mytoken" > /var/www/rjudge/token.txt

# rsync

core=$(grep --count ^processor /proc/cpuinfo)
n=$(($core*2))

chmod 777 /judge_server/data/
# rsync 的密码,
echo "server:5978" >/etc/rsyncd.secrets
/etc/init.d/rsync start

redis-server &
celery worker -A config.celery &
# python3 server.py
gunicorn server:app --workers $n --worker-connections 1000 --error-logfile /var/log/gunicorn.log --timeout 3600 --graceful-timeout 3600 --worker-class gevent --bind 0.0.0.0:4999

