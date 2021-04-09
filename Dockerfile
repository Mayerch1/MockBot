FROM python:3

RUN pip3 install discord.py discord-py-slash-command tinydb Pillow dblpy

WORKDIR /code
CMD ["python", "mockBot.py"]
