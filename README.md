# rJudge

## 快速安装

暂缺

## 设定

```
vim run.sh
```

## 安装:

基本如下:

 1.clone这个代码,安装docker,可以使用`aliyun`的docker[加速器](https://cr.console.aliyun.com/?spm=5176.100239.blogcont29941.12.fOsBW8)
 2. 修改rsync,token的相关参数,建立data文件夹
 3. 输入命令:`docker build -t rjudge .`,创建images
 4. `sudo docker run -it -v {你的data地址}:/judge_server/data -p 4999:4999 -p 873:873 -d rjudge`

## 特性

 - 使用rsync来同步测试数据
 - 使用token
 - 定时删除不用的测试文件
 - 使用qdoj的测评机为后台


# 安装方法

## 1.修改Token:

在run.sh里修改token
```
#修改token为你自己的token
echo "mytoken" > /var/www/rjudge/token.txt
```

## 2.修改rsync的密码

在`run.sh`里

## 上传数据:

使用`rsync`来上传数据

```
# rsync 的密码,
echo "server:5978" >/etc/rsyncd.secrets
```

### 同步数据的方法1:使用rsync

```
sudo echo 5978 > /etc/rsyncd.secret
sudo chmod 600 /etc/rsyncd.secret
sudo chown root:root /etc/rsyncd.secret
sudo rsync --port 8080 --password-file=/etc/rsyncd.secret -av /databack/ server@<ip>::data
```

### 同步数据的方法:使用lsync

使用lsync可以自动同步

ubuntu 下安装lsyncd

```
sudo apt-get install lsyncd
```

/etc/lsyncd.conf
```
settings {
    logfile      ="/var/log/lsyncd.log",
    statusFile   ="/tmp/lsyncd.status",
    inotifyMode  = "CloseWrite",
    maxProcesses = 10,
    statusInterval = 1
}

sync {
    default.rsync,
    source    = "/home/server1/test/data/",
    target    = "server@localhost::data",
    delay     = 15,
    rsync     = {
        binary    = "/usr/bin/rsync",
        archive   = true,
        compress  = true,
        verbose   = true,
        password_file = "/home/server1/test/rsyncd.secret"
    }
}
```

启动:`sudo lsyncd  /etc/lsyncd.conf`

根据你的实际情况修改参数

参数的含义请看:https://axkibe.github.io/lsyncd/manual/config/layer4/

## 请求测试的方法


先同步评测数据,然后使用http的post方法请求评测

**注意:**所有的请求头都要带有一个`token`头,

```node
headers = {
  token:"your_token"
}
requests.post(url, json=data, headers).json()
```

请求地址:`http://your_judge_server_ip/judge`

请求的json数据
```json
{
  "lang": "cpp",//c cpp pas
  "code": "int main() { return 0; }",
  "max_time": 1000,
  "max_memory": 256,//mb
  "problem_id": "1000",
  "r_url":",",//要返回数据的地址
  "judge": "fcmp",
  "revert":{//返回数据的时候把这个部分同样返回
  }
}
```

### 返回数据

If something is wrong (data is missing or some part of request is missing), server will return:
```json
{
  "status": "reject"
}
```
Otherwise, `status` will be `received`.

Then, submission will be under processing. If `COMPILE_ERROR` occurred:
```json
{
  "id": 302,
  "message": "... In function 'int main()':\n/ju...",
  "verdict": 6,
  "status": "received"
}
```

Otherwise,
```json
{
  "id": 304, 
  "memory": 3052, 
  "status": "received", 
  "time": 588, 
  "verdict": 0,
  "detail": [{"count": 1, "memory": 2944, "time": 16, "verdict": 0}, {"count": 2, "memory": 2944, "time": 16, "verdict": 0}]
}
```

"verdict"数据的含义如下:
```python
WRONG_ANSWER = -1
ACCEPTED = 0
CPU_TIME_LIMIT_EXCEEDED = 1
REAL_TIME_LIMIT_EXCEEDED = 2
MEMORY_LIMIT_EXCEEDED = 3
RUNTIME_ERROR = 4
SYSTEM_ERROR = 5
COMPILE_ERROR = 6
IDLENESS_LIMIT_EXCEEDED = 7
SUM_TIME_LIMIT_EXCEEDED = 8
```

Okay, that pretty much nails it! Good luck!

## 有关rsync自动同步

docker中使用了rsync-server,另一端使用lsyncd来**监视本地文件,自动发送到远程rsync-server的相应文件夹下**
