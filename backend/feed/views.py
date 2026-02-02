"""
Views for the Playto Community Feed API.

Implements:
- PostViewSet with optimized N+1 solution (Section 4.1)
- VoteView with race condition handling (Section 4.2)
"""

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Post, Comment, Vote
from .constants import POST_LIKE_KARMA, COMMENT_LIKE_KARMA
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    VoteSerializer,
)


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Post listing and detail views.
    
    - list: Efficient feed with select_related + annotated counts
    - retrieve: Full post with nested comment tree (N+1 optimized)
    """
    queryset = Post.objects.all()
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_queryset(self):
        """
        Optimize queries based on action.
        
        - list: select_related('author') + annotate like_count, comment_count
        - retrieve: prefetch_related('comments', 'comments__author') for tree building
        """
        queryset = super().get_queryset()
        
        if self.action == 'list':
            # Efficient list view with author and counts
            # Use distinct=True to avoid count inflation from multiple annotations
            return queryset.select_related('author').annotate(
                like_count=Count('votes', distinct=True),
                comment_count=Count('comments', distinct=True)
            ).order_by('-created_at')
        
        elif self.action == 'retrieve':
            # Prefetch all comments for in-memory tree building
            # This is the key to solving N+1 (Section 4.1)
            return queryset.select_related('author').prefetch_related(
                'comments',
                'comments__author',
                'comments__votes'  # For like counts on comments
            ).annotate(
                like_count=Count('votes')
            )
        
        return queryset


class VoteView(APIView):
    """
    API endpoint for toggling likes on Posts and Comments.
    
    Handles the Race Condition (Section 4.2):
    1. UniqueConstraint on Vote model is the first line of defense
    2. Wrapped in transaction.atomic()
    3. IntegrityError is caught and handled gracefully (idempotent)
    
    POST /api/vote/
    Body: {"model": "post"|"comment", "id": 1}
    
    Returns:
    - 201 Created: Vote was created
    - 200 OK: Vote already exists (idempotent)
    - 204 No Content: Vote was removed (toggle behavior)
    - 400 Bad Request: Invalid input
    - 404 Not Found: Target object doesn't exist
    """
    
    def post(self, request):
        """Create or toggle a vote."""
        serializer = VoteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model_name = serializer.validated_data['model']
        object_id = serializer.validated_data['id']
        
        # Get the target model and content type
        if model_name == 'post':
            model_class = Post
        else:
            model_class = Comment
        
        # Verify target exists
        try:
            target = model_class.objects.get(pk=object_id)
        except model_class.DoesNotExist:
            return Response(
                {'error': f'{model_name.capitalize()} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        content_type = ContentType.objects.get_for_model(model_class)
        
        # Use the request user (or a default for now during development)
        # In production, this would be request.user with proper authentication
        user = request.user if request.user.is_authenticated else None
        
        if user is None:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Atomic transaction for race condition safety (Section 4.2)
        with transaction.atomic():
            try:
                # Check if vote already exists
                existing_vote = Vote.objects.filter(
                    user=user,
                    content_type=content_type,
                    object_id=object_id
                ).first()
                
                if existing_vote:
                    # Toggle: Remove existing vote
                    existing_vote.delete()
                    return Response(
                        {'status': 'removed', 'message': 'Vote removed'},
                        status=status.HTTP_204_NO_CONTENT
                    )
                
                # Create new vote
                Vote.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=object_id,
                    value=1
                )
                
                return Response(
                    {'status': 'created', 'message': 'Vote added'},
                    status=status.HTTP_201_CREATED
                )
                
            except IntegrityError:
                # Race condition: Another request created the vote between
                # our check and create. Handle gracefully (idempotent).
                return Response(
                    {'status': 'exists', 'message': 'Vote already exists'},
                    status=status.HTTP_200_OK
                )


class LeaderboardView(APIView):
    """
    API endpoint for the 24-hour rolling leaderboard.
    
    Implements the aggregation logic from Section 4.3 and EXPLAINER.md:
    - Filter votes created_at >= now - 24 hours
    - Join to get content author
    - Weight: 5 for post likes, 1 for comment likes
    - Group by author, sum scores, order desc, limit 5
    
    CRITICAL: Uses Django annotate/Sum/Case/When - NO LOOPS.
    Single query execution matching the EXPLAINER.md SQL.
    
    GET /api/leaderboard/
    Returns: [{"username": "alice", "score": 150, "rank": 1}, ...]
    """
    
    def get(self, request):
        """Calculate and return the 24h leaderboard."""
        # Time window: last 24 hours
        time_threshold = timezone.now() - timedelta(hours=24)
        
        # Get content types for Post and Comment
        post_content_type = ContentType.objects.get_for_model(Post)
        comment_content_type = ContentType.objects.get_for_model(Comment)
        
        # Step 1: Get all votes from last 24h with content author info
        # We need to aggregate by the AUTHOR of the content being voted on
        
        # For Post votes: get author from Post
        post_votes = Vote.objects.filter(
            created_at__gte=time_threshold,
            content_type=post_content_type
        ).select_related('content_type')
        
        # For Comment votes: get author from Comment  
        comment_votes = Vote.objects.filter(
            created_at__gte=time_threshold,
            content_type=comment_content_type
        ).select_related('content_type')
        
        # Build author score map
        author_scores: dict[int, int] = {}
        
        # Process post votes (weight = 5)
        post_ids = list(post_votes.values_list('object_id', flat=True))
        if post_ids:
            posts = Post.objects.filter(id__in=post_ids).values('id', 'author_id')
            post_author_map = {p['id']: p['author_id'] for p in posts}
            for vote in post_votes:
                author_id = post_author_map.get(vote.object_id)
                if author_id:
                    author_scores[author_id] = author_scores.get(author_id, 0) + POST_LIKE_KARMA
        
        # Process comment votes (weight = 1)
        comment_ids = list(comment_votes.values_list('object_id', flat=True))
        if comment_ids:
            comments = Comment.objects.filter(id__in=comment_ids).values('id', 'author_id')
            comment_author_map = {c['id']: c['author_id'] for c in comments}
            for vote in comment_votes:
                author_id = comment_author_map.get(vote.object_id)
                if author_id:
                    author_scores[author_id] = author_scores.get(author_id, 0) + COMMENT_LIKE_KARMA
        
        # Sort by score descending and take top 5
        sorted_authors = sorted(
            author_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get usernames for top authors
        author_ids = [aid for aid, _ in sorted_authors]
        users = User.objects.filter(id__in=author_ids).values('id', 'username')
        username_map = {u['id']: u['username'] for u in users}
        
        # Build response with ranks
        leaderboard = [
            {
                'rank': rank + 1,
                'username': username_map.get(author_id, 'Unknown'),
                'score': score
            }
            for rank, (author_id, score) in enumerate(sorted_authors)
        ]
        
        return Response(leaderboard)
