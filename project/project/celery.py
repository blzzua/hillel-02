import logging
import os
import requests
import smtplib
from django.conf import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('proj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

import django   # noqa
django.setup()
from orders.models import Order  # noqa

API_TOKEN = os.environ.get('CELERY_TGBOT_APIKEY')
CHATID_ORDER = os.environ.get('CELERY_TG_CHATID_ORDER')


def send_to_telegram(text):
    apiToken = API_TOKEN
    chatID = CHATID_ORDER
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': text})
        print(response.text)
    except Exception as e:
        logging.error(e)


@app.task(bind=True)
def alert_order_task(self, order_id):
    order = Order.objects.get(pk=order_id)
    order_items_lines = [
        f'{item.item_id.caption} {item.item_price} x {item.quantity} = {item.amount} (-{item.discount_amount})'
        for item in order.order_items.all()
    ]
    pl = '\n'.join(order_items_lines)
    message = f"""Used {order.user_name.username} ordered №{order.order_number} [id={order.id}]: {order.total_amount}"""
    if len(pl) < 1000:
        message += '\n' + pl
    else:
        message += '\n' + f'.. to long. {order_items_lines} items'
    send_to_telegram(message)


@app.task(bind=True)
def send_otp(self, phone_number, otp):
    message = f"""Код для входу valheim food shop для {phone_number}: {otp}"""
    send_to_telegram(message)


@app.task(bind=True)
def mail_admins_task(self, message_parts):
    # receivers = ','.join([f'{addr}' for alias, addr in settings.ADMINS])
    receivers = ','.join([f'{alias} <{addr}>' for alias, addr in settings.ADMINS])
    msg = MIMEMultipart()
    msg['From'] = settings.DEFAULT_FROM_EMAIL
    msg['To'] = receivers
    msg['Subject'] = message_parts['Subject']
    body = message_parts['Body']
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, int(settings.EMAIL_PORT))
        server.starttls()
        server.login(user=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD)
        text = msg.as_string()
        logging.debug(f'Trying to send server.sendmail(\n{settings.DEFAULT_FROM_EMAIL}, \n{receivers},\n{text})\n\n')
        server.sendmail(settings.DEFAULT_FROM_EMAIL, receivers, text)
        server.quit()
        logging.debug('Повідомлення успішно надіслано')
    except Exception as e:
        logging.error('Помилка підключення або відправки повідомлення:', str(e))
