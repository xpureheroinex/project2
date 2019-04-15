from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.home_page, name='home'),
    path('', views.home_page),
    path('login/', views.user_login),
    path('register/', views.user_registration),
    path('groups/', views.GroupsList.as_view(), name='group_list'),
    path('groups/new/', views.GroupCreate.as_view()),
    path('groups/<int:pk>/', views.GroupInfo.as_view(), name='group_info'),
    path('groups/<int:group_id>/update/', views.GroupUpdate.as_view(),
         name='group_update'),
    path('groups/<int:group_id>/delete/', views.GroupUpdate.as_view(),
         name='group_delete'),

]