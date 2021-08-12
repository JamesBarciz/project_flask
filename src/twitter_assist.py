import requests
import ast
from typing import NoReturn

import spacy.lang.en

from src.orm_model import DB, Author, Tweet


def upsert_author_assist(author_handle: str, spacy_model: spacy.lang.en.English) -> NoReturn:
    """
    This function will send a request to https://lambda-ds-twit-assist.herokuapp.com/ followed by the name of a Twitter
    user's handle.  In the server, the code will pull the last 200 items in the user's Twitter timeline then, exclude
    all replies and reTweets the user has made of those 200 items.

    The remaining user-made Tweets will return as JSON which will be handled below to extract the user's id and handle
    followed by the the id and full-text of the user's Tweet.  After the information is extracted, the NLP object
    created from an instantiated SpaCy model will accept the Tweet's full text as a parameter which allows us to extract
    a word embedding through the vector attribute (spacy_model(<tweet-text>).vector).

    Once all necessary information is extracted, they will be added to our SQLAlchemy ORM model and entered into our
    database.

    :param author_handle: str - A Twitter user's @ handle (without the '@' - ex. 'cher')
    :param spacy_model: spacy.lang.en.English - A customized word model instantiated through SpaCy (version 2.3.5)

    ** Performs an action but does not return anything **
    """

    # The URL of the server at which we will send a GET request
    HEROKU_URL = 'https://lambda-ds-twit-assist.herokuapp.com/user/'

    # This will evaluate our "stringified" JSON response into a Python dict object
    author = ast.literal_eval(requests.get(HEROKU_URL + author_handle).text)

    try:

        # If the Twitter author already exists in our database...
        if Author.query.get(author['twitter_handle']['id']):

            # Assign the author to a variable
            db_author = Author.query.get(author['twitter_handle']['id'])

        else:

            # Otherwise, create a new Author object with the author's ID and name
            db_author = Author(id=author['twitter_handle']['id'],
                               name=author['twitter_handle']['username'])

        # Add the author to the database
        DB.session.add(db_author)

        # Iterate over the list object containing Tweets
        for tweet in author['tweets']:

            # Create a SpaCy word embedding of the Tweet's full_text attribute
            vectorized_tweet = spacy_model(tweet['full_text']).vector

            # Create an instance of the Tweet object with the Tweet's id, text and vector representation
            db_tweet = Tweet(id=tweet['id'], body=tweet['full_text'], vect=vectorized_tweet)

            # Append the Tweet object to the Author as it has backreference capabilities
            db_author.tweets.append(db_tweet)

            # Add the tweet to the database
            DB.session.add(db_tweet)

    # If all else fails, raise an Exception error
    except Exception as e:
        raise e

    else:

        # Commit the additions to the database
        DB.session.commit()
