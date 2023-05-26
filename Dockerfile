FROM python:3.8
ENV PYTHONUNBUFFERED True
ENV PORT 8000
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY project ./project
COPY .env ./
RUN echo "SECRET_KEY=`cat /dev/urandom | base64 -w96 | head -n1`" >> .env

WORKDIR $APP_HOME/project
#CMD exec gunicorn -b :${PORT:-8000}  --workers 1 --threads 2 --timeout=0 'project.wsgi:application"'
CMD python manage.py runserver 0.0.0.0:${PORT:-8000} 

