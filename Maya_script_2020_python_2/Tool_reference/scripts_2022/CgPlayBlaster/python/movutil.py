import json
import datetime
import os

ffprobe = os.path.normpath(os.path.join(get_program_dir(), 'ffprobe.exe'))
ffmpeg = os.path.normpath(os.path.join(get_program_dir(), 'ffmpeg.exe'))

def get_program_dir():
    py_dir = os.path.dirname(__file__)
    app_dir = os.path.dirname(py_dir)
    return os.path.normpath(os.path.join(app_dir, 'ExtraProgram'))
    
def get_time_code(frame, fps=24):
    sec = frame / fps
    frameless = (float(frame) / fps - sec) * fps
    mpf = float(1000) / fps
    msec = int(frameless * mpf)

    if msec:
        time_code = '%s.%s' % (datetime.timedelta(seconds=sec), msec)
    else:
        time_code = '%s' % (datetime.timedelta(seconds=sec))
    return time_code

def get_movie_info(movie_file_path):
    cmd = '"%s" -v quiet -show_streams -show_format -print_format json "%s"' % (ffprobe, movie_file_path)
    p = sp.Popen(cmd, shell=True, stdout=sp.PIPE)
    probe = json.loads(p.stdout.read())
    return probe
