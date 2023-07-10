from django.urls import path
from .views import (UserListView, UserDetailView,
                    UserLineDetailView, SignupAPI, LoginAPI, NearbyUserView)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('user/<int:user_id>/line/',
         UserLineDetailView.as_view(), name='user-detail'),
    path('signup/', SignupAPI.as_view(), name='signup'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('nearby_users/', NearbyUserView.as_view(), name='nearby-users')
]
