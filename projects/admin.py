from django.contrib import admin


from projects.models import Comment, Project, Issue


admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)
