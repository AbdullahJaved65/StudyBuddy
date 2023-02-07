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

from .forms import RoomForm, UserForm
from .models import Room, Topic, Message


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
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count,
               'room_message': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room_table: QuerySet[Room] = Room.objects.get(id=pk)
    room_messages = room_table.message_set.all().order_by("-created")
    participants = room_table.participant.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room_table,
            body=request.POST.get('body')
        )
        room_table.participant.add(request.user)
        return redirect('room', pk=room_table.id)
    context = {'room': room_table,
               'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user,
               'rooms': rooms,
               'room_message': room_message,
               'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context: dict[Any, Any] = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    update_room = Room.objects.get(id=pk)
    form = RoomForm(instance=update_room)
    topics = Topic.objects.all()
    if request.user != update_room.host:
        return HttpResponse("You are not allowed here! "
                            "Please Return Back")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        update_room.name = request.POST.get('name')
        update_room.topic = topic
        update_room.description = request.POST.get('description')
        update_room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': update_room}
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


@login_required(login_url='login')
def deleteMessage(request, pk):
    delete_message: Message = Message.objects.get(id=pk)

    if request.user != delete_message.user:
        return HttpResponse("You are not allowed here! "
                            "Please Return Back")

    if request.method == "POST":
        delete_message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', dict(obj=delete_message))


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)