"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required
from django.urls import path
from app import views

app_name = 'app'

urlpatterns = [
    path('', views.PaginationView.as_view(), name='index'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', login_required(views.LogoutView.as_view()), name='logout'),
    path('user/<int:id>/', login_required(views.UserView.as_view()), name='user'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('ask/', login_required(views.AskQuestionView.as_view()), name='ask'),
    path('question/<int:id>/', views.QuestionView.as_view(), name='question'),
    path('top/', views.TopQuestionsView.as_view(), name='top'),
    path('tag/<str:name>/', views.TagQuestionsView.as_view(), name='tag')
]
