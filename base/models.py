from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default='avatar.svg')

    balance = MoneyField(max_digits=19, decimal_places=4, default_currency='RUB', default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class JobStatus(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Job(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    cost = MoneyField(max_digits=19, decimal_places=4, default_currency='RUB')
    created = models.DateTimeField(auto_now_add=True)

    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    status = models.ForeignKey(JobStatus, on_delete=models.SET_NULL, null=True)

class MatchType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Match(models.Model):
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    type = models.ForeignKey(MatchType, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created']

class ReviewType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Review(models.Model):
    rating = models.SmallIntegerField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    type = models.ForeignKey(ReviewType, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created']

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    body = models.TextField() 
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
