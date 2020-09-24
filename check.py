# -*- coding: utf-8 -*-
import os
import requests
import threading
import time
from lxml import html
import pickledb
from bottle import install, route, run
from logger_tools import logger, log_to_logger
from tools import send_telegram
from requests.exceptions import RequestException

SEARCH_ITEMS = [
    {"name": "", "max_price": 31000},
    {"name": "", "max_price": 500000},
    {
        "name": "",
        "max_price": 550000,
    },
]

lock = threading.Lock()


def start_task():
    lock.acquire()
    db = pickledb.load("xxx.db", False, False)
    lock.release()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.avito.ru",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0,",
    }
    while True:
        for search in SEARCH_ITEMS:
            try:
                r = requests.get("https://www.avito.ru{}".format(search["name"]), headers=headers, verify=False)
                logger.info("--------Successfull request----------")
                if db.totalkeys() > 30:
                    logger.info("DataBase was dropped")
                    lock.acquire()
                    db.deldb()
                    lock.release()

                tree = html.fromstring(r.content)
                items = tree.xpath(
                    '//div[@class="js-catalog_serp"]/div[@class="item item_table clearfix js-catalog-item-enum  item-with-contact js-item-extended"]'
                    '/div[@class="item__line"]/div[@class="item_table-wrapper"]/div[@class="description item_table-description"]'
                )
                links = []
                for item in items:
                    link = item.xpath(
                        './div[@class="item_table-header"]/h3[@class="title item-description-title"]/a[@class="item-description-title-link"]'
                    )[0].get("href")
                    price = item.xpath('./div[@class="item_table-header"]/div[@class="about"]/span[@class="price "]')[
                        0
                    ].get("content")
                    date = item.xpath('./div[@class="data"]/div[@class="js-item-date c-2"]')[0].get(
                        "data-absolute-date"
                    )
                    if "Вчера" in date or "Сегодня" in date:
                        if int(price) <= search["max_price"]:
                            id = link.split("_")[-1]
                            if not db.exists(id):
                                links.append("https://www.avito.ru" + link)
                                lock.acquire()
                                db.set(id, None)
                                lock.release()
                db.dump()

                if links:
                    send_telegram(" \n".join(links))

            except RequestException as e:
                logger.debug("Request failed with error: %s" % (str(e)))
        time.sleep(20 * 60)


@route("/health")
def health():
    return "OK"


@route("/start")
def start():
    if threading.active_count() == 1:
        task_thread = threading.Thread(target=start_task)
        task_thread.setDaemon(True)
        task_thread.start()
        return "Started the service"
    else:
        return "Service has already been started"


install(log_to_logger)
# run(host='localhost', port=8080, debug=True)
run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
