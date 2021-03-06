import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import random
import send_mail
import configparser
# import logging
# import logging.config

"""
crontab 사용시 logging 모듈이 제대로 작동하지 않는 문제가 있어 주석처리 하였음
"""

# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger(__name__)

def neolook_alarm():
    dir = os.path.dirname(os.path.abspath(__file__))
    config = configparser.ConfigParser()
    config.read(dir + '/setting.cfg')
    server_setting_section = 'SERVER_SETTING'

    url = 'http://neolook.com/archives'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36'}
    keywords = tuple(config.get(server_setting_section, 'keyword').split(', '))

    data_dir = './data/'
    history_dir = './history/'
    server_dir = config.get(server_setting_section, 'server_dir')
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    if not os.path.isdir(history_dir):
        os.mkdir(history_dir)

    date = datetime.datetime.now().strftime('%Y%m%d')
    previous_html_name = '_archives.html'
    result_name = '_neolook_archives.html'

    html = requests.get(url, headers = headers).text
    html = html.replace('href="/', 'href="http://neolook.com/')
    html = html.replace('src="/', 'src="http://neolook.com/')
    # logger.info('Successful connection')

    try:
        previous_html = open(data_dir + previous_html_name, 'rt').read()
    except:
        # logger.info('No previous HTML file')
        previous_html = ' '
        pass
    else:
        pass
        # logger.debug('Found previous HTML file')

    soup = BeautifulSoup(html, 'html.parser')
    pre_soup = BeautifulSoup(previous_html, 'html.parser')

    cur_list = soup.find_all('li')
    pre_list = pre_soup.find_all('li')

    if pre_list != cur_list:
        # logger.debug('Check Data')

        head = soup.head
        body = soup.body
        body.div.decompose()    # decompose <div class='overlay'>...
        body.div.div.decompose()    # decompose <div class='sidebar'>...
        body.div.div.div.decompose()    #decompose <div class='toggle'>...
        body.div.div.div.div.div.decompose()    # decompose <div class="logo">...
        body.div.div.div.div.div.decompose()    # decompose <div class="text red">...
        body.div.div.div.div.div.decompose()    # decompose <div class="mailing">...
        body.div.div.div.div.script.decompose() # decompose <script src="http...>...

        items = body.find_all('li')
        items_num = len(items)
        count_num = 1

        for item in items:
            item_title = item.text.strip()
            item_url = item.a['href']
            item_html = requests.get(item_url, headers = headers).text
            # logger.debug('({}/{}): {}'.format(count_num, items_num, item_title))
            count_num = count_num + 1

            keyword_check = False
            for keyword in keywords:
                if (item_html.find(keyword) != -1):
                    keyword_check = True

            if (keyword_check == False):
                item.decompose()

            time.sleep(0.5)
            # time.sleep(random.randrange(1, 10))

        html_result = soup.prettify()
        try:
            previous_html_result = open(data_dir + result_name, 'rt').read()
        except FileNotFoundError as e:
            # logger.info('No previous result file')
            previous_html_result = ''

        if previous_html_result != html_result:

            current_item_set = set(soup.select('li a'))
            previous_item_set = set(BeautifulSoup(previous_html_result, 'html.parser').select('li a'))

            new_item_set = current_item_set - previous_item_set
            message = ''

            for item in new_item_set:
                message = message + item.text.strip() + '\n'

            send_mail.send_mail(message)    # send e-mail

            # Save Result at History Folder (./history/YYYYMMDD...)
            with open(history_dir + date + result_name, 'wt', encoding='utf8') as file:
                file.write(html_result)
            # Save Result at Data Folder (./data/...)
            with open(data_dir + result_name, 'wt', encoding='utf8') as file:
                file.write(html_result)
            # Save Result for web (/var/www/html/neolook_archive/...)
            with open(server_dir + result_name, 'wt', encoding='utf8') as file:
                file.write(html_result)
            # logger.info('Your data has been updated.')

        # Move Old HTML (Previous HTML --> ./old/YYYYMMDD...)
        with open(history_dir + date + previous_html_name, 'wt', encoding='utf8') as file:
                file.write(previous_html)
        # Save HTML
        with open(data_dir + previous_html_name, 'wt', encoding='utf8') as file:
                file.write(html)

    else:
        pass
        # logger.info('There is nothing to update.')

if __name__ == '__main__':
    neolook_alarm()

