From ubuntu:latest

RUN apt update
RUN apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt update
RUN apt install -y docker-ce
RUN apt-get update && \
    apt-get install -y python python-dev python-pip 

RUN apt -y install python-numpy python-matplotlib python-scipy python-wxgtk3.0 mongodb
RUN pip install quantities bagit pymongo==2.8


Add . /home/app
WORKDIR /home/app
RUN chmod +x run.sh
CMD ["/home/app/run.sh"]