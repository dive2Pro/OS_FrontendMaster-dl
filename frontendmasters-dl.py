import click
from extractor.spider import Spider

@click.command()
@click.option('--id', prompt='Username', help='Frontend Master Username')
@click.option('--password', prompt='Password', help='Frontend Master Password')
@click.option('--mute-audio', help='Mute Frontend Master browser tab', is_flag=True)
@click.option('--high-resolution', help='Download high resolution videos', is_flag=True)
@click.option('--video-per-video', help='Download one video at a time', is_flag=True)
@click.option('--all-courses', help='Download all of courses', is_flag=True)
@click.option('--course-name', help='Download specific category video ')
def downloader(id, password, mute_audio, high_resolution, video_per_video, all_courses, course_name):
    spider = Spider(mute_audio)
    click.secho('>>> Login with your credential', fg='green')
    spider.login(id, password)
    if all_courses :
        click.secho('>>> Downloading all of courses', fg='red')
        spider.download_all_courses(mute_audio, high_resolution, video_per_video, course_name)
        return
    course = click.prompt('Course Id')
    click.secho('>>> Downloading course: ' + course, fg='green')
    spider.download(course, high_resolution, video_per_video)
    click.secho('>>> Download Completed! Thanks for using frontendmasters-dl', fg='green')

# TODO: (Xinyang) Switching to setuptools
#   http://click.pocoo.org/5/quickstart/#switching-to-setuptools
if __name__ == '__main__':
    downloader()
