from django.contrib import admin

# Register your models here.

from .models import User, Topic, JobStatus, Job, MatchType, Match, ReviewType, Review, Message, Transaction

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(JobStatus)
admin.site.register(Job)
admin.site.register(MatchType)
admin.site.register(Match)
admin.site.register(ReviewType)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(Transaction)


