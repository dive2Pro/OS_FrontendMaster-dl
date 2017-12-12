import os
import os.path
import string
import requests
from urllib2 import urlopen, URLError, HTTPError

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
        return
    if len(url) <= 1:
        return
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
