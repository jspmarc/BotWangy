FROM python:3.8.9-slim-buster

RUN apt update -y
RUN apt upgrade -y
RUN apt install git -y
RUN apt install npm -y

RUN pip3 install pipenv

RUN git clone https://github.com/pyenv/pyenv.git /.pyenv
ENV PYENV_ROOT /.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

EXPOSE 80

COPY src /src
WORKDIR /src/view
RUN npm install
RUN npm run build
WORKDIR /src
RUN pipenv lock --keep-outdated --requirements > requirements.txt
RUN pip install -r requirements.txt
CMD ["gunicorn", "--bind", ":80", "wsgi:app"]
