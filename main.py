import requests 
from bs4 import BeautifulSoup as bs
import json
import sqlite3
from datetime  import datetime
import time

TIMEOUT = 0.5
HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0',
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language' : 'en-US,en;q=0.5',
		'Accept-Encoding' : 'gzip, deflate'
	}
LOGIN_URL = 'http://elearning.kazgasa.kz/login/index.php'


def connect_db():
    """
    Connect to local db
    return: connection cursor
    """
    conn = sqlite3.connect('../Course_enterer/app.db')
    c = conn.cursor()   
    return c

def get_users(cursor):
    result = []
    for row in cursor.execute('SELECT username,password FROM users'):
        result.append(row)
    return result

def login(username,password):
    session = requests.Session()
    response = session.get(LOGIN_URL, headers=HEADERS, verify=False,timeout=TIMEOUT)
    soup = bs(response.content,'lxml')
    logintoken = soup.find('input', {'name':'logintoken'})['value']
    data ={'username':username,'password':password,'logintoken':logintoken}
    req = session.post("http://elearning.kazgasa.kz/login/index.php", data = data,timeout=TIMEOUT,headers = HEADERS, verify=False)

    return session, req.content

def get_courses_url(content):
    """
    params: 
    content = content with courses 
    return:
    courses = list with courses url
    """
    courses_url = []
    soup = bs(content,'lxml')
    a_s = soup.find_all('a', class_ = 'list-group-item list-group-item-action')
    for a in a_s:
        href = a.get('href') 
        courses_url.append(href)
    #delete main_page,calendar url`s
    result = courses_url[3:]
    return result

def follow_links(session, links):
    for link in links:
        courses = session.get(url=link, headers=HEADERS, timeout=TIMEOUT)
        
def is_time():
    utcnow = datetime.utcnow()
    hour = utcnow.hour + 6
    minute = utcnow.minute
    dec_hour = hour+minute/60
    return (dec_hour)

def main():
    while True:
        try:
            hour = is_time()
            if hour > 8.5 and hour < 13:
                cursor = connect_db()
                users = get_users(cursor)
                for user in users:
                    session, content = login(username=user[0],password=user[1])
                    courses_url = get_courses_url(content)
                    follow_links(session, courses_url)
                time.sleep(60)

            else:
                time.sleep(20)
        except Exception as e:
            print (e)
            pass


if __name__ == "__main__":
    main()