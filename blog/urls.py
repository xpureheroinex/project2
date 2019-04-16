from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.home_page, name='home'),
    path('', views.home_page),
    path('login/', views.user_login),
    path('register/', views.user_registration),
    path('groups/', views.GroupsList.as_view(), name='group_list'),
    path('groups/new/', views.GroupCreate.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupInfo.as_view(), name='group_info'),
    path('groups/<int:group_id>/update/', views.GroupUpdate.as_view(),
         name='group_update'),
    path('groups/<int:group_id>/delete/', views.GroupDelete.as_view(),
         name='group_delete'),
    path('groups/<int:group_id>/join/', views.GroupJoin.as_view(),
         name='group_join'),
    path('posts/', views.PostsList.as_view(), name='post_list'),
    path('posts/<int:pk>', views.PostInfo.as_view(), name='post_info'),
    path('posts/create/', views.PostCreate.as_view(), name='post_create'),
    path('posts/<int:post_id>/update/', views.PostUpdate.as_view(),
         name='post_update'),
    path('posts/<int:post_id>/delete/', views.PostDelete.as_view(),
         name='post_delete')

]