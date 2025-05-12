from scraipe.async_classes import IAsyncScraper
from asyncpraw import Reddit
from scraipe.classes import ScrapeResult
import io

from typing import Optional, List, Literal, get_args
CommentInclusion = Literal['content','metadata', 'both', 'none']

USER_AGENT = "Scraipe RedditSubmissionScraper (by u/PeterTigerr)"
class RedditSubmissionScraper(IAsyncScraper):
    """
    A class that scrapes Reddit submissions using the asyncpraw library. 
    """
    client_id:str
    client_secret:str
    comment_inclusion:CommentInclusion
    def __init__(self, client_id, client_secret, comment_inclusion:CommentInclusion='content'):
        """
        Initialize the RedditSubmissionScraper.
        
        Args:
            client (Reddit): An instance of the asyncpraw Reddit client.
            comment_inclusion (CommentInclusion): Setting for how to include comments in the ScrapeResult.
                Options are 'content', 'metadata', 'both', or 'none'.
        """
        # validate comment_inclusion
        if comment_inclusion not in get_args(CommentInclusion):
            raise ValueError(f"comment_inclusion must be one of {get_args(CommentInclusion)}")
        self.comment_inclusion = comment_inclusion
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = USER_AGENT
        
    async def async_scrape(self, link) -> ScrapeResult:
        """
        Scrape a reddit submission. 
        
        Args:
            link (str): The link to the submission to scrape.
        """
        client = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )
        
        async with client:
            # Scrape submission 
            submission = await client.submission(url=link)
            
            metadata = {}
            metadata['title'] = submission.title
            metadata['author'] = submission.author.name if submission.author else None
            metadata['score'] = submission.score
            metadata['num_comments'] = submission.num_comments
            metadata['created_utc'] = submission.created_utc
            metadata['url'] = submission.url
            metadata['selftext'] = submission.selftext
            metadata['subreddit'] = submission.subreddit.display_name
            
            content = submission.selftext
            if self.comment_inclusion != 'none':
                comments = []
                await submission.comments.replace_more(limit=None)
                for comment in submission.comments.list():
                    comments.append({
                        'author': comment.author.name if comment.author else None,
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc
                    })
                    
                if self.comment_inclusion in ['metadata', 'both']:
                    metadata['comments'] = comments
                if self.comment_inclusion in ['content', 'both']:
                    # Append comments to content with custom, lightweight formatting
                    buffer = io.StringIO()
                    buffer.write(content)
                    buffer.write("\n\n===Comments===\n")
                    # Recursive function to walk through comments
                    def walk(comment, indent=0):
                        prefix = " " * (indent * 4)  # 4 spaces per depth level
                        # header with author and score
                        buffer.write(f"{prefix}- u/{comment.author}:\n")
                        # comment body, prefix each line
                        for line in comment.body.splitlines():
                            buffer.write(f"{prefix}    {line}\n")
                        # recurse into replies
                        for reply in comment.replies:
                            walk(reply, indent + 1)
                    # Walk each top‑level comment
                    for top in submission.comments:
                        walk(top, indent=0)
                        
                    # Get the content from the StringIO buffer
                    content = buffer.getvalue()
                    buffer.close()
                    
            return ScrapeResult.succeed(link=link, content=content, metadata=metadata)