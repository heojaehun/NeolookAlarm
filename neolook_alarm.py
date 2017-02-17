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
    # 실행 스크립트 절대경로
    path = os.path.dirname(os.path.abspath(__file__))

    # 설정파일 불러오기
    config = configparser.ConfigParser()
    config.read(path + '/setting.cfg')
    server_setting_section = 'SERVER_SETTING'
    keywords = tuple(config.get(server_setting_section, 'keyword').split(', '))
    server_path = config.get(server_setting_section, 'server_dir')

    # 결과파일 경로 및 파일명 설정
    data_path = path + './data/'
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    history_path = path + './history/'
    if not os.path.isdir(history_path):
        os.mkdir(history_path)

    date = datetime.datetime.now().strftime('%Y%m%d')
    previous_html_name = '_archives.html'
    result_name = '_neolook_archives.html'

    # 데이터 받아오기
    url = 'http://neolook.com/archives'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/41.0.2227.1 Safari/537.36'}
    html = requests.get(url, headers = headers).text
    html = html.replace('href="/', 'href="http://neolook.com/')
    html = html.replace('src="/', 'src="http://neolook.com/')
    # logger.info('Successful connection')

    # ./data/ 폴더로부터 지난 데이터 불러오기
    try:
        previous_html = open(data_path + previous_html_name, 'rt').read()
    except:
        # logger.info('No previous HTML file')
        previous_html = ' '
    else:
        pass
        # logger.debug('Found previous HTML file')

    # HTML 파싱 시작 (새로운 데이터와 지난 데이터)
    soup = BeautifulSoup(html, 'html.parser')
    pre_soup = BeautifulSoup(previous_html, 'html.parser')

    cur_list = soup.find_all('li')
    pre_list = pre_soup.find_all('li')

    # 새로운 데이터와 지난 데이터의 'li'리스트 차이가 있으면 업데이트 진행
    if pre_list != cur_list:
        # logger.debug('Check Data')

        # HTML 구조는 유지한체 불필요한 HTML 코드 지움
        body = soup.body
        body.div.decompose()    # decompose <div class='overlay'>...
        body.div.div.decompose()    # decompose <div class='sidebar'>...
        body.div.div.div.decompose()    #decompose <div class='toggle'>...
        body.div.div.div.div.div.decompose()    # decompose <div class="logo">...
        body.div.div.div.div.div.decompose()    # decompose <div class="text red">...
        body.div.div.div.div.div.decompose()    # decompose <div class="mailing">...
        body.div.div.div.div.script.decompose() # decompose <script src="http...>...

        items = body.find_all('li')

        # 각 항목별 키워드 검사
        for item in items:
            item_url = item.a['href']
            item_html = requests.get(item_url, headers=headers).text
            # logger.debug('({}/{}): {}'.format(count_num, items_num, item_title))

            for keyword in keywords:
                if (item_html.find(keyword) == -1):
                    item.decompose()

            time.sleep(0.5)
            # time.sleep(random.randrange(1, 10))

        # 결과 HTML 코드
        current_html_result = soup.prettify()

        try:
            previous_html_result = open(data_path + result_name, 'rt').read()
        except FileNotFoundError:
            previous_html_result = ''
            # logger.info('No previous result file')

        # 기존 결과 HTML 코드와 달라진 점 찾기 (새로 등록된 정보 찾기)
        if previous_html_result != current_html_result:
            current_item_set = set(BeautifulSoup(current_html_result, 'html.parser').select('li a'))
            previous_item_set = set(BeautifulSoup(previous_html_result, 'html.parser').select('li a'))
            new_item_set = current_item_set - previous_item_set

            # 갱신된 내용을 메일로 보내기
            message = ''
            for item in new_item_set:
                message = message + item.text.strip() + '\n'
            send_mail.send_mail(message)    # send e-mail

            # Save Result at History Folder (./history/YYYYMMDD...)
            with open(history_path + date + result_name, 'wt', encoding='utf8') as file:
                file.write(current_html_result)
            # Save Result at Data Folder (./data/...)
            with open(data_path + result_name, 'wt', encoding='utf8') as file:
                file.write(current_html_result)
            # Save Result for web (/var/www/html/neolook_archive/...)
            with open(server_path + result_name, 'wt', encoding='utf8') as file:
                file.write(current_html_result)
            # logger.info('Your data has been updated.')

        # Move Old HTML to history folder (Previous HTML --> ./history/YYYYMMDD...)
        with open(history_path + date + previous_html_name, 'wt', encoding='utf8') as file:
                file.write(previous_html)
        # Save HTML
        with open(data_path + previous_html_name, 'wt', encoding='utf8') as file:
                file.write(html)
    else:
        pass
        # logger.info('There is nothing to update.')

class NeolookAlarm(object):
    def __init__(self):
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.url = 'http://neolook.com/archives'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/41.0.2227.1 Safari/537.36'}
        self.keywords = tuple()


    def load_setting(self):
        config = configparser.ConfigParser()
        config.read(self.dir + '/setting.cfg')
        server_setting_section = 'SERVER_SETTING'
        self.keywords = tuple(config.get(server_setting_section, 'keyword').split(', '))



if __name__ == '__main__':
    neolook_alarm()

