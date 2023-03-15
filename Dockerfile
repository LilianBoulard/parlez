FROM python:3.8 AS intermediate

WORKDIR /usr/src/app

RUN apt-get update -qq
RUN apt-get update -y
RUN apt-get install -y git
RUN apt-get install -y ffmpeg
RUN rm -rf /var/cache/apt

COPY . .

# Install project requirements
RUN pip install --upgrade --disable-pip-version-check --no-input -r requirements.txt

RUN sh setup_tortoise.sh

# Launch the server at runtime
ENTRYPOINT ["sh", "deploy.sh"]
