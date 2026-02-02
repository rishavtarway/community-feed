"""
Models for the Playto Community Feed application.

Implements the data model as specified in Section 3.1 of ARCHITECTURE_AND_PRD.md:
- User (AbstractUser extension)
- Post
- Comment (with self-referential FK for threading - Adjacency List Model)
- Vote (with GenericForeignKey for polymorphic likes - Karma Ledger)
"""

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Note: No 'total_karma' field stored here to strictly satisfy the 
    assignment constraint of dynamic calculation (per ARCHITECTURE_AND_PRD.md Section 3.1.A).
    """
    
    class Meta:
        db_table = 'feed_user'
    
    def __str__(self) -> str:
        return self.username


class Post(models.Model):
    """
    Post model representing a content post in the community feed.
    
    As specified in Section 3.1.B of ARCHITECTURE_AND_PRD.md.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # GenericRelation for reverse lookup of votes
    votes = GenericRelation('Vote', related_query_name='post')
    
    class Meta:
        db_table = 'feed_post'
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    """
    Comment model with self-referential FK for threaded discussions.
    
    Uses the Adjacency List Model as specified in Section 3.1.C of ARCHITECTURE_AND_PRD.md.
    The 'parent' FK allows for nested comment threads.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'  # Critical for prefetching
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'  # Adjacency List Model
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # GenericRelation for reverse lookup of votes
    votes = GenericRelation('Vote', related_query_name='comment')
    
    class Meta:
        db_table = 'feed_comment'
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on Post {self.post_id}"


class Vote(models.Model):
    """
    Vote model - The Karma Ledger.
    
    This table is the source of truth for the Leaderboard as specified 
    in Section 3.1.D of ARCHITECTURE_AND_PRD.md.
    
    Uses GenericForeignKey to support voting on both Posts and Comments.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="The person clicking like"
    )
    value = models.IntegerField(
        default=1,
        help_text="Only Likes allowed per requirements (+1), but flexible for future"
    )
    
    # Generic Foreign Key fields
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('post', 'comment')}
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Crucial for the 24h window filter in leaderboard
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'feed_vote'
        # Prevent double-voting at the database level
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='unique_user_vote_per_content'
            )
        ]
    
    def __str__(self) -> str:
        return f"Vote by {self.user.username} on {self.content_type.model} {self.object_id}"
