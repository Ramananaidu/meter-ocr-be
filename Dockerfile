FROM python:3.9-slim

# Install Python Setuptools
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN apt-get update -y
RUN  pip3 install --upgrade pip
RUN  pip3 install --no-cache-dir -r requirements.txt
EXPOSE  5000
CMD ["app.py"]