from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Post, Comment, Vote


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'content_type', 'object_id', 'value', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['user__username']
    ordering = ['-created_at']
