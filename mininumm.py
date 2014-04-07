from PIL import Image
import numpy as np
import subprocess
import re

FFMPEG = "ffmpeg"

def video_info(path):
    cmd = [FFMPEG, '-i', path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    out = {}

    # eg.:
    # Duration: 01:37:20.86, start: 0.000000, bitrate: 5465 kb/s
    #   Stream #0.0(eng): Video: h264 (Main), yuv420p, 1280x720, 2502 kb/s, 21.60 fps, 25 tbr, 3k tbn, 6k tbc

    dur_match = re.search(r'Duration: (\d\d):(\d\d):(\d\d).(\d\d)', stderr)

    if dur_match:
        h, m, s, ms = [int(x) for x in dur_match.groups()]
        out["duration"] = s + ms/100.0 + 60*(m + 60*h)
    else:
        out["duration"] = None

    wh_match = re.search(r'Stream .*[^\d](\d\d+)x(\d\d+)[^\d]', stderr)
    w,h = [int(x) for x in wh_match.groups()]
    out["width"] = w
    out["height"] = h

    return out

def video_frames(path, height=240, width=None, fps=30, colororder='rgb', bitrate='24'):
    def div4(i):
        return 4*int(i/4.0)

    if width is None or height is None:
        # compute aspect ratio
        info = video_info(path)
        if width is None and height is None:
            width = info["width"]
            height = info["height"]
        elif width is None:
            width = div4(height * (info["width"] / float(info["height"])))
        else:
            height = div4(width * (info["height"] / float(info["width"])))

    cmd = [FFMPEG, '-i', path, 
           '-vf', 'scale=%d:%d'%(width,height),
           '-r', str(fps),
           '-an',
           '-vcodec', 'rawvideo', '-f', 'rawvideo',
           '-pix_fmt', '%s%s' % (colororder, bitrate),
           '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        arr = np.fromstring(p.stdout.read(width*height*3), dtype=np.uint8)
        if len(arr) == 0:
            p.wait()
            return
            
        yield arr.reshape((height, width, 3))

def frame_writer(first_frame, path, fps=30, ffopts=[]):
    fr = first_frame
    cmd =[FFMPEG, '-y', '-s', '%dx%d' % (fr.shape[1], fr.shape[0]),
          '-r', str(fps), 
          '-an',
          '-pix_fmt', 'rgb24',
          '-vcodec', 'rawvideo', '-f', 'rawvideo', 
          '-i', '-'] + ffopts + [path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    return p

def frames_to_video(generator, path, fps=30, ffopts=[]):
    p = None 
    for fr in generator:
        if p is None:
            p = frame_writer(fr, path, fps, ffopts)
        p.stdin.write(fr.tostring())
    p.stdin.close()
    print('done generating video')
    p.wait()

def np2video(np, path, fps=30, ffopts=[]):
    def vgen():
        for fr in np:
            yield fr
    return frames_to_video(vgen(), path, fps, ffopts)

def np2image(np, path):
    "Save an image array to a file."
    im = Image.fromstring(
        'RGB', (np.shape[1], np.shape[0]), np.tostring())
    im.save(path)

def sound_chunks(path, chunksize=2048, R=44100, nchannels=2):
    # XXX: endianness EEK
    # TODO: detect platform endianness & adjust ffmpeg params accordingly
    cmd = [FFMPEG, '-i', path, '-vn', '-ar', str(R), '-ac', str(nchannels), '-f', 's16le', '-acodec', 'pcm_s16le', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    frsize = 2*nchannels*chunksize

    while True:
        out = np.fromstring(p.stdout.read(frsize), dtype=np.int16).reshape((-1,nchannels))
        yield out

        if len(out) < chunksize:
            return

def sound2np(path, **kw):
    """
    Load audio data from a file.
    """
    return np.concatenate([x for x in sound_chunks(path, **kw)])

def chunk_writer(first_chunk, path, R=44100, ffopts=[]):
    nchannels = len(first_chunk.shape)
    cmd =[FFMPEG, '-y',
          '-vn',
          '-ar', str(R),
          '-ac', str(nchannels),
          '-acodec', 'pcm_s16le',
          '-f', 's16le',
          '-i', '-'] + ffopts + [path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    return p

def chunks_to_sound(generator, *a, **kw):
    p = None 
    for ch in generator:
        if p is None:
            p = chunk_writer(ch, *a, **kw)
        p.stdin.write(ch.tostring())
    p.stdin.close()
    print('done generating sound')
    p.wait()

def np2sound(np, *a, **kw):
    def agen():
        rest = np
        while len(rest) > 0:
            yield rest[:2048]
            rest = rest[2048:]
    return chunks_to_sound(agen(), *a, **kw)
