FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    python3 \
    python3-pip

RUN ln -s /usr/bin/python3 /usr/bin/python

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:${PATH}"

# Ustaw domyślną wersję pip jako pip3
RUN ln -s -f /usr/bin/pip3 /usr/bin/pip

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN apt-get install tesseract-ocr -y
RUN apt-get install poppler-utils

# docker build -t mlegtest .
# docker run -it mlengtest