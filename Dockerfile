FROM python:3.9.1-slim-buster
ENV GIT_PYTHON_REFRESH=quiet
ENV LENINEC_DOCKER=1

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install \
    --no-warn-script-location \
    --no-cache-dir \
    --upgrade \
    --disable-pip-version-check \
    -r /app/requirements.txt

RUN rm -rf /tmp/*

COPY . /app

WORKDIR /app

CMD ["python3", "bot.py"]
