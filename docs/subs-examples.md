# Example Subscriptions

## Polling for New Results

This example is an infinite loop that polls the database for new results and then sends them through the subscription. This is not a very scalable method; however, it is simple and can help you get started fast before trying out more advanced mechanisms.

This example assumes you have BlogPost and Comment model with associated GraphQL types already created and want to watch for new comments.

```python
import asyncio

from django.utils import timezone


class CommentSubscription:
    watch_for_comments = graphene.Field(
        CommentType,
        post_id=graphene.Int(required=True),
        after=graphene.DateTime,
    )

    async def subscribe_watch_comments(root, info, post_id, after=None):
        if after is None:
            after = timezone.now()

        while 1:
            async for comment in Comment.objects.filter(blogpost_id=post_id, published__gt=after).order_by('published'):
                after = comment.published
                yield comment

            await asyncio.sleep(3)
```

## Listen/Notify with Postgres

*coming soon*
