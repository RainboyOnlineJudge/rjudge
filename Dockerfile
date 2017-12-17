# rjudge
# VERSION 2
# Author: Rainboy

FROM ubuntu:16.04
MAINTAINER Rainboy Rainboylvx@qq.com
ENV DEBIAN_FRONTEND noninteractive

COPY sources.list /etc/apt/
RUN apt-get update
RUN apt-get -y install software-properties-common python-software-properties python python-dev python-pip \
    locales python3-software-properties python3 python3-dev python3-pip \
    gcc g++ fp-compiler git libtool python-pip libseccomp-dev make cmake  redis-server  rsync cron
#RUN apt-get -y install cron
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


# Copy main code

RUN mkdir -p /var/www/rjudge && mkdir ~/.pip/
COPY . /var/www/rjudge/
WORKDIR /var/www/rjudge

# 更新submodule
RUN cd /var/www/rjudge && git submodule init && git submodule update

# 安装checker
RUN cd /var/www/rjudge/checker && ./install.sh

# 安装qjudge
RUN cd /var/www/rjudge/qjudge && ./install.sh

# 安装ujudge
RUN cd /var/www/rjudge/ujudge && ./install.sh

# 安装fpc
#RUN cd /var/www/rjudge/free_pascal_compiler && ./install.sh


# Copy crontab
COPY crontab /var/spool/cron/crontabs/root

# rsync
COPY rsync/etc/ /etc/
RUN  chmod 600 /etc/rsyncd.secrets

RUN useradd -r compiler


#COPY pip.conf ~/.pip/
RUN pip3 install -r requirements.txt
RUN mkdir -p /judge_server /judge_server/round /judge_server/data /judge_server/tmp
RUN chmod 600 token.txt

#HEALTHCHECK --interval=30s --retries=3 CMD python3 healthcheck.py

EXPOSE 5000
EXPOSE 873

RUN chmod +x run.sh
CMD ./run.sh
