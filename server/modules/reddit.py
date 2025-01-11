import asyncpraw
import os

# Reddit API credentials from environment variables
reddit = asyncpraw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

# Subreddit and post details
subreddit_name = os.getenv('REDDIT_SUBREDDIT')

# Submit the post
async def post_to_reddit(title, text):
    subreddit = await reddit.subreddit(subreddit_name)
    post = await subreddit.submit(f'Lekker Herhalen - {title}', selftext=text)
    await post.load()
    print(f'Posted successfully: {post.title} (URL: {post.url})')
    return post
