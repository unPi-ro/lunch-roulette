FROM debian:latest

LABEL maintainer="your name <email@address>"

RUN useradd webot

RUN apt-get update

# you might need this for SSH.ing back into the container
RUN apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker/For/Noobs" | chpasswd

COPY sshd_config /etc/ssh/

# install python baseline
RUN apt-get install -y python3 python3-dev python3-venv

WORKDIR /home/webot

COPY requirements.txt requirements.txt

RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY roulette.py config.py boot.sh ./

RUN chmod +x boot.sh

ENV FLASK_APP roulette.py

EXPOSE 2222 80

ENTRYPOINT ["./boot.sh"]
