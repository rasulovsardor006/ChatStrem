from django.shortcuts import render

def video_chat(request):
    return render(request, 'chat/video_chat.html')