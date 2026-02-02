"""
Django Management Command to force-create a deeply nested comment thread.

Creates a 5-level deep conversation on the first post with multiple siblings
at each level to demonstrate recursive comment rendering.

Usage: python manage.py force_thread
"""

from django.core.management.base import BaseCommand
from feed.models import User, Post, Comment


class Command(BaseCommand):
    help = 'Create a 5-level deep nested comment thread on the first post'

    def handle(self, *args, **options):
        self.stdout.write('🧵 Creating mega thread...\n')

        # Get or create users for the conversation
        users = self._get_users()
        
        # Get the first post, or create one
        post = Post.objects.first()
        if not post:
            self.stdout.write('No posts found. Creating "The Mega Thread"...')
            post = Post.objects.create(
                author=users[0],
                content="🚀 The Mega Thread\n\nThis is a special post designed to showcase our deeply nested comment threading system. Every reply creates a new level of indentation, and we support up to 5+ levels deep!\n\nFeel free to explore the conversation below. 👇"
            )
        
        # Clear existing comments on this post
        deleted_count = Comment.objects.filter(post=post).delete()[0]
        if deleted_count:
            self.stdout.write(f'Cleared {deleted_count} existing comments.')
        
        # Create the nested thread structure
        self._create_thread(post, users)
        
        # Print results
        comment_count = Comment.objects.filter(post=post).count()
        self.stdout.write(self.style.SUCCESS(f'\n✅ Mega thread created!'))
        self.stdout.write(f'   Post ID: {post.id}')
        self.stdout.write(f'   Post Content: {post.content[:50]}...')
        self.stdout.write(f'   Total Comments: {comment_count}')
        self.stdout.write(f'\n👉 Visit: http://localhost:5173/post/{post.id}')

    def _get_users(self):
        """Get or create users for the conversation."""
        usernames = ['alice', 'bob', 'charlie', 'diana', 'eve']
        users = []
        for username in usernames:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            users.append(user)
        return users

    def _create_thread(self, post, users):
        """Create a 5-level deep nested thread with siblings at each level."""
        alice, bob, charlie, diana, eve = users
        
        # ============ LEVEL 1: Root Comments (3 siblings) ============
        self.stdout.write('Creating Level 1 (root comments)...')
        
        root1 = Comment.objects.create(
            post=post, author=alice, parent=None,
            content="This is incredible! I've been waiting for a proper threading system. The way it handles deep nesting is so clean. 🎉"
        )
        
        root2 = Comment.objects.create(
            post=post, author=bob, parent=None,
            content="I love how the comments indent automatically. Makes it super easy to follow conversations."
        )
        
        root3 = Comment.objects.create(
            post=post, author=charlie, parent=None,
            content="Quick question: is there a maximum depth limit for replies? I'm curious about the technical implementation."
        )
        
        # ============ LEVEL 2: Replies to root comments ============
        self.stdout.write('Creating Level 2 (first replies)...')
        
        # Replies to root1
        r1_1 = Comment.objects.create(
            post=post, author=bob, parent=root1,
            content="Totally agree! The UI is really intuitive. Have you tried clicking the like button yet?"
        )
        
        r1_2 = Comment.objects.create(
            post=post, author=diana, parent=root1,
            content="The color scheme for nested threads is 👌 - really helps distinguish between levels."
        )
        
        # Reply to root2
        r2_1 = Comment.objects.create(
            post=post, author=alice, parent=root2,
            content="Right? And it works great on mobile too. Responsive design FTW!"
        )
        
        # Reply to root3
        r3_1 = Comment.objects.create(
            post=post, author=eve, parent=root3,
            content="From what I can see, it uses an adjacency list model. The parent_id reference creates the tree structure."
        )
        
        # ============ LEVEL 3: Going deeper ============
        self.stdout.write('Creating Level 3 (deeper replies)...')
        
        # Replies to r1_1
        r1_1_1 = Comment.objects.create(
            post=post, author=charlie, parent=r1_1,
            content="The like button is so satisfying! Did you notice the little animation when you click it?"
        )
        
        r1_1_2 = Comment.objects.create(
            post=post, author=alice, parent=r1_1,
            content="Yes! And it updates the leaderboard in real-time. Check the sidebar! 📊"
        )
        
        # Reply to r1_2
        r1_2_1 = Comment.objects.create(
            post=post, author=eve, parent=r1_2,
            content="The border-left styling with the gradient is a nice touch. Very modern aesthetic."
        )
        
        # Reply to r3_1
        r3_1_1 = Comment.objects.create(
            post=post, author=charlie, parent=r3_1,
            content="Interesting! So the tree is built in memory rather than with recursive queries? That's smart for performance."
        )
        
        # ============ LEVEL 4: Even deeper ============
        self.stdout.write('Creating Level 4 (deep discussion)...')
        
        # Deep reply chain
        r1_1_1_1 = Comment.objects.create(
            post=post, author=diana, parent=r1_1_1,
            content="The animation is subtle but really adds to the user experience. Micro-interactions matter!"
        )
        
        r1_1_1_2 = Comment.objects.create(
            post=post, author=bob, parent=r1_1_1,
            content="I wonder if they're using Framer Motion or just CSS transitions. The smoothness is impressive."
        )
        
        # Technical discussion branch
        r3_1_1_1 = Comment.objects.create(
            post=post, author=eve, parent=r3_1_1,
            content="Exactly! It's the N+1 solution - fetch all comments in ONE query, build tree in Python. O(n) instead of O(n queries)."
        )
        
        # ============ LEVEL 5: Maximum depth showcase ============
        self.stdout.write('Creating Level 5 (maximum depth)...')
        
        r1_1_1_1_1 = Comment.objects.create(
            post=post, author=alice, parent=r1_1_1_1,
            content="Completely agree! It's these little details that separate good UX from great UX. This thread is getting deep! 🏊"
        )
        
        r1_1_1_1_2 = Comment.objects.create(
            post=post, author=charlie, parent=r1_1_1_1,
            content="We're at level 5 now! The indentation still looks clean. Great work on the CSS!"
        )
        
        r3_1_1_1_1 = Comment.objects.create(
            post=post, author=bob, parent=r3_1_1_1,
            content="That's brilliant! I was worried about performance with deep threads, but this approach is really elegant. 🧠"
        )
        
        r3_1_1_1_2 = Comment.objects.create(
            post=post, author=diana, parent=r3_1_1_1,
            content="Level 5 reached! The hash map approach for building the tree makes perfect sense. Computer science FTW!"
        )
        
        self.stdout.write(f'   Created comments at all 5 levels with siblings')
