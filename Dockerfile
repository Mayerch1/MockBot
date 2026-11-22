FROM python:3.11

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./Bot .
COPY ./legal ./legal/

WORKDIR /code
CMD ["python", "-OO", "mockBot.py"]
