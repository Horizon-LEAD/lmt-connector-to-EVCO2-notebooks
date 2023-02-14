FROM python:3.10.2-slim-bullseye

COPY setup.py requirements.txt README.md /srv/app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /srv/app/requirements.txt

COPY src srv/app/src
RUN pip install --no-cache-dir /srv/app

ENTRYPOINT [ "lmt2evco2", "-vv" ]
