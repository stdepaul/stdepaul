from django.contrib import admin

from .models import Helper
from .models import Post
from .models import PostReport
from .models import Comment
from .models import CommentReport

@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    pass