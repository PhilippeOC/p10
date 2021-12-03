from django.urls import path

from projects import views 

urlpatterns = [
    path('', views.ProjectListCreate.as_view(), name='project'),
    path('<int:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('<int:pk>/issues/', views.IssueListCreate.as_view(), name='issue'),
    path('<int:id_project>/issues/<int:pk>/', views.IssueDetail.as_view(), name='issue-detail'),
    path('<int:id_project>/issues/<int:id_issue>/comments/', views.CommentListCreate.as_view(), name='comment'),
    path('<int:id_project>/issues/<int:id_issue>/comments/<int:pk>/', views.CommentDetail.as_view(), name='comment-detail'),
    path('<int:pk>/users/', views.ProjectUser.as_view(), name='project-user'),
    path('<int:id_project>/users/<int:id_user>/', views.ProjectUserDelete.as_view(), name='project-user-delete'),
]
