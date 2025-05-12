from async_classes import IAsyncScraper
from asyncpraw import Reddit
from classes import ScrapeResult
import io

from typing import Optional, List, Literal, get_args
CommentInclusion = Literal['content','metadata', 'both', 'none']

class RedditPostScraper(IAsyncScraper):
    """
    A class that scrapes Reddit post links using the asyncpraw library. 
    """
    
    client:Reddit
    comment_inclusion:CommentInclusion
    def __init__(self, client:Reddit, comment_inclusion:CommentInclusion='content'):
        """
        Initialize the RedditPostScraper.
        
        Args:
            client (Reddit): An instance of the asyncpraw Reddit client.
            comment_inclusion (CommentInclusion): Setting for how to include comments in the ScrapeResult.
                Options are 'content', 'metadata', 'both', or 'none'.
        """
        self.client = client
        # validate comment_inclusion
        if comment_inclusion not in get_args(CommentInclusion):
            raise ValueError(f"comment_inclusion must be one of {get_args(CommentInclusion)}")
        self.comment_inclusion = comment_inclusion
        
    async def async_scrape(self, link) -> ScrapeResult:
        """
        Scrape a reddit post. 
        
        Args:
            link (str): The link post to scrape.
        """
        
        # Scrape post 
        submission = await self.client.submission(url=link)
        
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
                buf = io.StringIO(content)
                buf.write("\n\n=== Comments ===\n\n")

                # Recursive function to walk through comments
                def walk(comment, indent=0):
                    prefix = " " * (indent * 4)  # 4 spaces per depth level
                    # header with author and score
                    buf.write(f"{prefix}- u/{comment.author}:\n")
                    # comment body, prefix each line
                    for line in comment.body.splitlines():
                        buf.write(f"{prefix}    {line}\n")
                    # recurse into replies
                    for reply in comment.replies:
                        walk(reply, indent + 1)
                # Walk each top‑level comment
                for top in submission.comments:
                    walk(top, indent=0)
                    
                # Get the content from the StringIO buffer
                content = buf.getvalue()
                buf.close()
                
        return ScrapeResult.succeed(link=link, content=content, metadata=metadata)