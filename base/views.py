from typing import Any

from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.db.models import Q

from .forms import RoomForm
from .models import Room, Topic


# Create your views here.
# rooms = [
#     {'id': 1, "name": "Let's learn Python together!"},
#     {'id': 2, "name": "Let's learn JavaScript together!"},
#     {'id': 3, "name": "Let's learn C# together!"},
# ]


def home(request):
    q = request.GET.get('q') \
        if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room_table: QuerySet[Room] = Room.objects.get(id=pk)
    context = {'room': room_table}
    return render(request, 'base/room.html', context)


def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context: dict[Any, Any] = {'form': form}
    return render(request, 'base/room_form.html', context)


def updateRoom(request, pk):
    update_room = Room.objects.get(id=pk)
    form = RoomForm(instance=update_room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=update_room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    delete_room = Room.objects.get(id=pk)
    if request.method == "POST":
        delete_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', dict(obj=delete_room))