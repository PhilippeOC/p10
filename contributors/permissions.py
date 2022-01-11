from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Contributor
from projects.models import Issue, Comment


class ProjectPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """ Retourne True si l'utilisateur connecté est un contributeur (request GET)
            ou s'il est le responsable du projet (request PUT DELETE)
        """
        if request.method == 'GET':
            contributors_list = Contributor.objects.filter(project_id=obj.id, role='C').values_list('user_id',
                                                                                                    flat=True)
            if request.user.id in contributors_list:
                return True
            raise ValidationError(f"Vous n'êtes pas contributeur du projet {obj.id}.")
        elif request.method in ['PUT', 'DELETE']:
            owner = Contributor.objects.filter(project_id=obj.id, role='O').values_list('user_id', flat=True)
            if request.user.id in owner:
                return True
            raise ValidationError(f"Seul le responsable du projet {obj.id} peut l'actualiser ou le supprimer.")


class IssuePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        """ - Autorise l'utilisateur connecté s'il est contributeur à lire la liste des problèmes
            du projet auquels il contribue.
            - Autorise l'utilisateur connecté s'il est contributeur du projet à créer un problème
        """
        user_connected = request.user.id
        pk_project = request.resolver_match.kwargs.get('id_project')
        projects = Contributor.objects.filter(project_id=pk_project)
        contributors = Contributor.objects.filter(project_id=pk_project, role='C').values_list('user_id', flat=True)
        if not projects:
            raise ValidationError(f"Le projet {pk_project} n'existe pas.")
        if request.method == 'GET':
            if user_connected in contributors:
                return True
            raise ValidationError(f"Seuls les contribueurs au projet {pk_project} peuvent accéder à ses problèmes.")
        if request.method in ['PUT', 'DELETE']:
            if user_connected in contributors:
                return True
            raise ValidationError(f"Seuls les contribueurs au projet {pk_project} peuvent modifier"
                                  " ou supprimer un problème.")
        if request.method == 'POST':
            if user_connected in contributors:
                return True
            raise ValidationError(f"Seuls les contribueurs au projet {pk_project} peuvent à créer un problème.")

    def has_object_permission(self, request, view, obj):
        """ - Autorise l'utilisateur connecté, s'il est l'auteur du problème, à l'actualiser ou à le supprimer.
            - Autorise l'utilisateur connecté, s'il est contributeur du projet, à lire un problème.
        """
        user_connected = request.user.id
        pk_project = request.resolver_match.kwargs.get('id_project')
        if request.method == 'GET':
            contributor = Contributor.objects.filter(project_id=pk_project, user_id=user_connected, role='C')
            if contributor:
                return True
            raise ValidationError(f"Vous n'êtes pas un contributeur du projet {pk_project}")
        elif request.method in ['PUT', 'DELETE']:
            author_issue = get_object_or_404(Issue, pk=obj.id).author_user
            if user_connected == author_issue.id:
                return True
            raise ValidationError(f"Seul l'auteur du problème {obj.id} peut l'actualiser ou le supprimer")


class CommentPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        """ - Autorise l'utilisateur connecté s'il est contributeur à lire la liste des commentaires
            des problèmes du projet auquels ils contribuent.
            - Autorise l'utilisateur connecté s'il est contributeur du projet à créer un commentaire
            à un problème.
        """
        user_connected = request.user.id
        pk_project = request.resolver_match.kwargs.get('id_project')
        pk_issue = request.resolver_match.kwargs.get('id_issue')
        projects = Contributor.objects.filter(project_id=pk_project)
        contributors = Contributor.objects.filter(project_id=pk_project, role='C').values_list('user_id', flat=True)
        if not projects:
            raise ValidationError(f"Le projet {pk_project} n'existe pas.")
        if request.method == 'GET':
            if user_connected in contributors:
                return True
            raise ValidationError(f"Vous n'êtes pas autorisé à accéder aux commentaires du problème {pk_issue}"
                                  f" du projet {pk_project}")
        if request.method in ['PUT', 'DELETE']:
            if user_connected in contributors:
                return True
            raise ValidationError(f"Seuls les contribueurs du projet {pk_project}"
                                  " peuvent modifier ou supprimer un commentaire.")
        if request.method == 'POST':
            if user_connected in contributors:
                return True
            raise ValidationError(f"Seuls les contribueurs du projet {pk_project} peuvent créer un commentaire.")

    def has_object_permission(self, request, view, obj):
        """ - Autorise l'utilisateur connecté, s'il est l'auteur du commentaire, à l'actualiser ou à le supprimer.
            - Autorise l'utilisateur connecté, s'il est contributeur du projet, à lire un commentaire.
        """
        user_connected = request.user.id
        pk_project = request.resolver_match.kwargs.get('id_project')
        if request.method == 'GET':
            contributor = Contributor.objects.filter(project_id=pk_project, user_id=user_connected, role='C')
            if contributor:
                return True
            raise ValidationError(f"Vous n'êtes pas un contributeur du projet {pk_project}.")
        elif request.method in ['PUT', 'DELETE']:
            author_comment = get_object_or_404(Comment, pk=obj.id).author_user
            if user_connected == author_comment.id:
                return True
            raise ValidationError(f"Seul l'auteur du commentaire {obj.id} peut l'actualiser ou le supprimer.")


class UserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        pk_project = request.resolver_match.kwargs.get('id_project')
        if request.method == 'GET':
            return True
        if request.method in ['POST', 'PUT', 'DELETE']:
            owner = Contributor.objects.filter(project_id=pk_project, role='O').values_list('user_id', flat=True)
            if not owner:
                raise ValidationError(f"Le projet {pk_project} n'existe pas.")
            if request.user.id in owner:
                return True
            raise ValidationError(f"Vous n'êtes pas le responsable du projet {pk_project}.")
