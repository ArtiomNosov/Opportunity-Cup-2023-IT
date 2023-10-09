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


def get_customer(job):
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')[0]
    return User.objects.get(id=customer_id['user'])

def get_job_to_customer(jobs):
    job_to_customer = {}  # Создаем пустой словарь

    for job in jobs:
        customer = get_customer(job)
        if customer:
            job_to_customer[job] = customer
    
    return job_to_customer

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

    job_to_customer = get_job_to_customer(jobs)  

    context = {'jobs': jobs, 
               'job_to_customer': job_to_customer, 
               'topics': topics,
               'job_count': job_count, 
               'job_messages': job_messages}
    

    return render(request, 'base/home.html', context)


def job(request, pk):
    job = Job.objects.get(id=pk)
    job_messages = job.message_set.all()
    participants_id = Match.objects.filter(job=job).values('user')
    participants = User.objects.filter(id__in=[user_id['user'] for user_id in participants_id])
    print()
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
    
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    context = {'job': job, 'job_messages': job_messages,
               'participants': participants,
               'job_customer': job_customer}
    return render(request, 'base/job.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    jobs = Job.objects.filter(id__in=[x['job'] for x in 
        Match.objects.filter(user=user, type=MatchType.objects.get_or_create(name='Customer')[0].id).values('job')
    ])
    job_messages = user.message_set.all()
    topics = Topic.objects.all()
    job_to_customer = get_job_to_customer(jobs)
    context = {'user': user, 'job_to_customer': job_to_customer,
               'job_messages': job_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

def userBalance(request, pk): # TODO:
    user = User.objects.get(id=pk)
    transactions = user.transaction_set.all()
    context = {
        'user': user,
        'transactions': transactions
    }
    return render(request, f'base/balance.html', context)


@login_required(login_url='login')
def createJob(request):
    form = JobForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        job = Job.objects.create(
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            status = JobStatus.objects.get_or_create(name='Find performer')[0],
            cost=request.POST.get('cost'),
        )
        job.save()
        match = Match.objects.create(
            job = job,
            user = request.user,
            type = MatchType.objects.get_or_create(name='Customer')[0],
        )
        match.save()
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/job_form.html', context)


@login_required(login_url='login')
def updateJob(request, pk):
    job = Job.objects.get(id=pk)
    form = JobForm(instance=job)
    topics = Topic.objects.all()
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    if request.user != job_customer:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        job.name = request.POST.get('name')
        job.topic = topic
        job.description = request.POST.get('description')
        job.cost = request.POST.get('cost')
        job.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'job': job}
    
    return render(request, 'base/job_form.html', context)

def get_customer(job):
    customer_id = Match.objects.filter(job=job, type=MatchType.objects.get_or_create(name='Customer')[0]).values('user')
    job_customer = User.objects.filter(id=customer_id[0]['user'])[0]
    return job_customer

@login_required(login_url='login')
def deleteJob(request, pk):
    job = Job.objects.get(id=pk)
    job_customer = get_customer(job)

    if request.user != job_customer:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        job.delete()
        return redirect('home')
    context = {'obj': job}
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
