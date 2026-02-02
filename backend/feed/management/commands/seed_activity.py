"""
Django Management Command to seed activity for leaderboard demonstration.

Creates users, posts, comments, and strategically distributed votes
to showcase the 24h leaderboard feature.

Usage: python manage.py seed_activity
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from feed.models import User, Post, Comment, Vote


class Command(BaseCommand):
    help = 'Seed database with activity to demonstrate the leaderboard'

    def handle(self, *args, **options):
        self.stdout.write('🎯 Seeding activity for leaderboard...\n')

        # Create users
        users = self._create_users()
        alice, bob, charlie, diana, eve = users[:5]
        
        # Create posts with tech-twitter style content
        posts = self._create_posts(users)
        
        # Add comments
        self._create_comments(posts, users)
        
        # Strategic voting to create leaderboard rankings
        self._create_strategic_votes(users, posts)

        self.stdout.write(self.style.SUCCESS('\n✅ Activity seeded successfully!'))
        self.stdout.write(f'   Posts: {Post.objects.count()}')
        self.stdout.write(f'   Comments: {Comment.objects.count()}')
        self.stdout.write(f'   Votes: {Vote.objects.count()}')
        self.stdout.write('\n🏆 Expected Leaderboard:')
        self.stdout.write('   #1 alice (most likes)')
        self.stdout.write('   #2 bob')
        self.stdout.write('   #3+ others')

    def _create_users(self):
        """Ensure core users exist."""
        self.stdout.write('Creating users...')
        
        usernames = ['alice', 'bob', 'charlie', 'diana', 'eve']
        users = []
        
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.capitalize(),
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
        
        return users

    def _create_posts(self, users):
        """Create tech-twitter style posts."""
        self.stdout.write('Creating posts...')
        
        alice, bob, charlie, diana, eve = users[:5]
        
        post_data = [
            (alice, "Just shipped my first Django app! The DRF serializers are amazing once you understand them. 🚀"),
            (alice, "Hot take: PostgreSQL > MySQL for anything beyond a simple blog. The JSONB support alone is worth it."),
            (alice, "TIL about Django's select_for_update(). Game changer for handling race conditions in voting systems."),
            (bob, "Why is CSS so hard? Spent 3 hours centering a div today. 😭"),
            (bob, "Python 3.11 speed improvements are real. Just migrated our codebase and seeing 25% faster API responses."),
            (bob, "Unpopular opinion: Docker is overkill for most hobby projects. Sometimes a virtualenv is all you need."),
            (charlie, "React Server Components are confusing but powerful. The mental model shift is real."),
            (charlie, "Just discovered TanStack Query. Why did I ever manage server state manually? 🤦"),
            (diana, "Tailwind CSS changed how I think about styling. Utility-first > component libraries."),
            (eve, "Deployed to Render today. Free tier PostgreSQL + automatic deploys = chef's kiss 👨‍🍳"),
        ]
        
        posts = []
        for author, content in post_data:
            post = Post.objects.create(author=author, content=content)
            posts.append(post)
        
        return posts

    def _create_comments(self, posts, users):
        """Add realistic comments to posts."""
        self.stdout.write('Creating comments...')
        
        comment_templates = [
            "This is so relatable! Had the same experience last week.",
            "Great insight! Bookmarking this for later.",
            "100% agree. Been saying this for years.",
            "Interesting perspective. I might try this approach.",
            "Thanks for sharing! Really helpful.",
            "Couldn't agree more! 🙌",
            "This is the way.",
            "Facts. No cap. 💯",
        ]
        
        for post in posts:
            # Add 1-3 comments per post
            num_comments = random.randint(1, 3)
            commenters = [u for u in users if u != post.author]
            
            for _ in range(num_comments):
                Comment.objects.create(
                    post=post,
                    author=random.choice(commenters),
                    content=random.choice(comment_templates)
                )

    def _create_strategic_votes(self, users, posts):
        """Create votes to make alice #1 and bob #2 on leaderboard."""
        self.stdout.write('Creating strategic votes for leaderboard...')
        
        alice, bob, charlie, diana, eve = users[:5]
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        # Get posts by author
        alice_posts = [p for p in posts if p.author == alice]
        bob_posts = [p for p in posts if p.author == bob]
        
        # Strategy: Alice gets lots of post likes (5 points each)
        # bob, charlie, diana all like alice's posts
        for post in alice_posts:
            for voter in [bob, charlie, diana, eve]:
                self._create_vote(voter, post_ct, post.id)
        
        # Bob gets some likes (will be #2)
        # alice, charlie, eve like bob's posts
        for post in bob_posts:
            for voter in [alice, charlie, eve]:
                self._create_vote(voter, post_ct, post.id)
        
        # Charlie and Diana get some likes too
        charlie_posts = [p for p in posts if p.author == charlie]
        diana_posts = [p for p in posts if p.author == diana]
        
        for post in charlie_posts:
            for voter in [alice, bob]:
                self._create_vote(voter, post_ct, post.id)
        
        for post in diana_posts:
            self._create_vote(alice, post_ct, post.id)
        
        # Add some comment likes too
        all_comments = list(Comment.objects.all())
        alice_comments = [c for c in all_comments if c.author == alice]
        bob_comments = [c for c in all_comments if c.author == bob]
        
        # Extra likes for alice's comments
        for comment in alice_comments[:3]:
            for voter in [bob, charlie, diana]:
                if voter != comment.author:
                    self._create_vote(voter, comment_ct, comment.id)
        
        # Some likes for bob's comments
        for comment in bob_comments[:2]:
            for voter in [alice, eve]:
                if voter != comment.author:
                    self._create_vote(voter, comment_ct, comment.id)
        
        self.stdout.write(f'   Created votes for strategic leaderboard ranking')

    def _create_vote(self, user, content_type, object_id):
        """Create a vote if it doesn't exist."""
        Vote.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            defaults={'value': 1}
        )
