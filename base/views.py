from typing import Any
from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.db.models import Q
from django.db.models import QuerySet

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .forms import RoomForm
from .models import Room, Topic


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User Does not Exist')

        user = authenticate(request,
                            username=username,
                            password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password not found')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit="False")
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An Error Occurred "
                                    "During The Registration")
    return render(request, 'base/login_register.html',
                  {'form': form})


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
    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room_table: QuerySet[Room] = Room.objects.get(id=pk)
    context = {'room': room_table}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context: dict[Any, Any] = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    update_room = Room.objects.get(id=pk)
    form = RoomForm(instance=update_room)

    if request.user != update_room.host:
        return HttpResponse("You are not allowed here! "
                            "Please Return Back")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=update_room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    delete_room = Room.objects.get(id=pk)

    if request.user != delete_room.host:
        return HttpResponse("You are not allowed here! "
                            "Please Return Back")

    if request.method == "POST":
        delete_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', dict(obj=delete_room))
