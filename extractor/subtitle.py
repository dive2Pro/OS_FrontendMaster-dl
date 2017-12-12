import requests
import os
import json
from helper import format_filename
TRANSCRIPTS_PATH = 'https://api.frontendmasters.com/v1/kabuki/transcripts/'
def download_subtitles(couses, self):
    if couses is None:
        return
    if not couses.has_key('slug') :
        return
    title = couses['slug']
    download_path = self.create_download_directory()
    course_path = self.create_course_directory(download_path, title)
    data_json = os.path.join(course_path, 'index.json')
    with open(data_json, 'wb') as out_file:
        json.dump(couses, out_file)
    for lesson_data in couses['lessonData']:
        lesson_title = lesson_data['title']
        stats_id = lesson_data['statsId']
        if stats_id is None:
            continue
        path = os.path.join(course_path, format_filename(lesson_title) + ".vtt")
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            print("Downloading subtitle of {0}/{1}".format(format_filename(lesson_title), path))
            lesson_transcript_api = TRANSCRIPTS_PATH + stats_id + ".vtt"
            data = requests.get(lesson_transcript_api)
            if data is None:
                continue
            with open(path, 'wb') as local_file:
                local_file.writelines(data.iter_lines())
