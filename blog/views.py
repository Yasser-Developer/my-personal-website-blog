from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def index(request):
    return render(request, 'blog/index.html')

def topics(request):
    query = request.GET.get('q')
    if query:
        topics = Topic.objects.filter(
            Q(text__icontains=query) | Q(entry__text__icontains=query)
        ).distinct().order_by('date_added')
    else:
        topics = Topic.objects.order_by('date_added')
    context = {'topics': topics, 'query': query}
    return render(request, 'blog/topics.html', context)

def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'blog/topic.html', context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:topics')
    context = {'form': form}
    return render(request, 'blog/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('blog:topic', topic_id=topic_id)
    context = {'topic': topic, 'form': form}
    return render(request, 'blog/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'blog/edit_entry.html', context)

@login_required
def delete_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if request.method == 'POST':
        entry.delete()
        return redirect('blog:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic}
    return render(request, 'blog/delete_entry.html', context)

def signup(request):
    if request.method != 'POST':
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    context = {'form': form}
    return render(request, 'registration/signup.html', context)