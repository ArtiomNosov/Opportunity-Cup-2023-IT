from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import User, Topic, JobStatus, Job, MatchType, Match, ReviewType, Review, Message
from .forms import JobForm, UserForm, MyUserCreationForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    jobs = Job.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    job_count = jobs.count()
    job_messages = Message.objects.filter(
        Q(job__topic__name__icontains=q))[0:3]

    job_customer = User.objects.all()[0] # TODO: правильно определить customer для этой job

    context = {'jobs': jobs, 
               'job_customer': job_customer, 
               'topics': topics,
               'job_count': job_count, 
               'job_messages': job_messages}
    
    return render(request, 'base/home.html', context)


def job(request, pk):
    job = Job.objects.get(id=pk)
    job_messages = job.message_set.all()
    # participants = job.participants.all()
    participants = User.objects.all() # TODO: правильно определять всех participant для данной job
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            job=job,
            body=request.POST.get('body')
        )
        message.save()
        if Match.objects.filter(user=request.user).count() == 0:
            match = Match.objects.create(
                job = job,
                user = request.user,
                type = MatchType.objects.get_or_create(name='Participant')[0]
            )
            match.save()
        return redirect('job', pk=job.id)
    
    job_customer = User.objects.all()[0] # job_customer
    context = {'job': job, 'job_messages': job_messages,
               'participants': participants,
               'job_customer': job_customer}
    return render(request, 'base/job.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    jobs = user.job_set.all()
    job_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'jobs': jobs,
               'job_messages': job_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createJob(request):
    # form = JobForm()
    # topics = Topic.objects.all()
    if request.method == 'POST':
        # topic_name = request.POST.get('topic')
        # topic, created = Topic.objects.get_or_create(name=topic_name)

        # Job.objects.create(
        #     host=request.user,
        #     topic=topic,
        #     name=request.POST.get('name'),
        #     description=request.POST.get('description'),
        # )
        return redirect('home')

    # context = {'form': form, 'topics': topics}
    context = {}
    return render(request, 'base/job_form.html', context)


@login_required(login_url='login')
def updateJob(request, pk):
    # job = Job.objects.get(id=pk)
    # form = JobForm(instance=job)
    # topics = Topic.objects.all()
    # if request.user != job.host:
    #     return HttpResponse('Your are not allowed here!!')

    # if request.method == 'POST':
    #     topic_name = request.POST.get('topic')
    #     topic, created = Topic.objects.get_or_create(name=topic_name)
    #     job.name = request.POST.get('name')
    #     job.topic = topic
    #     job.description = request.POST.get('description')
    #     job.save()
    #     return redirect('home')

    # context = {'form': form, 'topics': topics, 'job': job}
    
    return render(request, 'base/job_form.html', {})


@login_required(login_url='login')
def deleteJob(request, pk):
    # job = Job.objects.get(id=pk)

    # if request.user != job.host:
    #     return HttpResponse('Your are not allowed here!!')

    # if request.method == 'POST':
    #     job.delete()
    #     return redirect('home')
    # context = {'obj': job}
    return render(request, 'base/delete.html', {})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    job_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'job_messages': job_messages})
