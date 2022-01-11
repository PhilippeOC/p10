from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.shortcuts import get_object_or_404
from .models import Project, Issue, Comment
from .serializers import (WriteProjectSerializer,
                          ReadProjectSerializer,
                          WriteIssueSerializer,
                          ReadIssueSerializer,
                          ReadCommentSerializer,
                          WriteCommentSerializer)

from contributors.serializers import ReadContributorSerializer, WriteContributorSerializer
from contributors.permissions import (ProjectPermissions,
                                      IssuePermissions,
                                      CommentPermissions,
                                      UserPermissions)

from contributors.models import Contributor


class ProjectListCreate(generics.ListCreateAPIView):
    """ - Creation d'un projet et lecture des projets auquels l'utilisateur connecté contribue
        - Le créateur du projet est également enregistré comme contributeur
    """

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadProjectSerializer
        return WriteProjectSerializer

    def get_queryset(self):
        projects = Contributor.objects.filter(user_id=self.request.user.id).values_list('project_id')
        if not projects:
            raise ValidationError("Vous n'avez pas encore créé de projet.")
        return Project.objects.filter(id__in=projects)

    def perform_create(self, serializer):
        user_connected = self.request.user
        instance = serializer.save(author_user_id=user_connected.id)
        Contributor.objects.create(project=instance, user_id=user_connected.id, role='O')
        Contributor.objects.create(project=instance, user_id=user_connected.id, role='C')


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """ - Lecture d'un projet par son créateur ou un contributeur auquel il contribue
        - Seul le créateur d'un projet peut l'effacer ou l'actualiser
    """
    permission_classes = [ProjectPermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadProjectSerializer
        return WriteProjectSerializer

    def get_queryset(self):
        pk_project = self.kwargs.get('pk')
        projects = Project.objects.filter(pk=pk_project)
        if not projects:
            raise ValidationError(f"Le projet {pk_project} n'existe pas.")
        return projects

    def perform_update(self, serializer):
        project = Project.objects.filter(pk=self.kwargs.get('pk'))
        serializer.save(project=project)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": f"Le projet {self.kwargs.get('pk')} est supprimé."},
                        status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class IssueListCreate(generics.ListCreateAPIView):
    """ - Creation d'un problème associé à un projet
        - Lecture des problèmes associés à un projet
        - Seuls les contributeurs sont autorisés à créer ou lire les problèmes d'un projet """
    permission_classes = [IssuePermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadIssueSerializer
        return WriteIssueSerializer

    def get_queryset(self):
        pk_project = self.kwargs.get('id_project')
        issues = Issue.objects.filter(project=pk_project)
        if not issues:
            raise ValidationError(f"Le projet {pk_project} n'a pas de problème.")
        return issues

    def perform_create(self, serializer):
        user_connected = self.request.user
        pk_project = self.kwargs.get('id_project')
        # issue = Project.objects.get(pk=pk)
        issue = get_object_or_404(Project, pk=pk_project)
        assignee_user = serializer.validated_data['assignee_user']
        users_project = Contributor.objects.filter(project_id=pk_project).values_list('user_id', flat=True)
        if assignee_user.id not in users_project:
            raise ValidationError(f"L'utilisateur assigné doit être un contributeur du projet {pk_project}.")
        issue.assignee_user = serializer.validated_data['assignee_user']
        issue.author_user = user_connected
        issue.save()
        serializer.save(project=issue, author_user=user_connected)


class IssueDetail(generics.RetrieveUpdateDestroyAPIView):
    """ - Lecture par un contributeur d'un problème associé à un projet auquel il contribue
        - Seul l'auteur du problème peut l'effacer ou l'actualiser
    """

    permission_classes = [IssuePermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET' or 'PUT':
            return ReadIssueSerializer
        return WriteIssueSerializer

    def get_queryset(self):
        pk_project = self.kwargs.get('id_project')
        pk_issue = self.kwargs.get('pk')
        issues_list = Issue.objects.filter(project=pk_project)
        if pk_issue not in issues_list.values_list('id', flat=True):
            raise ValidationError(f"Le projet {pk_project} n'a pas de problème {pk_issue}.")
        return issues_list

    def perform_update(self, serializer):
        projet = Project.objects.get(pk=self.kwargs.get('id_project'))
        serializer.save(project=projet)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": f"Le problème {self.kwargs.get('pk')} est supprimé."},
                        status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class CommentListCreate(generics.ListCreateAPIView):
    permission_classes = [CommentPermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadCommentSerializer
        return WriteCommentSerializer

    def get_queryset(self):
        pk_issue = self.kwargs.get('id_issue')
        pk_project = self.kwargs.get('id_project')
        issues_list = Issue.objects.filter(project=pk_project).values_list('id', flat=True)
        if pk_issue not in issues_list:
            raise ValidationError(f"Le projet {pk_project} n'a pas de problème {pk_issue}.")
        comments = Comment.objects.filter(issue_id=pk_issue)
        if not comments:
            raise ValidationError(f"Le problème {pk_issue} du projet {pk_project} n'a pas de commentaire.")
        return comments

    def perform_create(self, serializer):
        pk_issue = self.kwargs.get('id_issue')
        pk_project = self.kwargs.get('id_project')
        issue = Issue.objects.filter(pk=pk_issue)
        if not issue:
            raise ValidationError(f"Le problème {pk_issue} n'existe pas dans le projet {pk_project}.")
        serializer.save(issue=issue.first(), author_user=self.request.user)


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [CommentPermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadCommentSerializer
        return WriteCommentSerializer

    def get_queryset(self):
        pk_issue = self.kwargs.get('id_issue')
        pk_project = self.kwargs.get('id_project')
        pk_comment = self.kwargs.get('pk')

        issues_list = Issue.objects.filter(project=pk_project)
        if pk_issue not in issues_list.values_list('id', flat=True):
            raise ValidationError(f"Le projet {pk_project} n'a pas de problème {pk_issue}.")
        comments_list = get_object_or_404(Issue, project_id=pk_project, pk=pk_issue).comments.all()
        if pk_comment not in comments_list.values_list('id', flat=True):
            raise ValidationError(f"Le problème {pk_issue} du projet {pk_project} n'a pas de commentaire {pk_comment}.")
        return comments_list

    def perform_update(self, serializer):
        comment = get_object_or_404(Issue, pk=self.kwargs.get('id_issue'))
        serializer.save(comment=comment)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": f"Le commentaire {self.kwargs.get('pk')} est supprimé."},
                        status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class UserProject(generics.ListCreateAPIView):
    """ - Ajouter un contributeur à un projet
        - Liste des contributeurs à un projet
        - Seul le responsable du projet peut ajouter un contributeur
        - Les contributeurs peuvent lire la liste des contributeurs
    """
    permission_classes = [UserPermissions]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadContributorSerializer
        return WriteContributorSerializer

    def get_queryset(self):
        pk_project = self.kwargs.get('id_project')
        users = Contributor.objects.filter(project_id=pk_project, role='C')

        if not users:
            raise ValidationError(f"Le projet {pk_project} n'existe pas.")
        if self.request.user.id not in users.values_list('user_id', flat=True):
            raise ValidationError(f"Vous n'êtes pas contributeur du projet {pk_project}.")
        return users

    def perform_create(self, serializer):
        pk_project = self.kwargs.get('id_project')
        users_project = Contributor.objects.filter(project_id=pk_project).values_list('user_id', flat=True)
        user_to_add = serializer.validated_data.get('user')
        if user_to_add.id in users_project:
            raise ValidationError(f"L'utilisateur {user_to_add.id} est déjà dans le projet {pk_project}")
        serializer.save(project_id=pk_project, role='C')


class DelUserProject(APIView):
    """ - Supprime un contributeur d'un projet
        - Seul le créateur du projet peut supprimer un contributeur
    """
    permission_classes = [UserPermissions]

    def delete(self, request, id_project, pk):
        if self.request.user.pk == pk:
            raise ValidationError(f"Vous ne pouvez pas supprimer le responsable du projet {id_project}.")
        user = Contributor.objects.filter(project_id=id_project, user_id=pk)
        if not user:
            raise ValidationError(f"L'utilisateur {pk} n'est pas dans le projet {id_project}")
        user.delete()
        return Response(f"L'utilisateur {pk} du projet {id_project} est supprimé.", status=status.HTTP_204_NO_CONTENT)
