from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('job/<str:pk>/', views.job, name="job"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-job/', views.createRoom, name="create-job"),
    path('update-job/<str:pk>/', views.updateRoom, name="update-job"),
    path('delete-job/<str:pk>/', views.deleteRoom, name="delete-job"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
]
