from django.shortcuts import get_object_or_404, render

from blog.models import Comment, Post, Tag


def fetch_posts():
    return Post.objects.prefetch_related("author", "tags").popular()


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [{"title": tag.title} for tag in post.tags.all()],
        "first_tag_title": post.tags.first().title,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": tag.posts__count,
    }


def index(request):
    posts = fetch_posts()
    most_popular_posts = posts[:5].fetch_with_comments_count()
    most_fresh_posts = posts.order_by("-published_at")[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    posts = fetch_posts()
    post = get_object_or_404(posts, slug=slug)
    most_popular_posts = posts[:5].fetch_with_comments_count()

    comments = Comment.objects.prefetch_related("author").filter(post=post)
    serialized_comments = [
        {
            "text": comment.text,
            "published_at": comment.published_at,
            "author": comment.author.username,
        }
        for comment in comments
    ]

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": post.likes__count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [{"title": tag.title} for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)
    most_popular_tags = Tag.objects.popular()[:5]

    posts = fetch_posts()
    most_popular_posts = posts[:5].fetch_with_comments_count()
    related_posts = posts.filter(tags=tag)[:20].fetch_with_comments_count()

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
