FROM python:3.8.9-slim-buster

RUN apt update -y
RUN apt upgrade -y
RUN apt install git -y
RUN apt install npm -y

RUN pip3 install pipenv

RUN git clone https://github.com/pyenv/pyenv.git /.pyenv
ENV PYENV_ROOT /.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN useradd -ms /bin/bash botwangy

COPY src /src
RUN chown -R root:root /src
RUN chmod -R 755 /src

WORKDIR /src/view
RUN npm install
RUN npm run build

WORKDIR /src
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip install -r requirements.txt

USER botwangy

# CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "wsgi:app"]
CMD gunicorn wsgi:app --bind 0.0.0.0:$PORT
