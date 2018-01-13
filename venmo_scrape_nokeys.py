import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import datetime
from collections import deque
import csv

#finds last row for data comparison purposes
def get_last_row(csv_filename):
    with open(csv_filename, 'r') as f:
        try:
            lastrow = deque(csv.reader(f), 1)[0]
        except IndexError:  # empty file
            lastrow = None
        return lastrow

#pulls down venmo transactions
def scraper():
	#logging in to Venmo
	driver = webdriver.Firefox()
	driver.get('https://venmo.com/#public')

	detail = driver.find_element_by_class_name('icon-lock-blue')
	detail.click()

	time.sleep(3)

	logins = driver.find_elements_by_class_name('auth-form-input')
	logins[0].send_keys('enter email here')
	logins[1].send_keys('enter password here')

	time.sleep(3)

	login_but = driver.find_element_by_tag_name('button')
	login_but.click()

	time.sleep(3)

	no_access = driver.find_element_by_css_selector("a[href*='#']")
	no_access.click()

	time.sleep(3)

	bank = driver.find_element_by_class_name('auth-form-input')
	bank.send_keys('enter bank number here')

	time.sleep(3)

	login_but = driver.find_element_by_tag_name('button')
	login_but.click()

	time.sleep(3)

	login_but = driver.find_elements_by_tag_name('button')
	login_but[0].click()

	time.sleep(3)

	driver.get('https://venmo.com/#public')

	time.sleep(10)

	now = datetime.datetime.now()

	#clicking load more 200 times
	holder = 0
	while holder < 200:
		try:
			more = driver.find_element_by_class_name('moreButton')
			more.click()
			time.sleep(1)
			holder += 1
		except:
			holder += 1

	pghtml = driver.page_source

	try:
		splits = pghtml.split('<!-- FRIENDS FEED -->')
		pghtml = splits[0]

	except:
		pass

	soup = BeautifulSoup(pghtml, "html.parser")

	rows = soup.find_all(class_ = 'align_top p_ten_l p_ten_b')

	exchanges = []

	#reading each transaction in
	for row in rows:
		try:
			transaction = row.find_all(class_ = 'm_five_t p_ten_r')
			people = transaction[0].contents
			sender = str((people[1])['href'])
			receiver = str((people[3])['href'])
			pay_type = str(people[2]).strip()
			descriptions = row.find_all('div', style="word-wrap:break-word")
			description = (descriptions[0].string).strip()
			times = row.find_all(class_ = 'gray_link')

			if times[0].string == 'just now':
				now_time = now

			elif 'seconds' in times[0].string:
				time_delta = [int(s) for s in (times[0].string).split() if s.isdigit()][0]
				now_time = now - datetime.timedelta(seconds=time_delta)

			elif 'minutes' in times[0].string:
				time_delta = [int(s) for s in (times[0].string).split() if s.isdigit()][0]
				now_time = now - datetime.timedelta(minutes=time_delta)

			elif 'about an hour ago' in times[0].string:
				now_time = now - datetime.timedelta(hours=1)

			elif 'hours' in times[0].string:
				time_delta = [int(s) for s in (times[0].string).split() if s.isdigit()][0]
				now_time = now - datetime.timedelta(hours=time_delta)

			if pay_type == 'paid':
				exchanges.append((sender,receiver,description,now_time))
			else:
				exchanges.append((receiver,sender,description,now_time))

		except:
			pass

	most_recent = get_last_row('venmo_data.csv')
	try:
		recent_time = datetime.datetime.strptime(most_recent[3],"%Y-%m-%d %H:%M:%S.%f")
		exchanges = [x for x in exchanges if x[3] > recent_time]
		print('success')
	except:
		print('failed')

	exchanges.reverse()

	#writing to csv
	with open('venmo_data.csv','a') as outfile:
		for exchange in exchanges:
			out = (exchange[0]).encode('utf-8')+','+(exchange[1]).encode('utf-8')+','+(exchange[2]).encode('utf-8')+','+str(exchange[3])
			outfile.write(out)
			outfile.write("\n")
		outfile.close()

	driver.close()

	time.sleep(900)

while datetime.datetime.now() < datetime.datetime(2016,12,13,23,30):
	scraper()
