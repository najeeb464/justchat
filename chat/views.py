from django.shortcuts import render
import json
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    return render(request, 'chat/index.html')

# def room(request, room_name):
#     return render(request, 'chat/room.html', {
#         "room_name":room_name
#         # 'room_name':mark_safe(json.dumps(room_name))
#     })

@login_required
def room(request, room_name):
    print("in room view")
    return render(request, 'chat/room.html', {
        "room_name":mark_safe(json.dumps(room_name)),
        "username":mark_safe(json.dumps(request.user.username))
    })