FROM python:3.7-alpine

ADD . /app

WORKDIR app

RUN pip install pipenv && pipenv install

VOLUME /nbt

EXPOSE 80

CMD ["python", "-m", "pipenv", "run", "python", "/app/newfriend.py"]