from bs4                             import BeautifulSoup
from selenium                        import webdriver
from selenium.webdriver.common.keys  import Keys
from urllib2                         import urlopen, URLError, HTTPError
from helper                          import *
from subtitle import download_subtitles
import httplib
import cookielib
import json
import mechanize
import os
import time
import click

# Constants
DATA_COURSE_LIST              = './DATA_COURSE_LIST.json'
DATA_COURSE_DETAILED_LIST_CDN = './DATA_COURSE_DETAILED_LIST_CDN.json'
URL_LOG_IN                    = 'https://frontendmasters.com/login/'
URL_COURSE_LIST               = 'https://frontendmasters.com/courses/'
URL_TRANSLATIONS              = 'https://api.frontendmasters.com/v1/kabuki/courses/'
class Spider(object):
    def __init__(self, mute_audio):
        options = webdriver.ChromeOptions()

        if mute_audio:
            options.add_argument("--mute-audio")

        self.browser = webdriver.Chrome(chrome_options=options)

    def login(self, id, password):
        self.browser.get(URL_LOG_IN)
        time.sleep(2)

        username_field = self.browser.find_element_by_id('username')
        password_field = self.browser.find_element_by_id('password')

        username_field.send_keys(id)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

    def download(self, course, high_resolution, video_per_video, has_sub_title=True):
        # if has_sub_title:

        # Get detailed course list
        course_detailed_list = self._get_detailed_course_list(course)
        # Get subtitles
        # download_subtitle(course, self)
        # Get downloadable CDN
        course_downloadbale = self._get_downloadable_links(course_detailed_list, high_resolution, video_per_video)
        # Download course videos
        if not video_per_video:
            self.download_course(course_downloadbale)

        # self.browser.close()

    def download_all_courses(self, mute_audio, high_resolution, video_per_video, course_name ):
        # now we are in cours page
        # find all courses id
        courses = self._get_courses_data()
        # spider download course (video_per_video)
        # courses = sorted(courses, key=lambda c: c['meta'][0:2])
        if course_name:
            courses = filter(lambda x: findWholeWord(course_name)(x['title']), courses)
        # print(courses, ' ---- ')
        for course in courses :
            id = course['id']
            has_sub_title = course['has_sub_title']
            self.download(id, high_resolution, video_per_video , has_sub_title)
        click.secho('>>> Downloading all of courses  are finished <<<', fg='red')

    def _get_courses_data(self):
        courses = []
        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        items = soup_page.find('ul', {'class': 'MediaList'}).find_all('li', {'class': 'MediaItem s-vflex'})
        for index, item in enumerate(items, start= 0):
            course_item = {
                'id':None,
                'meta':None,
                'title': None,
                'has_sub_title': False
            }
            course_item['title'] = item.find('h2', {'class': 'title'}).find('a', {}).get_text("|", strip=True)
            meta = item.find('div', {'class': 'meta'})
            course_item['has_sub_title'] = meta.find('strong') is not None
            course_item['meta'] = meta.get_text("|", strip=True)
            course_item['id'] = item['id']
            courses.append(course_item)
        return courses
    def download_subtitles(self, course):
        click.secho('>>> Downloading course subtitles', fg='green')
        course_link = URL_TRANSLATIONS + course
        self.browser.get(course_link)
        self.browser.implicitly_wait(4)
        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        data = soup_page.find('pre').getText()
        download_subtitles(json.loads(data), self)


    def _get_detailed_course_list(self, course):
        course_link = URL_COURSE_LIST + course + '/'
        course_detial = {
            'title': course,
            'url': course_link,
            'sections': []
        }

        self.browser.get(course_link)
        self.browser.implicitly_wait(4)
        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')

        # Find video nav list
        sections = soup_page.find('section', {'class': 'CourseToc'})
        sections_items = sections.find_all(
            'ul', {'class': 'LessonList'}
        )

        sections = self._get_section_data(sections_items)
        # is like this {'subsections': [{'url': u'/courses/complete-intro-react/introduction/', 'downloadable_url': None, 'title': u'Introduction'},...]}
        course_detial['sections'].extend(sections)

        return course_detial

    def _get_section_data(self, sections_items):
        sections = []

        soup_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        titles = soup_page.find('section', {'class': 'CourseToc'}).find_all('h3', {'class', 'lessongroup'})

        for index, item in enumerate(sections_items, start=0):
            # Course section data structure
            course_section = {
                'title': None,
                'subsections': []
            }

            course_section['title'] = titles[index].getText()

            videos_section = item
            videos_section_items = videos_section.find_all('li')

            videos_data = self._get_videos_data(videos_section_items)
            course_section['subsections'].extend(videos_data)

            sections.append(course_section)

        return sections

    def _get_videos_data(self, videos_section_items):
        subsections = []

        for video in videos_section_items:
            # Course subsection data structure
            course_subsection = {
                'title': None,
                'url': None,
                'downloadable_url': None
            }
            course_subsection['url'] = video.find('a')['href']
            title = video.find('a').find(
                'div', {'class', 'heading'}
            ).find(
                'h3', { }
            ).getText()

            course_subsection['title'] = format_filename(title)
            subsections.append(course_subsection)

        return subsections

    def _get_downloadable_links(self, course, high_resolution, video_per_video):
        # course data structure
        # {
        #     'title': course,
        #     'url': course_link,
        #     'sections': []
        # }

        url = course['url']
        if video_per_video:
            title = course['title']
            download_path = self.create_download_directory()
            course_path = self.create_course_directory(download_path, title)
        index = 0
        for i1, section in enumerate(course['sections']):
            section_title = section['title']

            for i2, subsection in enumerate(section['subsections']):
                if subsection['downloadable_url'] is None:
                    # print("Downloading infomations  are {0} ------- {1} ---------- {2}: ".format(course, section, subsection))
                    print("Retriving: {0}/{1}/{2}".format(
                        format_filename(course['title']),
                        format_filename(section['title']),
                        format_filename(subsection['title'])))

                    video_url = 'https://frontendmasters.com' + subsection['url']
                    self.browser.get(video_url)
                    time.sleep(8)

                    if high_resolution:
                        resolution_button = self.browser.find_element_by_class_name("fm-vjs-quality")
                        resolution_button.click()

                        high_resolution_text = resolution_button.find_element_by_tag_name("li")
                        high_resolution_text.click()
                        time.sleep(3)

                    url_str = self._get_video_source()
                    print("Video URL: {0}".format(url_str))
                    subsection['downloadable_url'] = url_str
                    if video_per_video:
                        self.download_video(index, subsection, section_title, course_path)
                        index += 1

        return course

    def _get_video_source(self):
        try:
            video_tag = self.browser.find_element_by_tag_name('video')
            source_link = video_tag.get_attribute('src')
            return source_link
        except:
            return "http://placehold.it/500x500"

    def create_download_directory(self):
        download_path = os.path.join(os.path.curdir, 'Download')
        create_path(download_path)
        return download_path

    def create_course_directory(self, download_path, title):
        course_path = os.path.join(download_path, title)
        create_path(course_path)
        return course_path

    def download_course(self, course):
        title = course['title']
        download_path = self.create_download_directory()
        course_path = self.create_course_directory(download_path, title)
        click.secho('>>> Downloading  {0}  start <<<'.format(title), fg='red')
        index = 0
        for i1, section in enumerate(course['sections']):
            section_title = section['title']
            for i2, subsection in enumerate(section['subsections']):
                self.download_video(index, subsection, section_title, course_path)
                index += 1
        click.secho('>>> Downloading  {0}  end <<<'.format(title), fg='red')

    def download_video(self, index, subsection, section_title, course_path):
        subsection_title = subsection['title']
        print("Downloading: {0}".format(
            format_filename(subsection_title)))

        filename = str(index) + '-' + format_filename(
            section_title) + '-' + format_filename(
            subsection_title) + '.' + get_file_path_from_url(subsection['downloadable_url'])

        file_path = os.path.join(course_path, format_filename(filename))

        download_file(subsection['downloadable_url'], file_path, self)
