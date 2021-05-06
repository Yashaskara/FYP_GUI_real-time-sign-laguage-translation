
"""
https://github.com/FrederikSchorr/sign-language
This module
* launches the webcam,
* waits for the start signal from user,
* captures 5 seconds of video,
* extracts frames from the video
* calculates and displays the optical flow,
* and uses the neural network to predict the sign language gesture.
* Then start again.
"""

# import the necessary packages
import time
import os
import glob
import sys
import random

import numpy as np
import pandas as pd

import cv2

from timer import Timer
from frame import video2frames, images_normalize, frames_downsample, images_crop
from frame import images_resize_aspectratio, frames_show, frames2files, files2frames, get_length
from videocapture import video_start, frame_show, video_show, video_capture
from opticalflow import frames2flows, flows2colorimages, flows2file, flows_add_third_channel
from datagenerator import VideoClasses
from model_mobile import features_2D_load_model
from model_lstm import lstm_load
from model_i3d import I3D_load
from predict import probability2label
from google_trans_new import google_translator
from gtts import gTTS

import io
from playsound import playsound
from io import BytesIO
import io
import time

import pyglet
from gtts import gTTS


pyglet.options["audio"] = ("directsound",)

def speak(words: str, lang: str="kn"):
    with io.BytesIO() as f:
        gTTS(text=words, lang=lang).write_to_fp(f)
        f.seek(0)

        player = pyglet.media.load('.mp3', file=f).play()
        while player.playing:
            pyglet.app.platform_event_loop.dispatch_posted_events()
            pyglet.clock.tick()

# def speak(my_text):
#     with io.BytesIO() as f:
#         gTTS(text=my_text, lang='kn').write_to_fp(f)
#         f.seek(0)
#         return Audio(f.read(), autoplay=True)
import video_converter
import subprocess

import ffmpeg
def livedemo():
    # print("HERE")
    # ffmpeg_path = "E:\\ffmpeg_real\\ffmpeg-n4.4-10-g75c3969292-win64-gpl-4.4\\bin\\"
    # video_path = 'D:\\GUI_videos\\'
    # output_path = 'D:\\GUI_videos_for_predict\\'
    # #testvar = os.listdir(video_path)
    # try:
    #     for videos in os.listdir(video_path):
    #         print(videos)
    #         try:
    #             print("HERE")
    #             command = f'{ffmpeg_path}ffmpeg.exe -i {video_path + videos} {output_path + videos[:-5]}.mp4'
    #
    #             subprocess.run(command)
    #         except Exception as e:
    #             print(e)
    # except Exception as e:
    #     print(e)

    '''
        try:
            # for videos in os.listdir(video_path):
                stream = ffmpeg.input(video_path)
                stream1 = ffmpeg.output(stream, output_path)
                ffmpeg.run(stream1)
        except Exception as e:
            print(e)
        '''
    '''
        # video_path = "D:\\FINAL PROJECT\\GUI Videos\\"
        # output_path = "D:\\FINAL PROJECT\\GUI_videos_for_predict\\"
        # print("here")
        # for videos in os.listdir(video_path):
        #     videoConverter_instance = video_converter.VideoConverter(video_file=videos,
        #                                                              output_dir=output_path,
        #                                                              formats='mp4')
        #     videoConverter_instance.convert_video()
        # print("Completed conversion")
        # dataset
        '''
    diVideoSet = {"sName": "ISL_sign",
                  "nClasses": 89,  # number of classes
                  "nFramesNorm": 40,  # number of frames per video
                  "nMinDim": 240,  # smaller dimension of saved video-frames
                  "tuShape": (240, 320),  # height, width
                  "nFpsAvg": 10,
                  "nFramesAvg": 50,
                  "fDurationAvg": 5.0}  # seconds

    # files
    #sClassFile = "class.csv"  # %(diVideoSet["sName"], diVideoSet["nClasses"])
    sClassFile = "D:\\FINAL PROJECT\\GUI\\data-set\\ISA_sign\\089\\class.csv"

    #sVideoDir = "data-set/%s/%03d" % (diVideoSet["sName"], diVideoSet["nClasses"])

    print("\nStarting gesture recognition live demo ... ")
    print(os.getcwd())
    print(diVideoSet)

    # load label description
    oClasses = VideoClasses(sClassFile)

    #sModelFile = "model/20210318-1839-ISL_sign089-oflow-i3d-entire-best.h5"
    sModelFile = "D:\\FINAL PROJECT\\GUI\\model\\20210318-1839-ISL_sign089-oflow-i3d-entire-best.h5"

    h, w = 224, 224
    keI3D = I3D_load(sModelFile, diVideoSet["nFramesNorm"], (h, w, 2), oClasses.nClasses)

    # open a pointer to the webcam video stream
    oStream = video_start(device=1, tuResolution=(320, 240), nFramePerSecond=diVideoSet["nFpsAvg"])

    # liVideosDebug = glob.glob(sVideoDir + "/train/*/*.*")
    nCount = 0
    sResults = ""
    timer = Timer()

    # loop over action states
    while True:
        # show live video and wait for key stroke
        key = video_show(oStream, "green", "Press <blank> to start", sResults, tuRectangle=(h, w))

        # start!
        if key == ord(' '):
            # countdown n sec
            video_show(oStream, "orange", "Recording starts in ", tuRectangle=(h, w), nCountdown=3)

            # record video for n sec
            fElapsed, arFrames, _ = video_capture(oStream, "red", "Recording ", \
                                                  tuRectangle=(h, w), nTimeDuration=int(diVideoSet["fDurationAvg"]),
                                                  bOpticalFlow=False)
            print("\nCaptured video: %.1f sec, %s, %.1f fps" % \
                  (fElapsed, str(arFrames.shape), len(arFrames) / fElapsed))

            # show orange wait box
            frame_show(oStream, "orange", "Translating sign ...", tuRectangle=(h, w))

            # crop and downsample frames
            arFrames = images_crop(arFrames, h, w)
            arFrames = frames_downsample(arFrames, diVideoSet["nFramesNorm"])

            # Translate frames to flows - these are already scaled between [-1.0, 1.0]
            print("Calculate optical flow on %d frames ..." % len(arFrames))
            timer.start()
            arFlows = frames2flows(arFrames, bThirdChannel=False, bShow=True)
            print("Optical flow per frame: %.3f" % (timer.stop() / len(arFrames)))

            # predict video from flows
            print("Predict video with %s ..." % (keI3D.name))
            arX = np.expand_dims(arFlows, axis=0)
            arProbas = keI3D.predict(arX, verbose=1)[0]
            nLabel, sLabel, fProba = probability2label(arProbas, oClasses, nTop=3)
            translator = google_translator()
            translate_text = translator.translate(sLabel, lang_tgt='kn')
            mytext = translate_text
            # language = 'kn'
            # myobj = gTTS(text=mytext, lang=language, slow=False)

            # mp3_fp = BytesIO()
            # myobj.write_to_fp(mp3_fp)

            # myobj.save("output.mp3")
            # os.system("start output.mp3")

            #print(speak(mytext))

            sResults = "Sign: %s (%.0f%%)" % (sLabel, fProba * 100.)
            print(sResults)
            nCount += 1

        # quit
        elif key == ord('q'):
            break

        if nCount:
            break
    # do a bit of cleanup
    oStream.release()
    cv2.destroyAllWindows()
    speak(mytext, 'kn')
    return sResults


'''
if __name__ == '__main__':
    livedemo()
'''