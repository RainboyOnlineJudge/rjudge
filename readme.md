# rJudge

## 安装

### 手动安装

```
git clone https://github.com/RainboyOnlineJudge/rjudge 
cd rjudge
git submodule init
git submodule update
sudo apt-get update
sudo apt-get -y install software-properties-common python-software-properties python python-dev python-pip \
    locales python3-software-properties python3 python3-dev python3-pip \
    gcc g++ fp-compiler git libtool python-pip libseccomp-dev make cmake  redis-server  rsync cron

# 安装checker
cd checker && ./install.sh && cd ..

# 安装qjudge
cd qjudge && ./install.sh && cd ..

# 安装ujudge
cd ujudge && ./install.sh && cd ..

sudo useradd -r compiler

# rsync 配置

sudo cp rsync/etc/ /etc/
sudo chmod 600 /etc/rsyncd.secrets

# 路径
sudo mkdir -p /judge_server /judge_server/round /judge_server/data /judge_server/tmp

# 安装python 模块
sudo pip3 install -r requirements.txt

# 设置用户
useradd -r compiler

# 运行
redis-server &
sudo celery  worker -A config.celery &
sudo python3 server.py
```


### 使用docker

在使用docker的使用里不能使用ujudge 这个评测机,不知道为什么?

 1. clone这个代码,安装docker,可以使用`aliyun`的docker[加速器](https://cr.console.aliyun.com/?spm=5176.100239.blogcont29941.12.fOsBW8)
 2. 修改rsync,token的相关参数,建立data文件夹
  - 修改`run.sh`下的rsync的用户和密码
  - 修改`run.sh`下的token的密码
 3. 输入命令:`docker build -t rjudge .`,创建images
 4. `sudo docker run --net=host -it -v {你的data地址}:/judge_server/data -p 5000:5000 -p 873:873 -d rjudge`

### 一些配置

## 如何使用
使用的核心数: 在`config.py`里,cpu_count()

socket 消息监测:


消息:`request_judge`请求测评测,请求数据如下:

```
{
    "code":String,代码
    "lang":String,代码语言:c,cpp,pas,python3
    "time":int 时间 //second
    "memory":int 内存 //mb
    "stack":int 栈大小 //mb
    "output_size":输出大小 //mb
    "judge_id":请求评测的文件id,/judge_server/data 目录下
    "cmp": String, 文件比较器,fcmp2 ,或者是spj,如果是spj,就在data/jduge_id/目录下录找spj.cpp,或者spj.py?
    "judger":String,选择哪个评测机,qjudge,ujudge
    "revert":{ Object ,返回的数据
    }
}
```

## 返回信息


```js
socket.on('judge_respone',function(data){
})
```

```
{
    status:0,
    mid:START_JUDGE/1
}
```

返回信息的mid值
```
PREPARE_JUDGE   0
START_JUDGE     1
COMPILE         2
JUDGING         3
END_JUDGE       4
```

## 评测数据的流程


### PREPARE_JUDGE 阶段
判断数据文件是否,正常,数据文件夹是否存在

如果正确返回:

```
{
    status:0,
    mid:PREPARE_JUDGE,
    message:'评测数据正常',
    revert:you post revert,
    data:[["1.in","1.out"],["2.in","2.out"]......]  //返回的数据名
}
```

如果失败:

```
{
    status:-1,
    mid:PREPARE_JUDGE,
    err_code:1,
    message:'数据目录不存在',
    revert:you post revert,
    data_dir: data_dir_path '/'
}
```
```
{
    status:-1,
    mid:PREPARE_JUDGE,
    err_code:2,
    message:'数据目录为空',
    revert:you post revert,
    data_dir: data_dir_path '/'
}
```

```
{
    status:-1,
    mid:PREPARE_JUDGE,
    message:'没有找到in文件',
    err_code:3,
    raw_file_list:[a,b,c] //数据目录下的文件
}
```

```
{
    status:-1,
    message:'数据文件匹配结果为空',
    err_code:4,
    raw_file_list:[a,b,c]
}
```

### COMPILING 阶段

完成对上传代码和spj代码(如果有)的编译,成功后:

```
{
    status:0,
    message:'编译代码成功',
    mid:COMPILING,
    revert:you post revert
}
```

如果失败,返回

```
{
    status:-1,
    'mid':COMPILING,
    message:'代码编译失败',
    err_code:1,
    details:'' ,//失败原因
    revert: you post revert
}
```

```
{
    status:-1,
    mid:COMPILING,
    message:'还不支持这种文件比较器:'+_cmp
    err_code:2,
    revert: you post revert
}
```

```
{
    status:-1,
    mid:COMPILING,
    message:'文件比较器不存在:'+_cmp,
    err_code:3,
    revert: you post revert
}
```

```
{
    status:-1,
    mid:COMPILING,
    message:'编译spj失败',
    err_code:4,
    details:'' ,//失败原因
    revert: you post revert
}
```

### judge 评测阶段

```
{
    status:0,
    count:1, //第几个数据结果,
    mid:JUDGING,
    time: 时间 //ms
    memory: 内存 //kb
    result: 结果码,
    details: //答案错误细节
    revert:you post revert
}
```


### 整个评测结束

```
{
        "status":0,
        "mid":END_JUDGE,
        "result":[] //结果列表
        "revert":you post revert
}
```


## 支持的测评语言:

 - c++
 - c
 - pascal
 - python3.5


具体可以上传`tests`下的各个语言的代码看看


## 生成settings 类

其中`roundsetting`主要是产生各种参数,产生的参数如下

 - `revert` {} 返回的数据
 - `sid`    str socket_client_id
 - `cmp`    str 比较器 / spj.cpp
 - `code`   str 代码
 - `time`    时间
 - `memory`  内存
 - `judge_id` data 目录 下的数据所有的文件夹名
 - `round_id`:一个随机的字符串,`Handler`类初始化时传递过来
 - `data_dir`:和`problem_id`行成的评测数据路径
 - `round_dir`:和`round_id`行成的临时测评路径
 - `language_settings`:`languages.py`里对应的语言设定
 - `src_name`   源码名
 - `exe_name`   程序名
 - `src_path`   源码路径
 - `exe_path`   生成的程序路径
 - `compile_out_path` 编译输出
 - `compile_log_path` 编译的log
 - `compile_cmd`      编译的cmd
 - `seccomp_rule_name` 

## 数据检查

数据目录的数据是否正确
spj.cpp 是否存在

## 编译

## 评测

传递固定的参数,选择不同的评测机

## 结束评测,返回数据


数据类型为:

## 处理流程

生成settings 类

检查源数据文件目录
    - 是否存在
    - 数据命名是否规范
    - 返回相关信息
        - 长度
        - 文件列表 有序 [ [in,out]]

编译源代码 编译spj/复制cmp

评测
    - 文件比较

整体评测结束

## 数据命名规范

输入文件后缀`.in`,`.input`,`.txt`
输出文件后缀`.out`,`.ans`,`.output`



