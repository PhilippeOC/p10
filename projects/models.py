from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()


class Project(models.Model):
    BACK_END = 'BE'
    FRONT_END = 'FE'
    IOS = 'IS'
    ANDROID = 'AD'
    TYPE_CHOICE = [
        (BACK_END, 'Back-end'),
        (FRONT_END, 'Front-end'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=2, choices=TYPE_CHOICE, default=BACK_END)
    author_user_id = models.IntegerField()

    def __str__(self):
        return f"Project id: {self.pk}"


class Issue(models.Model):
    BUG = 'BUG'
    IMPROVEMENT = 'IMPROV'
    TASK = 'TASK'
    TAG_CHOICE = [(BUG, 'Bug'), (IMPROVEMENT, 'Amélioration'), (TASK, 'Tâche')]

    TO_DO = 'TD'
    IN_PROGRESS = 'IP'
    ENDED = 'END'
    STATUS_CHOICE = [(TO_DO, 'A faire'), (IN_PROGRESS, 'En cours'), (ENDED, 'Terminé')]

    LOW_PRIORITY = 'LP'
    MEDIUM_PRIORITY = 'MP'
    HIGH_PRIORITY = 'HP'
    PRIORITY_CHOICE = [(LOW_PRIORITY, 'Faible'), (MEDIUM_PRIORITY, 'Moyenne'), (HIGH_PRIORITY, 'Elevée')]

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1200)
    tag = models.CharField(max_length=6, choices=TAG_CHOICE, default=BUG)
    status = models.CharField(max_length=3, choices=STATUS_CHOICE, default=TO_DO)
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICE, default=LOW_PRIORITY)

    author_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="issues_author")
    assignee_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="issues_assignee")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue id: {self.pk} - Projet id: {self.project.id}"


class Comment(models.Model):
    description = models.CharField(max_length=1200)
    author_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment id: {self.pk} - Issue id: {self.issue.id}"
