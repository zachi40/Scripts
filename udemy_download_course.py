# -*- coding: utf-8 -*-

import os, requests, urlparse, sys ,art, argparse,time, cfscrape, stdiomask
from bs4 import BeautifulSoup
proxies={
    "http":"127.0.0.1:8080",
    "https":"127.0.0.1:8080"
}

__version__ = 1.02
requests.packages.urllib3.disable_warnings()

class udemy_download_course(object):
    def __init__(self,username,password,course_url):
        self.login_popup = "https://www.udemy.com/join/login-popup/?skip_suggest=1&display_type=popup&locale=en_US&next=https://www.udemy.com/mobile/ipad/&ref=&response_type=json&xref=&display_type=popup"
        self.login_url = "https://www.udemy.com/join/login-popup/"
        if not course_url[len(course_url) - 1] == "/":
            self.course_url = course_url + "/"
        else:
            self.course_url=course_url
        self.enrolls = []
        self.COURSE_NAME = ""
        self.COURSE_ID = ""
        self.username = username
        self.password = password
        self.thread_count = 10
        self.ITEMS = []
        self.details = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        self.login_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://www.udemy.com/mobile/ipad/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        self.ACCESS_TOKEN = self.login(username, password)
        self.QUALITY1 = "1080"
        self.QUALITY2 = "720"
        self.QUALITY3 = "460"
        self.QUALITY4 = "320"
        self.QUALITY4 = "240"
        self.max_path = 220

    #login
    def login(self,username, password):
        CSRF_REQUES = cfscrape.create_scraper()
        CSRF_REQUES = CSRF_REQUES.get(self.login_url, headers=self.login_headers)
        CSRF_REQUES.encoding = 'utf-8'
        soup = BeautifulSoup(CSRF_REQUES.text, 'html5lib')
        csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'}).attrs.get(u'value')
        self.login_headers.update({'Cookie': 'csrftoken='+CSRF_REQUES.cookies.get("csrftoken")})
        data = {
            'csrfmiddlewaretoken':csrf,
            'locale':'he_IL',
            'email':username,
            'password':password
        }
        response = requests.post(self.login_popup, data=data, headers=self.login_headers)
        ACCESS_TOKEN= response.cookies.get("access_token")
        if ACCESS_TOKEN == None:
            raise Exception("username or password is incorrect")
        self.headers.update({
            'Authorization': 'Bearer '+ ACCESS_TOKEN,
            'Cookie': 'access_token='+ACCESS_TOKEN
        })
        return ACCESS_TOKEN

    def get_data(self,url):
        # r = requests.get(course_url,headers=headers,proxies=proxies,verify=False)
        return requests.get("https://www.udemy.com/{url}".format(url=url),headers=self.headers)#,proxies=proxies,verify=False)

    #get coures id
    def get_course_id(self, course_url):
        print "[+] Information: getting course id"
        course_page = self.get_data(str(course_url).replace("https://www.udemy.com/",""))
        if course_page.status_code == 403:
            raise Exception('[+] Udemy: Try later')
        elif course_page.status_code == 404:
            raise Exception('[+] Udemy: course not found')
        course_page.encoding = 'utf-8'
        soup = BeautifulSoup(course_page.text, 'html5lib')
        self.COURSE_ID = str(soup.find('a', {'class': 'js-user-tracker-click'}).attrs.get(u'data-user-tracker-object-id'))

    #get name
    def get_course_name(self,id):
        print "[+] Information: getting course name"
        course_name =self.get_data("api-2.0/courses/{id}?fields[course]=title&fields[user]=url".format(id=id)).json()
        self.COURSE_NAME = course_name.get(u'title')

    #get video
    def get_video_files(self,course_id):
        print "[+] Information: getting video files"
        items_requset = self.get_data("api-2.0/course-landing-components/{course_id}/me/?components=curriculum".format(course_id=course_id)).json()

        print "[+] Udemy: found {count} video files in this course".format(count=items_requset.get(u'curriculum').get(u'data').get(u'num_of_published_lectures'))
        if not len((items_requset.get(u'curriculum').get(u'data').get(u'sections')))> 1:
            for item in items_requset.get(u'curriculum').get(u'data').get(u'sections')[0].get(u'items'):
                self.add_items(course_id, item)
                sys.stdout.write('\r[+] loading video files |')
                time.sleep(0.1)
                sys.stdout.write('\r[+] loading video files /')
                time.sleep(0.1)
                sys.stdout.write('\r[+] loading video files -')
                time.sleep(0.1)
                sys.stdout.write('\r[+] loading video files \\')
                time.sleep(0.1)
            sys.stdout.write('\r[+] Done!     ')
        else:
            #with folder
            for folder in items_requset.get(u'curriculum').get(u'data').get(u'sections'):
                for item in folder.get(u'items'):
                    self.add_items(course_id,item,folder)
                    sys.stdout.write('\r[+] loading video files |')
                    time.sleep(0.1)
                    sys.stdout.write('\r[+] loading video files /')
                    time.sleep(0.1)
                    sys.stdout.write('\r[+] loading video files -')
                    time.sleep(0.1)
                    sys.stdout.write('\r[+] loading video files \\')
                    time.sleep(0.1)

            sys.stdout.write('\r[+] Done!     ')

    def download_file(self, index,url,path):
        if len(os.path.dirname(os.path.realpath(__file__))+"\\"+path) > self.max_path:
            list_path= path.split("/")
            ext=list_path[3].split(".")
            path = '{}/{}/{}/{}.{}'.format(list_path[0],list_path[1],list_path[2],index,ext[len(ext)-1])
        with open(path, "wb") as f:
                response = requests.get(url, stream=True)
                print "\n Downloading to {filename}".format(filename=path)
                total_length = response.headers.get('content-length')

                if total_length is None:
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                        sys.stdout.flush()

    def download_html(self,index,path,content):
        html = '<html><head></head><body><div align="center"><div style="max-height: 50%;max-width: 400px;"><h1>{title}</h1>{article}</div></div></body></html>'\
            .format(title=content[0],article=self.cut_filename(content[1]))
        if len(os.path.dirname(os.path.realpath(__file__)) + "\\" + path) > self.max_path:
            list_path= path.split("/")
            ext=list_path[3].split(".")
            path = '{}/{}/{}/{}.{}'.format(list_path[0],list_path[1],list_path[2],index,ext[len(ext)-1])
        print "\n Downloading to {filename}.html".format(filename=path)
        with open(path, "wb") as f:
            f.write(html)
            f.close()
        print "[==================================================]"

    def download_url(self,index,path,target):
        if len(os.path.dirname(os.path.realpath(__file__)) + "\\" + path) > self.max_path:
            list_path= path.split("/")
            ext=list_path[3].split(".")
            path = '{}/{}/{}/{}.{}'.format(list_path[0],list_path[1],list_path[2],index,ext[len(ext)-1])
        print "\n Downloading to {filename}.url".format(filename=path)
        with open(path, "wb") as f:
            f.write('[InternetShortcut]\n')
            f.write('URL=%s' % target)
            f.close()
        print "[==================================================]"


    def cut_filename(self, string):
        clearString=string.encode('ascii', 'ignore')
        return str(clearString).replace(":", "").replace("*", "").replace("/","_").replace("?","")

    def download_conntent(self):
        directory = str(self.COURSE_NAME).replace("/"," ").replace(":","")
        if not os.path.exists(directory):
            os.makedirs(directory)
        for item in self.ITEMS:
            if item.get(u'folder'):
                directory_path='{course_name}/{folder_index}. {subject}'.format(course_name=directory,
                                                                                subject=self.cut_filename(item.get(u'folder')),
                                                                                folder_index=item.get(u'index_folder'))
                filename = '{index}. {title}'.format(index=item.get(u'index'), title=self.cut_filename(item.get('title')))
                path = ('{path}/{file}'.format(path=directory_path, file=filename))
                if not os.path.exists(path):
                    os.makedirs(path)
            else:
                filename = '{index}. {title}'.format(index=item.get(u'index'),title=item.get('title'))
                path='{path}/{file}'.format(path=directory, file = filename)
                print "\n\n[+] Downloading: {}".format(filename)
                if not os.path.exists(path):
                    os.makedirs(path)

            #download vtt
            if not len(item.get(u'vtt')) == 0:
                for vttFile in item.get(u'vtt'):
                    self.download_file(item.get(u'index'),vttFile.get(u'url'),"{path}/{filename}".format
                    (path=path,filename=self.cut_filename(vttFile.get('title')).replace(".vtt","_{lang}.vtt".format(lang=vttFile.get(u'lang')))))
            if not len(item.get(u'article')) == 0:
                for i in item.get(u'article'):
                    self.download_html(item.get(u'index'),"{path}/{filename}.html".format(path=path,filename=self.cut_filename(item.get('title'))),
                                       (item.get('title'),i.get(u'body')))

            if not len(item.get(u'shortcut_url')) == 0:
                for url in item.get(u'shortcut_url'):
                    self.download_url(item.get(u'index'),"{path}/{filename}.url".format(path=path,filename=
                    self.cut_filename(url.get('title'))))

            if not len(item.get(u'files')) == 0:
                for file in item.get(u'files'):
                    self.download_file(item.get(u'index'),file.get(u'url'),"{path}/{filename}"
                                       .format(path=path, filename= self.cut_filename(file.get('title'))))

            # download video
            if not len(item.get(u'video')) == 0:
                if str(item.get(u'video')[0].get(u'quality')) == self.QUALITY1 or str(item.get(u'video')[0].get(u'quality')) == self.QUALITY2:
                    self.download_file(item.get(u'index'),item.get(u'video')[0].get(u'url'),
                                       "{path}/{filename}.mp4".format(path=path, filename=self.cut_filename(item.get(u'video')[0].get('title'))))
                elif str(item.get(u'video')[1].get(u'quality')) == self.QUALITY1 or str(item.get(u'video')[1].get(u'quality')) == self.QUALITY2:
                    self.download_file(item.get(u'index'), item.get(u'video')[1].get(u'url'),
                                       "{path}/{filename}.mp4".format(path=path, filename=self.cut_filename(item.get(u'video')[1].get('title'))))
                elif str(item.get(u'video')[2].get(u'quality')) == self.QUALITY1 or str(item.get(u'video')[2].get(u'quality')) == self.QUALITY2:
                    self.download_file(item.get(u'index'), item.get(u'video')[2].get(u'url'),
                                      "{path}/{filename}.mp4".format(path=path,filename= self.cut_filename(item.get(u'video')[2].get('title'))))
                elif str(item.get(u'video')[3].get(u'quality')) == self.QUALITY1 or str(item.get(u'video')[3].get(u'quality')) == self.QUALITY2:
                    self.download_file(item.get(u'index'), item.get(u'video')[3].get(u'url'),
                                       "{path}/{filename}.mp4".format(path=path, filename=self.cut_filename(item.get(u'video')[3].get('title'))))
                else:
                    self.download_file(item.get(u'index'), item.get(u'video')[0].get(u'url'),
                                       "{path}/{filename}.mp4".format(path=path, filename=self.cut_filename(item.get(u'video')[0].get('title'))))


    def add_items(self,course_id,item,folder=False):
        article = []
        shortcut_url = []
        video_files = []
        files = []
        vtt = []

        for lecture in self.details:
            if item.get(u'id') == lecture.get(u'id'):
                if str(lecture.get(u'asset').get(u'asset_type')) =="Video":
                    asset_type_requset=self.get_data("api-2.0/users/me/subscribed-courses/{course_id}/lectures/"
                                                     "{item}?fields[lecture]=asset&fields[asset]=stream_urls,captions"
                                                     .format(course_id=course_id, item=item.get(u'id'))).json()
                    asset_type_requset = asset_type_requset[u'asset']
                    for vttfile in asset_type_requset.get(u'captions'):
                        vtt.append({'url': vttfile.get(u'url'), 'lang': vttfile.get(u'video_label').strip(" [Auto]"),
                                    'title':vttfile.get(u'title').replace(".autogenerated","").encode('ascii', 'ignore')
                                    })
                    for video in asset_type_requset.get(u'stream_urls').get(u'Video'):
                        video_files.append({'url': video.get(u'file'), 'quality': video.get(u'label'),
                                            'title':lecture.get(u'title').encode('ascii', 'ignore')})
                if str(lecture.get(u'asset').get(u'asset_type')) == "Article":
                    article_requset = self.get_data(
                        "api-2.0/assets/{item}?fields[asset]=body".format(item=lecture.get(u'asset').get(u'id'))).json()
                    article.append({'body': article_requset.get(u'body').encode('ascii', 'ignore')})
                if len(lecture.get(u'supplementary_assets'))> 0:
                    for supplementary_assets in lecture.get(u'supplementary_assets'):
                        if str(supplementary_assets.get(u'asset_type')) == "File":
                            files_requset = self.get_data(
                                "api-2.0/users/me/subscribed-courses/{course_id}/lectures/{item}/supplementary-assets/{fileid}"
                                "?fields[asset]=download_urls".format(course_id=course_id, item=item.get(u'id'),
                                                                      fileid=supplementary_assets.get(u'id'))).json()
                            files.append({'url': files_requset.get(u'download_urls').get(u'File')[0].get(u'file'),
                                          'title': supplementary_assets.get(u'title').encode('ascii', 'ignore')})
                        if str(supplementary_assets.get(u'asset_type')) == "ExternalLink":
                                shortcut_url.append({'url': supplementary_assets.get(u'external_url'),
                                                     'title': supplementary_assets.get(u'title').encode('ascii', 'ignore')})
                if folder:
                    self.ITEMS.append({'index': item.get(u'object_index'),
                              'title': (item.get(u'title')).encode('ascii', 'ignore'),
                              'id': item.get(u'id'),
                              'video': video_files,
                              'vtt': vtt,
                              'article':article,
                              'shortcut_url':shortcut_url,
                              'files': files,
                              'folder': folder.get(u'title'),
                              'index_folder': folder.get(u'index')
                              })
                else:
                    self.ITEMS.append({'index': item.get(u'object_index'),
                                   'title': (item.get(u'title')).encode('ascii', 'ignore'),
                                   'id': item.get(u'id'),
                                  'video': video_files,
                                  'article': article,
                                  'shortcut_url': shortcut_url,
                                  'vtt': vtt,
                                  'files': files
                                  })
                break

    def check_enrool(self):
        NEXTPAGE=True
        print "[+] Udemy: Check enrolls courses"
        enroll_id = self.get_data("api-2.0/users/me/subscribed-courses?fields[course]=id,title").json()
        for enroll in enroll_id.get(u'results'):
             self.enrolls.append({
                 'id':enroll.get(u'id'),
                 'title':enroll.get(u'title')
             })
        while(NEXTPAGE):
            if enroll_id.get(u'next'):
                enroll_id = requests.get(enroll_id.get(u'next'),headers=self.headers, verify=False).json()
                for enroll in enroll_id.get(u'results'):
                    self.enrolls.append({
                        'id': enroll.get(u'id'),
                        'title':enroll.get(u'title')
                    })
            else:
                NEXTPAGE=False
                break
        for value in self.enrolls:
            if str(value.get(u'id')) == self.COURSE_ID:
                return True
        print "[+] Udemy: you are not enroll this course"
        exit(0)

    def get_courses_details(self,id):
        get_courses_requset = self.get_data("api-2.0/courses/{id}/subscriber-curriculum-items/?page_size=1400&fields[lecture]="
                                            "title,object_index,is_published,sort_order,created,asset,supplementary_assets,last_watched_second,"
                                            "is_free&fields[chapter]=title,object_index,is_published,sort_order&fields[asset]=title,filename,"
                                            "asset_type,external_url,status,time_estimation".format(id=id)).json()
        for lecture in get_courses_requset.get(u'results'):
            if str(lecture.get(u'_class')) == "lecture":
                self.details.append(lecture)


    def main(self):
        self.get_course_id(self.course_url)
        self.check_enrool()
        self.get_course_name(self.COURSE_ID)
        self.get_courses_details(self.COURSE_ID)
        self.get_video_files(self.COURSE_ID)
        self.download_conntent()

def main():
    print art.text2art("TzuhiScript", font="random")
    time.sleep(1)
    version = "{version}".format(version=__version__)
    description = 'A cross-platform python based utility to download courses from udemy for personal offline use.'

    parser = argparse.ArgumentParser(description=description, conflict_handler="resolve")
    parser.add_argument('course_url', help="Udemy course.", type=str, default="https://#")
    authentication = parser.add_argument_group("Authentication")
    authentication.add_argument('-u', '--username', dest='username', type=str, help="Username in udemy.")
    authentication.add_argument('-p', '--password', dest='password', type=str, help="Password of your account.")
    general = parser.add_argument_group("General")
    general.add_argument('-h', '--help', action='help', help="Shows the help.")
    general.add_argument('-v', '--version',action='version', version=version,help="Shows the version.")
    options = parser.parse_args()
    if not options.username and not options.password:
        email = raw_input("Username: ")
        password = stdiomask.getpass("Password: ")
        udemy = udemy_download_course(email, password, options.course_url)
        udemy.main()
    else:
        udemy = udemy_download_course(options.username, options.password, options.course_url)
        udemy.main()

if __name__ == '__main__':
    main()
