import requests 
from bs4 import BeautifulSoup as bs
import json

headers = {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0',
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language' : 'en-US,en;q=0.5',
		'Accept-Encoding' : 'gzip, deflate'
	}
LOGIN_URL = 'http://elearning.kazgasa.kz/login/index.php'
s = requests.Session()
response = s.get(LOGIN_URL, headers=headers, verify=False)
#logintokenparser
soup = bs(response.content,'html.parser')
logintoken = soup.find('input', {'name':'logintoken'})['value']
headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
headers['content-type'] = 'application/x-www-form-urlencoded'
data ={'username':'adminus','password':'1lhfgSv?aTvQ','logintoken':logintoken}
req = s.post("http://elearning.kazgasa.kz/login/index.php", data = data,headers = headers, verify=False)




#проверяет список на какие он курсы подписан и создает список, содержаший эти url
payload = {'elementid':'expandable_branch_0_mycourses',
            'id':'mycourses',
            'type':'0',
            'sesskey':'QThfgh',
            'instance':'4'
            }
get_nav_bar = s.post("http://elearning.kazgasa.kz/lib/ajax/getnavbranch.php",data=payload , headers = headers)


soup = bs(req.content,  features="html.parser")
my_json = json.loads(get_nav_bar.text)

course_links = []
for i in range(len(my_json['children'])):
    link = my_json['children'][i]['link']
    course_links.append(link)

for link in course_links:
    course = s.get(url = link,headers = headers)
    print ("Succesfully entered in ",link)
