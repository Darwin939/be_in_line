import requests 
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import json
import sqlite3
import time
from threading import Thread

#TODO 1) documentation to the funcs
#TODO 2) timezones or learn how to set time to unix
#TODO 3) threading 
#TODO 4) delete 

TIMEOUT = 30
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
      
    return conn

def get_users(cursor):
    """
    Getting username and password from cursor db
    return: tuple(username,password)
    """
    result = []
    db = sqlite3.connect('../Course_enterer/app.db')
    rows = db.cursor().execute('SELECT username,password FROM users;')
    for row in rows:
        result.append(row)
    return result

def login(username,password):
    """
    Logining to the site
    return: request.Session 
    """
    session = requests.Session()
    response = session.get(LOGIN_URL, headers=HEADERS, verify=False,timeout=TIMEOUT)
    soup = bs(response.content,'lxml')
    logintoken = soup.find('input', {'name':'logintoken'})['value']
    data ={'username':username,'password':password,'logintoken':logintoken}
    session.post("http://elearning.kazgasa.kz/login/index.php", data = data,timeout=TIMEOUT,headers = HEADERS, verify=False)
    return session

def get_attendance_url(session,url):
    """
    Get attendance_url and some keys to login that
    return:
    """
    r = session.get(url)
    soup = bs(r.content,"lxml")
    a = soup.find_all("td",class_ ='statuscol cell c2 lastcol')[-1].find("a").get("href")
    splitten = a.split("=")
    sesskey = splitten[-1]
    sessid = splitten[1].split("&")[0]
    session.get(a)
    return sesskey,sessid,session,a

def current_time_unix()->int:
    """
    Get local time in unix
    return: int
    """
    utc = datetime.utcnow()
    unixtime = time.mktime(utc.timetuple())
    local = int(unixtime)+(3600*12)
    return local

def get_lessons(session)->list:
    """
    Getting url`s lesson attendance
    return: list
    """
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

def get_status_from_btn(session,url)->str:
    """
    Get button value
    return: str 
    """
    r = session.get(url)
    soup = bs(r.content,"lxml")
    status = soup.find_all("input",class_ = "form-check-input")[0].get("value")
    return status

def is_time()->float:
    """
    Getting decimal time 
    return: float
    """
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    dec_hour = hour+minute/60
    return (dec_hour)

def lesson_async_iterator(lesson,session):
    """
    docstring
    """
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

def go_to_lesson(url, session):
    session.get(url)

def is_valid(session):
    r = session.get("http://elearning.kazgasa.kz/course/view.php?id=4161" , allow_redirects=False)
    if r.status_code > 300:
        return False
    return True

def delete_from_db(username):
    """
    Delete user , whose  login or password incorect
    """
    command = "DELETE FROM users WHERE username='{}';".format(username)
    connection = connect_db()
    connection.cursor().execute(command)
    connection.commit()

def do(user):
    """
    main func that assembly all func 
    """
    username = user[0]
    password = user[1]
    session = login(username, password)
    if not is_valid(session):
        delete_from_db(username)
    lessons_url = get_lessons(session)
    
    for lesson in lessons_url:
        th = Thread(target=lesson_async_iterator,args=(lesson,session))
        th2 = Thread(target=go_to_lesson,args=(lesson,session))
        th.start()
        th2.start()
    th.join()
    th2.join()





def main():
    while True:
        try:
            hour = is_time()
            if hour > 8.5 and hour < 15:
                cursor = connect_db()
                users = get_users(cursor)
                for user in users:
                    print ("Do it for user",user[0])
                    do(user)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
    
