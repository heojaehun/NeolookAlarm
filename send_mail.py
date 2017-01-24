import smtplib
from email.mime.text import MIMEText
import configparser

def send_mail():
	config = configparser.ConfigParser()
	config.read('setting.cfg')
	mail_info_section = 'MAIL_INFO'

	sender = config.get(mail_info_section, 'sender')
	receivers = config.get(mail_info_section, 'receivers').split(', ')
	password = config.get(mail_info_section, 'password')
	subject = '네오룩 알림 서비스'
	message = '''네오룩 아카이브가 업데이트 되었습니다.
	http://jakupsil.iptime.org/neolook_archive/_neolook_archives.html
	파싱 키워드: '미디어', '게임', 'media', 'game'
	'''

	server = smtplib.SMTP_SSL('smtp.naver.com', 465)
	server.login(sender, password)

	for receiver in receivers:
	    msg = MIMEText(message, _charset='utf8')
	    msg['Subject'] = subject
	    msg['From'] = sender
	    msg['To'] = receiver

	    #server.sendmail(sender, [receiver], body.encode('utf8'))
	    server.sendmail(sender, [receiver], msg.as_string())

	server.quit()

	print('...Mail sended!...')

def send_mail(_message):
	config = configparser.ConfigParser()
	config.read('setting.cfg')
	mail_info_section = 'MAIL_INFO'

	sender = config.get(mail_info_section, 'sender')
	receivers = config.get(mail_info_section, 'receivers').split(', ')
	password = config.get(mail_info_section, 'password')
	subject = '네오룩 알림 서비스'
	message = '''네오룩 아카이브가 업데이트 되었습니다.
http://jakupsil.iptime.org/neolook_archive/_neolook_archives.html
파싱 키워드: '미디어', '게임', 'media', 'game'

=== 새로 업데이트된 항목 ===
''' + _message

	server = smtplib.SMTP_SSL('smtp.naver.com', 465)
	server.login(sender, password)

	for receiver in receivers:
	    msg = MIMEText(message, _charset='utf8')
	    msg['Subject'] = subject
	    msg['From'] = sender
	    msg['To'] = receiver

	    #server.sendmail(sender, [receiver], body.encode('utf8'))
	    server.sendmail(sender, [receiver], msg.as_string())

	server.quit()

	print('...Mail sended!...')


if __name__ == '__main__':
    send_mail('테스트입니다.')
