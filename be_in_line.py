import requests 
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import pytz
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




def login(username,password):
    session = requests.Session()
    response = session.get(LOGIN_URL, headers=HEADERS, verify=False,timeout=TIMEOUT)
    soup = bs(response.content,'lxml')
    logintoken = soup.find('input', {'name':'logintoken'})['value']
    data ={'username':username,'password':password,'logintoken':logintoken}
    req = session.post("http://elearning.kazgasa.kz/login/index.php", data = data,timeout=TIMEOUT,headers = HEADERS, verify=False)

    return session, req.content

def get_attendance_url(session):
    r = session.get(ATTENDANCE_URL)
    soup = bs(r.content,"lxml")
    
    a = soup.find_all("td",class_ ='statuscol cell c2 lastcol')[0].find("a").get("href")  #a = soup.find_all("td",class_ ='statuscol cell c2 lastcol')[-1].find("a").get("href")                               IndexError: list index out of range  
    
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
    r = session.get((CALENDAR_URL).format(str(time)))
    print (url)
    

def get_status_from_btn(url):
    r =session.get(url)
    soup = bs(r.content,"lxml")
    status = soup.find_all("input",class_ = "form-check-input")[0].get("value")
    return status

if __name__ == "__main__":
    
    local = current_time_unix()
    session, content = login("41711251","4#rBFVPKi7")
    get_lessons(session)
    sesskey,sessid ,session,a = get_attendance_url(session)
    status = get_status_from_btn(a)
    attendant_post_data = {'sessid':sessid,
                        'sesskey':sesskey,
                        '_qf__mod_attendance_student_attendance_form':1,
                        'mform_isexpanded_id_session':1,
                        'status':status,
                       'submitbutton':'%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C'}
    a = session.post("http://elearning.kazgasa.kz/mod/attendance/attendance.php",data= attendant_post_data, headers= HEADERS)
    a.headers

    