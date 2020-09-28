import requests 
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import json
import sqlite3
import time

TIMEOUT = 60
HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0',
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language' : 'en-US,en;q=0.5',
		'Accept-Encoding' : 'gzip, deflate',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Host':'elearning.kazgasa.kz'}
        # не забыть сессию
	
LOGIN_URL = 'http://elearning.kazgasa.kz/login/index.php'
ATTENDANCE_URL = 'http://elearning.kazgasa.kz/mod/attendance/view.php?id=42495'
CALENDAR_URL = "http://elearning.kazgasa.kz/calendar/view.php?view=day&time={}"


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
    session.post("http://elearning.kazgasa.kz/login/index.php", data = data,timeout=TIMEOUT,headers = HEADERS, verify=False)

    return session

def get_attendance_url(session,url):
    r = session.get(url)
    soup = bs(r.content,"lxml")
    
    a = soup.find_all("td",class_ ='statuscol cell c2 lastcol')[-1].find("a").get("href")  #a = soup.find_all("td",class_ ='statuscol cell c2 lastcol')[-1].find("a").get("href")                               IndexError: list index out of range  

    splitten = a.split("=")
    sesskey = splitten[-1]
    sessid = splitten[1].split("&")[0]
    session.get(a)
    return sesskey,sessid,session,a

def current_time_unix():
    utc = datetime.utcnow()
    unixtime = time.mktime(utc.timetuple())
    local = int(unixtime)+(3600*12)
    return local

def get_lessons(session):
    time = current_time_unix()
    url = ((CALENDAR_URL).format(str(time)))

    r = session.get(url)
    soup = bs(r.content, "lxml")
    all_event = soup.find('div',class_ = 'eventlist my-1').find_all('div',class_ = 'event m-t-1')
    lesson_attendance_urls = []
    for i in all_event:
        lesson_url = i.find("div", class_='card-footer text-right bg-transparent')\
                                                .find('a').get('href')
        lesson_attendance_urls.append(lesson_url)
    return lesson_attendance_urls

def get_status_from_btn(session,url):
    r = session.get(url)
    soup = bs(r.content,"lxml")
    status = soup.find_all("input",class_ = "form-check-input")[0].get("value")
    return status

def is_time():
    utcnow = datetime.utcnow()
    hour = utcnow.hour + 6
    minute = utcnow.minute
    dec_hour = hour+minute/60
    return (dec_hour)


def do(user):
    
    username = user[0]
    password = user[1]
    session = login(username,password)
    lessons_url = get_lessons(session)
    for lesson in lessons_url:
        try:
            sesskey,sessid ,session,a = get_attendance_url(session,lesson)
            status = get_status_from_btn(session,a)
            attendant_post_data = {'sessid':sessid,
                                  'sesskey':sesskey,
                                  '_qf__mod_attendance_student_attendance_form':1,
                                  'mform_isexpanded_id_session':1,
                                  'status':status,
                                  'submitbutton':'%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C'}
            session.post("http://elearning.kazgasa.kz/mod/attendance/attendance.php",data= attendant_post_data, headers= HEADERS)
        except Exception as e:
              print (e)

def main():
    while True:
        try:
            hour = is_time()
            if hour > 8.5 and hour < 14:
                cursor = connect_db()
                users = get_users(cursor)
                for user in users:
                    try:
                        do(user)
                    except Exception as e:
                        print (e)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
