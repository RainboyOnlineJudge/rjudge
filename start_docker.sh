#docker run -p 8080:873 test
docker run -v /home/server1/data:/judge_server/data -p  8080:873 -p 4999:4999 -d rjudge
