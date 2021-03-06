from django.urls import path

from . import views
from .views import AddGroupView

urlpatterns = [
    path('add_group/', AddGroupView.as_view(), name='add_group'),
    path('search/', views.search, name='search_results'),
#     path('search/', SearchResultsView.as_view(), name='search_results'),
    path('', views.index, name='index'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        '<str:username>/follow/', views.profile_follow,
        name='profile_follow'
    ),
    path('<str:username>/unfollow/',
         views.profile_unfollow, name='profile_unfollow'),
    path('new/', views.new_post, name='new_post'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path('<str:username>/<int:post_id>/comment', views.add_comment,
         name="add_comment"),
    
]
