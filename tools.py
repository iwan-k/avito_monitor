import smtplib
import requests
from logger_tools import logger


def send_email(msg):
    mailer = smtplib.SMTP_SSL("smtp.mail.ru")
    mailer.login("", "")
    message = "Subject: {}\n\n{}".format("Updates", msg)
    mailer.sendmail("", [""], message)
    mailer.quit()
    logger.info("Email was sent")


def send_telegram(msg):
    params = {"chat_id": 477872864, "text": msg}
    res = requests.get(
        url="https://api.telegram.org/xxx/sendMessage", params=params
    )
    if res.status_code == 200:
        logger.info("Telegram message was sent")
    else:
        logger.error("Error when sending telegram message")
    # how to get user/chat id:
    # res = requests.get('https://api.telegram.org/bot<bot_id>/getUpdates')
    # print(res.text)
