from django.urls import path

from .views import UserCreateView, UserListView

urlpatterns = [
        path('register/', UserCreateView.as_view(), name='register'),
        path('users/', UserListView.as_view(), name='user-list'),
]
