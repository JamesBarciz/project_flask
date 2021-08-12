from functools import partial
from typing import NoReturn

import numpy as np

from src.orm_model import DB, Author, Tweet


def upsert_user(author_handle: str, twitter_api, spacy_model) -> NoReturn:
    """Allows us to UPdate or inSERT a Twitter author"""
    twitter_author = twitter_api.get_user(author_handle)

    if Author.query.get(twitter_author.id):
        db_author = Author.query.get(twitter_author.id)
    else:
        db_author = Author(id=twitter_author.id, name=author_handle)
        DB.session.add(db_author)

    author_tweet_ids = [tweet.id for tweet in Tweet.query.filter(Tweet.author_id == db_author.id)]

    # partial creates a function with preset params/kwargs
    author_tweet_func = partial(twitter_author.timeline, count=200, exclude_replies=True,
                                include_rts=False, tweet_mode='extended')

    if len(author_tweet_ids) > 0:
        last_tweet_stored_id = np.max(author_tweet_ids)
        author_tweets = author_tweet_func(since_id=last_tweet_stored_id)
    else:
        author_tweets = author_tweet_func()

    for tweet in author_tweets:
        vectorized_tweet = spacy_model(tweet.full_text).vector
        db_tweet = Tweet(id=tweet.id, body=tweet.full_text, vect=vectorized_tweet)
        db_author.tweets.append(db_tweet)
        DB.session.add(db_tweet)

    DB.session.commit()
