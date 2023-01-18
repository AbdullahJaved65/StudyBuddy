from typing import Any

from django.db.models import QuerySet
from django.shortcuts import render, redirect

from .forms import RoomForm
from .models import Room


# Create your views here.
# rooms = [
#     {'id': 1, "name": "Let's learn Python together!"},
#     {'id': 2, "name": "Let's learn JavaScript together!"},
#     {'id': 3, "name": "Let's learn C# together!"},
# ]


def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
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
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', dict(obj=room))
