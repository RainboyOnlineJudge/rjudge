# rJudge
# VERSION 1
# Author: Rainboy

FROM ubuntu:16.04
MAINTAINER Rainboy Rainboylvx@gmail.com
ENV DEBIAN_FRONTEND noninteractive

COPY sources.list /etc/apt/
RUN apt-get update
RUN apt-get -y install software-properties-common python-software-properties python python-dev python-pip \
    locales python3-software-properties python3 python3-dev python3-pip \
    gcc g++ git libtool python-pip libseccomp-dev cmake openjdk-8-jdk redis-server fp-compiler rsync
RUN apt-get -y install cron
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Copy main code

RUN mkdir -p /var/www/rjudge && mkdir ~/.pip/
COPY . /var/www/rjudge/
WORKDIR /var/www/rjudge

# Copy crontab
COPY crontab /var/spool/cron/crontabs/root

# rsync
COPY rsync/etc/ /etc/
RUN  chmod 600 /etc/rsyncd.secrets

# Install judger
RUN useradd -r compiler
COPY judger/java_policy /etc/
RUN cd judger && chmod +x runtest.sh
RUN cd judger && ./runtest.sh; exit 0

# Install checker
RUN cd testlib && ./build.sh

COPY pip.conf ~/.pip/
RUN pip3 install -r requirements.txt
RUN mkdir -p /judge_server /judge_server/round /judge_server/data /judge_server/tmp
RUN chmod 600 token.txt

#HEALTHCHECK --interval=30s --retries=3 CMD python3 healthcheck.py

EXPOSE 4999
EXPOSE 873

RUN chmod +x run.sh
CMD ./run.sh
