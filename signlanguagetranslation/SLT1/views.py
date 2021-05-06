from django.shortcuts import render
from django.http import HttpResponse

import sys



sys.path.insert(0, 'D:\\FINAL PROJECT\\GUI\\')

from livedemo import livedemo
from livedemo_withSpeech import livedemo
# Create your views here.
def welcome(response):
    return render(response, "SLT1/base.html", {})

def live_video(response):
    return render(response, "SLT1/liveVideo.html")

def translate(response):
    word = livedemo()
    #word = "IN progress"
    return render(response, "SLT1/translate.html", {"word" : word})
