"""
Serializers for the Playto Community Feed API.

Implements the N+1 Solution for threaded comments as described in Section 4.1
of ARCHITECTURE_AND_PRD.md. The comment tree is built in-memory using a 
hash map + single pass approach (O(2 Queries + N CPU cycles)).
"""

from typing import Any

from rest_framework import serializers

from .models import User, Post, Comment, Vote


class UserSerializer(serializers.ModelSerializer):
    """Minimal user representation for nested serialization."""
    
    class Meta:
        model = User
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    """
    Flat comment serializer - used as the base representation.
    
    Note: This does NOT recursively fetch children from the DB.
    The 'replies' field is populated in-memory by the tree builder.
    """
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'parent_id', 'replies', 'like_count']
    
    def get_replies(self, obj: Comment) -> list:
        """
        Returns pre-computed replies from context.
        The tree is built in PostDetailSerializer.get_comments() 
        and passed via context to avoid recursive DB queries.
        """
        # Get the pre-built children map from context
        children_map = self.context.get('children_map', {})
        children = children_map.get(obj.id, [])
        
        # Recursively serialize children (all data is already in memory)
        return CommentSerializer(
            children, 
            many=True, 
            context=self.context
        ).data
    
    def get_like_count(self, obj: Comment) -> int:
        """Get like count from prefetched votes or annotated value."""
        if hasattr(obj, 'like_count'):
            return obj.like_count
        return obj.votes.count()


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer for the post feed list view.
    Efficient - uses select_related for author and annotated like_count.
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'like_count', 'comment_count']
    
    def get_like_count(self, obj: Post) -> int:
        """Get like count from annotated value or fallback to count."""
        if hasattr(obj, 'like_count'):
            return obj.like_count
        return obj.votes.count()
    
    def get_comment_count(self, obj: Post) -> int:
        """Get comment count from annotated value or fallback to count."""
        if hasattr(obj, 'comment_count'):
            return obj.comment_count
        return obj.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for single post detail view with FULL nested comment tree.
    
    Implements the N+1 Solution from Section 4.1:
    - Fetches all comments in 1 query via prefetch_related
    - Builds tree structure in-memory using hash map approach
    - O(2 Queries + N CPU cycles) instead of O(N Queries)
    """
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'updated_at', 'like_count', 'comments']
    
    def get_like_count(self, obj: Post) -> int:
        """Get like count from annotated value or fallback."""
        if hasattr(obj, 'like_count'):
            return obj.like_count
        return obj.votes.count()
    
    def get_comments(self, obj: Post) -> list[dict[str, Any]]:
        """
        Build the nested comment tree in-memory.
        
        Strategy (from EXPLAINER.md):
        1. Load flat list of comments into memory (already prefetched)
        2. Convert to hash map (Dictionary) keyed by ID
        3. Single pass to attach children to their parents
        4. Return only root-level comments (serialized with nested replies)
        """
        # All comments are already prefetched - no additional queries
        comments = list(obj.comments.all())
        
        if not comments:
            return []
        
        # Build children map: parent_id -> [child_comments]
        children_map: dict[int | None, list[Comment]] = {}
        for comment in comments:
            parent_id = comment.parent_id
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(comment)
        
        # Get root comments (parent_id is None)
        root_comments = children_map.get(None, [])
        
        # Serialize with children_map in context for recursive serialization
        return CommentSerializer(
            root_comments,
            many=True,
            context={'children_map': children_map, **self.context}
        ).data


class VoteSerializer(serializers.Serializer):
    """
    Serializer for vote creation.
    Accepts model type and object ID.
    """
    model = serializers.ChoiceField(choices=['post', 'comment'])
    id = serializers.IntegerField()
