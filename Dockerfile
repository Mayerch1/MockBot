FROM python:3

RUN pip3 install discord.py discord-py-slash-command tinydb Pillow dblpy Flask waitress web.py requests_html

WORKDIR /code
CMD ["python", "mockBot.py"]
