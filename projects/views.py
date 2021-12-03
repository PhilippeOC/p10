from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import get_object_or_404

from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from .models import Project, Issue, Comment
from contributors.models import Contributor
from contributors.serializers import ContributorSerializer
#  from contributors.permissions import IsOwner



class ProjectListCreate(generics.ListCreateAPIView):
    # Permissions: - création d'un projet : tout utilisateur authentifié
    # Permissions: - liste des projets : le responsable et les contributeurs liés à ces projets
    # queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        projects = Contributor.objects.filter(user_id=self.request.user.pk).values_list('project_id')
        return Project.objects.filter(id__in=projects)
    
    def perform_create(self, serializer):
        user_connected = self.request.user
        instance = serializer.save()
        Contributor.objects.create(project=instance, user=user_connected)
        
        
class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    # Permissions: - actualisation et suppression réservé au responsable du projet
    #              - Lecture du projet : le responsable et les contributeurs au projet  
    #permission_classes = [IsOwner]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    
class IssueListCreate(generics.ListCreateAPIView):
    # Permissions: les contributeurs peuvent créer ou consulter les problèmes d'un projet
    serializer_class = IssueSerializer
    
    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs.get('pk'))

    def perform_create(self, serializer):
        issue = Project.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(project=issue)


class IssueDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IssueSerializer

    def get_queryset(self):
        return Issue.objects.filter(project=self.kwargs.get('id_project'))

    def perform_update(self, serializer):
        issue = Project.objects.filter(pk=self.kwargs.get('id_project'))
        serializer.save(project=issue)

    def perform_destroy(self, serializer):
        Project.objects.filter(pk=self.kwargs.get('id_project'))
        serializer.delete()
        
        
class CommentListCreate(generics.ListCreateAPIView):
    # permission: les contributeurs peuvent créer et lire les commentaires
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs.get('id_issue'))

    def perform_create(self, serializer):
        comment = Issue.objects.filter(pk=self.kwargs.get('id_issue'))
        serializer.save(issue=comment)
        
        
class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    # permission: les contributeurs peuvent actualiser ou supprimer les commentaires dont il sont les auteurs
    serializer_class = CommentSerializer
    

    def get_queryset(self):
        # permission aux contributeurs
        return Comment.objects.filter(issue=self.kwargs.get('id_issue'))

    def perform_update(self, serializer):
        # permission aux contributeurs qui sont aussi auteurs du commentaire
        comment = Issue.objects.filter(pk=self.kwargs.get('id_issue'))
        serializer.save(comment=comment)

    def perform_destroy(self, serializer):
        # permission aux contributeurs qui sont aussi auteurs du commentaire
        Issue.objects.filter(pk=self.kwargs.get('id_issue'))
        serializer.delete()

class ProjectUser(generics.ListCreateAPIView):
    # permission_classes = [IsOwner]
    # permission:- acces uniquement au responsable du projet
    #            - uniquement aux projets du responsable du projet
    serializer_class = ContributorSerializer
    
    def get_queryset(self):
        return Contributor.objects.filter(project_id = self.kwargs.get('pk'))
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        users_project = Contributor.objects.filter(project_id=pk).values_list('user_id', flat=True)
        if not users_project:
            raise ValidationError(f"Le projet {pk} n'existe pas")
        user_to_add = serializer.validated_data.get('user')
        if user_to_add.id in users_project:
            raise ValidationError(f"L'utilisateur {user_to_add.id} est déjà dans le projet {pk}")
        
        serializer.save(project_id=pk)
        
class ProjectUserDelete(APIView):
    # permission: acces uniquement au responsable du projet
    def delete(self, request, id_project, id_user):
        if self.request.user.pk == id_user:
            raise ValidationError("Vous ne pouvez pas supprimer le responsable du projet.") 
        get_object_or_404(Contributor, project_id=id_project, user_id=id_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)