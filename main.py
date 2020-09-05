import requests 
from bs4 import BeautifulSoup as bs
import json

HEADERS = {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0',
		'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language' : 'en-US,en;q=0.5',
		'Accept-Encoding' : 'gzip, deflate'
	}
LOGIN_URL = 'http://elearning.kazgasa.kz/login/index.php'



def login(username,password):
    session = requests.Session()
    response = session.get(LOGIN_URL, headers=HEADERS, verify=False)
    soup = bs(response.content,'lxml')
    logintoken = soup.find('input', {'name':'logintoken'})['value']
    data ={'username':username,'password':password,'logintoken':logintoken}
    req = session.post("http://elearning.kazgasa.kz/login/index.php", data = data,headers = HEADERS, verify=False)

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








#logintokenparser
#проверяет список на какие он курсы подписан и создает список, содержаший эти url
# payload = {'elementid':'expandable_branch_0_mycourses',
#             'id':'mycourses',
#             'type':'0',
#             'sesskey':'QThfgh',
#             'instance':'4'
#             }
# get_nav_bar = s.post("http://elearning.kazgasa.kz/lib/ajax/getnavbranch.php",data=payload , headers = headers)


# soup = bs(req.content,  features="html.parser")
# my_json = json.loads(get_nav_bar.text)

# course_links = []
# for i in range(len(my_json['children'])):
#     link = my_json['children'][i]['link']
#     course_links.append(link)

# for link in course_links:
#     course = s.get(url = link,headers = headers)
#     print ("Succesfully entered in ",link)


def main():
    data = {'username': '41711251',
            'password':'4#rBFVPKi7'}
    session, content = login(username=data['username'],password=data['password'])
    courses_url = get_courses_url(content)


if __name__ == "__main__":
    main()