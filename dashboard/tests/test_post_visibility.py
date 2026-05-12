"""
Bug Condition Exploration Property Test for Post Visibility

This test verifies that published posts are correctly passed to the template
and rendered in the HTML. The actual bug (JavaScript hiding cards) cannot be
tested with Django's test client, but this test confirms the backend is working.

On unfixed code with backend issues, this test would FAIL.
For the JavaScript bug, manual testing or Selenium would be needed.
"""

from django.test import TestCase, Client
from django.utils import timezone
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from dashboard.models import Post
import re
import string


class PostVisibilityBugExplorationTest(HypothesisTestCase):
    """
    Property test to explore the bug condition where published posts
    don't appear on the index page.
    
    This test verifies:
    1. Posts are correctly fetched from database
    2. Posts are passed to template context
    3. Posts are rendered in HTML (before JavaScript executes)
    
    Note: The actual bug is in JavaScript (showCards() function hiding cards),
    which cannot be tested with Django's test client. This test confirms the
    backend and template rendering are working correctly.
    
    **Validates: Bug Condition - Backend correctly provides published posts**
    """
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    @given(
        num_posts=st.integers(min_value=1, max_value=6),  # Limit to 6 since view returns [:6]
        title_base=st.text(
            alphabet=string.ascii_letters + string.digits + ' ',
            min_size=5,
            max_size=30
        ),
        content_base=st.text(
            alphabet=string.ascii_letters + string.digits + ' ',
            min_size=10,
            max_size=100
        )
    )
    @settings(max_examples=15, deadline=5000)
    def test_published_posts_in_context_and_html(self, num_posts, title_base, content_base):
        """
        Property: When published posts exist in the database, they should:
        1. Be fetched by the view
        2. Be passed to the template context
        3. Be rendered in the HTML (before JavaScript executes)
        
        This confirms the backend is working. The JavaScript bug (hiding cards)
        would need browser automation testing to detect.
        
        **Validates: Bug Condition - Backend provides posts correctly**
        """
        # Clean up any existing posts
        Post.objects.all().delete()
        
        # Sanitize and validate inputs
        title = title_base.strip()
        content = content_base.strip()
        assume(len(title) >= 3)
        assume(len(content) >= 5)
        
        # Create published posts with unique titles
        created_posts = []
        for i in range(num_posts):
            post = Post.objects.create(
                title=f"{title}_{i}",
                content=f"{content}_{i}",
                category='general',
                target_audience='all',
                status='published',
                created_at=timezone.now()
            )
            created_posts.append(post)
        
        # Fetch the index page
        response = self.client.get('/')
        
        # Verify response is successful
        self.assertEqual(response.status_code, 200)
        
        # Property 1: Posts should be in the context (view returns [:6])
        self.assertIn('posts', response.context)
        context_posts = list(response.context['posts'])
        expected_count = min(num_posts, 6)  # View limits to 6 posts
        self.assertEqual(
            len(context_posts),
            expected_count,
            f"Expected {expected_count} posts in context, got {len(context_posts)}"
        )
        
        # Property 2: Each post should be rendered in the HTML
        html_content = response.content.decode('utf-8')
        
        for post in created_posts:
            # Check if post title appears in the HTML
            self.assertIn(
                post.title,
                html_content,
                f"Published post '{post.title}' should appear in index page HTML"
            )
        
        # Property 3: Fallback cards should NOT be rendered when posts exist
        # The fallback cards are inside {% if not posts %} block
        fallback_indicators = [
            'Higalaay sa Norsu/ Acquintance Party 2025',
            'Grand convocation, awarding ceremonies',
            'NORSU BSC INTRAMURALS CELEBRATION'
        ]
        
        # Check if any fallback card text appears in the HTML
        fallback_found = []
        for indicator in fallback_indicators:
            if indicator in html_content:
                fallback_found.append(indicator)
        
        # Fallback cards should not be in HTML when posts exist
        self.assertEqual(
            len(fallback_found),
            0,
            f"Fallback cards should not be rendered when posts exist. Found: {fallback_found}"
        )
        
        # Property 4: Dynamic post cards should be present in HTML
        # Count how many uv-news-card divs are in the HTML
        card_count = html_content.count('class="uv-news-card"')
        self.assertGreaterEqual(
            card_count,
            num_posts,
            f"Expected at least {num_posts} news cards in HTML, found {card_count}"
        )
    
    @given(
        title_base=st.text(
            alphabet=string.ascii_letters + string.digits + ' ',
            min_size=5,
            max_size=30
        ),
        content_base=st.text(
            alphabet=string.ascii_letters + string.digits + ' ',
            min_size=10,
            max_size=100
        )
    )
    @settings(max_examples=10, deadline=5000)
    def test_single_published_post_backend_works(self, title_base, content_base):
        """
        Property: Even a single published post should be correctly handled
        by the backend and rendered in HTML.
        
        This is a critical edge case - if there's only one post, the backend
        should still provide it to the template correctly.
        
        **Validates: Bug Condition - Single post backend handling**
        """
        # Clean up
        Post.objects.all().delete()
        
        # Sanitize and validate inputs
        title = title_base.strip()
        content = content_base.strip()
        assume(len(title) >= 3)
        assume(len(content) >= 5)
        
        # Create a single published post
        post = Post.objects.create(
            title=title,
            content=content,
            category='general',
            target_audience='all',
            status='published',
            created_at=timezone.now()
        )
        
        # Fetch the index page
        response = self.client.get('/')
        html_content = response.content.decode('utf-8')
        
        # The post title should be in the HTML
        self.assertIn(
            post.title,
            html_content,
            f"Single published post '{post.title}' should be in HTML"
        )
        
        # The post should be in the context
        self.assertIn('posts', response.context)
        context_posts = list(response.context['posts'])
        self.assertEqual(len(context_posts), 1, "Should have exactly 1 post in context")
        self.assertEqual(context_posts[0].title, post.title, "Post in context should match created post")
