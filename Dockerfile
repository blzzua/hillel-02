FROM python:3.10
ENV PYTHONUNBUFFERED True
ENV PORT 8000
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY .env ./
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
