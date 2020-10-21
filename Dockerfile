FROM l4t:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=check-yaskawa-robot-connection\
    AION_HOME=/var/lib/aion \
    MYSQL_HOST=localhost \
    MYSQL_USER=latona \
    MYSQL_PASSWORD=Latona2019!

# Setup Directoties
RUN mkdir -p /${AION_HOME}/$POSITION/$SERVICE

WORKDIR /${AION_HOME}/$POSITION/$SERVICE

RUN apt-get update \
 && apt-get -y install iputils-ping net-tools \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ADD . .
RUN python3 setup.py install

CMD ["python3", "-m", "checkrobot"]
