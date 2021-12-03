from django.db import models

from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

class Contributor(models.Model):
    # OWNER_PERMISSION = 'OP'
    # CONTRIBUTOR_PERMISSION = 'CP'
    # PERMISSIONS_CHOICE = [(OWNER_PERMISSION, 'Permissions proriétaire'), (CONTRIBUTOR_PERMISSION, 'Permissions contributeur')]
    
    OWNER = 'O'
    CONTRIBUTOR = 'C'
    ROLE_CHOICE = [(OWNER, 'Propriétaire'), (CONTRIBUTOR, 'Contributeur')]

    # permission = models.CharField(max_length=30, choices=PERMISSIONS_CHOICE, default=OWNER_PERMISSION)
    role = models.CharField(max_length=30, choices=ROLE_CHOICE, default=OWNER)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
    
    def __str__(self):
        return f"Contributor id : {self.pk}"
    
    
    
