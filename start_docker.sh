#docker run -p 8080:873 test
docker run --net=host -v /home/server1/data:/judge_server/data -p  873:873 -p 4999:4999 -d rjudge
