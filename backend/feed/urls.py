"""
URL routing for the Feed API.

Endpoints:
- GET /api/posts/           - List posts (paginated)
- GET /api/posts/{id}/      - Retrieve post with nested comments
- POST /api/vote/           - Toggle vote on post/comment
- GET /api/leaderboard/     - Top 5 users by 24h karma
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, VoteView, LeaderboardView


router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
    path('vote/', VoteView.as_view(), name='vote'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
