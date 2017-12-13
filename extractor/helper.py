import os
import os.path
import string
import requests
import re
from urllib2 import urlopen, URLError, HTTPError

import re


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

#
# courses_names = [{'name': 'Complete Intro to React, v3 (feat. Redux, Router & Flow)'},
#                  {'name': 'Testing JavaScript Applications (feat. React and Redux)'},
#                  {'name': 'Advanced State Management in React (feat. Redux and MobX)'},
#                  {'name': "Reactive Angular 2"}
#                  ]
# names = sorted(courses_names , key=lambda n : n['name'], cmp=lambda a,b)
# names = filter(lambda x: findWholeWord('React')(x['name']), courses_names)
# print(names)

def format_filename(filename_str):
    s = filename_str
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename

def get_file_path_from_url(url):
    return url.split("?")[0].split(".")[-1]

def download_file(url, path, self):
    # FIXME(Xinyang): Better exception handling for empty url
    if url is None:
        raise AttributeError("Url is empty")
    if len(url) <= 1:
        raise AttributeError("Url is empty")
    print('Download_file start : ', url, path )
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        temporaryURL = self.browser.current_url
        # self.browser.get(url)
        # self.browser.back()
        r = requests.get(url, stream=True)
        print("Downloading: %s" % (path))
        with open(path, 'wb') as local_file:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    local_file.write(chunk)
                    local_file.flush()
                    os.fsync(local_file.fileno())
            local_file.close()


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
