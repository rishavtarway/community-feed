"""
Django Management Command to seed the database with realistic test data.

Creates:
- 10 users (alice, bob, charlie, etc.)
- 15 posts with varying content
- A "mega thread" with 4-5 levels of nested comments
- Votes distributed to test the leaderboard (alice/bob get most likes)

Usage: python manage.py seed_data
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from feed.models import User, Post, Comment, Vote


class Command(BaseCommand):
    help = 'Seed the database with realistic test data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...\n')

        # Clear existing data (optional - comment out to append)
        self.stdout.write('Clearing existing data...')
        Vote.objects.all().delete()
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create users
        users = self._create_users()
        
        # Create posts
        posts = self._create_posts(users)
        
        # Create the "mega thread" on the first post
        self._create_mega_thread(posts[0], users)
        
        # Create some regular comments on other posts
        self._create_regular_comments(posts[1:], users)
        
        # Create votes (likes) - bias towards alice and bob
        self._create_votes(users, posts)

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(f'   Users: {User.objects.count()}')
        self.stdout.write(f'   Posts: {Post.objects.count()}')
        self.stdout.write(f'   Comments: {Comment.objects.count()}')
        self.stdout.write(f'   Votes: {Vote.objects.count()}')

    def _create_users(self):
        """Create 10 test users."""
        self.stdout.write('Creating users...')
        
        usernames = [
            'alice', 'bob', 'charlie', 'diana', 'eve',
            'frank', 'grace', 'henry', 'iris', 'jack'
        ]
        
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
        """Create 15 posts with varying content."""
        self.stdout.write('Creating posts...')
        
        post_contents = [
            "Just discovered an amazing new coffee shop downtown! ☕ The atmosphere is incredible and their cold brew is next level. Anyone else been there?",
            
            "Hot take: tabs are better than spaces. Fight me. 😤\n\nBut seriously, I've been using tabs for indentation and spaces for alignment, and it's been working great for accessibility.",
            
            "Finally finished my side project after 6 months! It's a habit tracker app built with React and Django. The hardest part was staying motivated when no one was using it yet.",
            
            "TIL that PostgreSQL has a 'LISTEN/NOTIFY' feature for real-time updates without polling. Mind = blown 🤯",
            
            "What's everyone's favorite VS Code extension? I'll start: GitLens completely changed how I navigate codebases.",
            
            "Unpopular opinion: Most design patterns are over-engineered for the problems they solve. Sometimes a simple function is all you need.",
            
            "Just had the best debugging experience of my life. The bug was a single missing comma in a JSON file. Two hours well spent. 🙃",
            
            "Looking for book recommendations! Currently reading 'Designing Data-Intensive Applications' and loving it. What else should be on my list?",
            
            "The amount of boilerplate needed to set up a simple CRUD app in 2024 is still ridiculous. We need better tooling.",
            
            "Shoutout to everyone who writes good documentation. You're the real heroes of the software industry. 📚",
            
            "Pro tip: Use `git stash -p` to selectively stash changes. It's a game changer when you're working on multiple features.",
            
            "Just realized I've been over-complicating my React state management. Sometimes useState is all you need. Not everything requires Redux or Zustand.",
            
            "Anyone else feel like they're constantly learning in this field? I've been coding for 10 years and still feel like a beginner sometimes.",
            
            "The best code is the code you don't have to write. Seriously, before adding a feature, ask if it's actually necessary.",
            
            "Weekend project idea: Build a CLI tool that generates commit messages using AI. Because writing 'fixed stuff' is getting old. 😅",
        ]
        
        posts = []
        for i, content in enumerate(post_contents):
            # Distribute posts among users
            author = users[i % len(users)]
            post = Post.objects.create(
                author=author,
                content=content
            )
            posts.append(post)
        
        return posts

    def _create_mega_thread(self, post, users):
        """Create a deeply nested comment tree (4-5 levels) on a single post."""
        self.stdout.write('Creating mega thread...')
        
        alice, bob, charlie, diana, eve = users[:5]
        
        # Level 1: Root comments
        c1 = Comment.objects.create(
            post=post,
            author=alice,
            content="This is such a great find! I've been looking for a new coffee spot. What's the name of the place?"
        )
        
        c2 = Comment.objects.create(
            post=post,
            author=bob,
            content="I think I know which one you're talking about. Is it the one on Main Street?"
        )
        
        # Level 2: Replies to c1
        c1_1 = Comment.objects.create(
            post=post,
            author=users[2],  # charlie
            parent=c1,
            content="It's called 'The Roasted Bean'. The owner is super friendly and they roast their own beans!"
        )
        
        c1_2 = Comment.objects.create(
            post=post,
            author=diana,
            parent=c1,
            content="I went there last week! The latte art is incredible. 🎨"
        )
        
        # Level 2: Replies to c2
        c2_1 = Comment.objects.create(
            post=post,
            author=post.author,  # Original poster responds
            parent=c2,
            content="Yes, that's the one! Have you tried their seasonal menu?"
        )
        
        # Level 3: Replies to c1_1
        c1_1_1 = Comment.objects.create(
            post=post,
            author=eve,
            parent=c1_1,
            content="Wait, they roast their own beans?! That's awesome. Do they sell bags to take home?"
        )
        
        c1_1_2 = Comment.objects.create(
            post=post,
            author=alice,
            parent=c1_1,
            content="Thanks for the name! Adding it to my list for this weekend."
        )
        
        # Level 3: Reply to c2_1
        c2_1_1 = Comment.objects.create(
            post=post,
            author=bob,
            parent=c2_1,
            content="Not yet! What do you recommend from the seasonal menu?"
        )
        
        # Level 4: Replies to c1_1_1
        c1_1_1_1 = Comment.objects.create(
            post=post,
            author=charlie,
            parent=c1_1_1,
            content="Yes! They have 250g and 500g bags. The Ethiopian single origin is my favorite."
        )
        
        # Level 4: Reply to c2_1_1
        c2_1_1_1 = Comment.objects.create(
            post=post,
            author=post.author,
            parent=c2_1_1,
            content="The pumpkin spice cold brew is amazing right now! Not too sweet like other places."
        )
        
        # Level 5: Deep reply
        c1_1_1_1_1 = Comment.objects.create(
            post=post,
            author=diana,
            parent=c1_1_1_1,
            content="Ethiopian coffee is the best! Have you tried their Yirgacheffe? It has these amazing fruity notes. ☕"
        )
        
        # Level 5: Another deep reply
        c1_1_1_1_2 = Comment.objects.create(
            post=post,
            author=eve,
            parent=c1_1_1_1,
            content="I'll definitely grab a bag next time. Thanks for the recommendation!"
        )
        
        self.stdout.write(f'   Created mega thread with {Comment.objects.filter(post=post).count()} comments')

    def _create_regular_comments(self, posts, users):
        """Create some regular comments on other posts."""
        self.stdout.write('Creating regular comments...')
        
        comment_templates = [
            "Great point! I totally agree with this.",
            "Hmm, I see it differently. Have you considered...?",
            "This is so relatable! 😂",
            "Thanks for sharing this. Really helpful!",
            "I've been thinking about this too. Any resources you'd recommend?",
            "100% agree. This needs more attention.",
            "Interesting perspective. Never thought of it that way.",
            "This made my day! 🙌",
        ]
        
        for post in posts[:8]:  # Add comments to first 8 posts
            # Add 1-3 root comments per post
            num_comments = random.randint(1, 3)
            for _ in range(num_comments):
                Comment.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=random.choice(comment_templates)
                )

    def _create_votes(self, users, posts):
        """Create votes to populate the leaderboard."""
        self.stdout.write('Creating votes...')
        
        alice, bob = users[0], users[1]
        other_users = users[2:]
        
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        # Strategy: Make alice's and bob's content receive the most votes
        # to ensure they appear at the top of the leaderboard
        
        # Get all posts and comments
        all_posts = list(Post.objects.all())
        all_comments = list(Comment.objects.all())
        
        # Vote on alice's content (posts and comments)
        alice_posts = [p for p in all_posts if p.author == alice]
        alice_comments = [c for c in all_comments if c.author == alice]
        
        for post in alice_posts:
            # Most users vote on alice's posts
            for voter in users[1:8]:  # 7 voters
                self._create_vote(voter, post_ct, post.id)
        
        for comment in alice_comments:
            # Several users vote on alice's comments
            for voter in random.sample(users[1:], min(5, len(users)-1)):
                self._create_vote(voter, comment_ct, comment.id)
        
        # Vote on bob's content
        bob_posts = [p for p in all_posts if p.author == bob]
        bob_comments = [c for c in all_comments if c.author == bob]
        
        for post in bob_posts:
            # Many users vote on bob's posts
            for voter in users[:1] + users[2:7]:  # 6 voters (including alice)
                self._create_vote(voter, post_ct, post.id)
        
        for comment in bob_comments:
            for voter in random.sample([u for u in users if u != bob], min(4, len(users)-1)):
                self._create_vote(voter, comment_ct, comment.id)
        
        # Some random votes for other users (fewer than alice/bob)
        other_posts = [p for p in all_posts if p.author not in [alice, bob]]
        other_comments = [c for c in all_comments if c.author not in [alice, bob]]
        
        for post in random.sample(other_posts, min(5, len(other_posts))):
            for voter in random.sample([u for u in users if u != post.author], 2):
                self._create_vote(voter, post_ct, post.id)
        
        for comment in random.sample(other_comments, min(8, len(other_comments))):
            voter = random.choice([u for u in users if u != comment.author])
            self._create_vote(voter, comment_ct, comment.id)

    def _create_vote(self, user, content_type, object_id):
        """Create a vote if it doesn't exist."""
        Vote.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            defaults={'value': 1}
        )
