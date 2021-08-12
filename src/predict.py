from src.orm_model import Tweet, Author
import pandas as pd
from sklearn.linear_model import LogisticRegression
# import pickle


def get_most_likely_author(tweet_body, spacy_model):
    authors = Author.query.all()
    features = pd.DataFrame()
    target = pd.Series()
    for a in authors:
        for t in a.tweets:
            if not len(features) > 0:
                features = pd.DataFrame(t.vect).T
            else:
                features = pd.concat([pd.DataFrame(t.vect).T, features])
            target = target.append(pd.Series([a.name]))
    target.reset_index(inplace=True, drop=True)
    features.reset_index(inplace=True, drop=True)
    model = LogisticRegression()
    model.fit(X=features, y=target)
    # with open('model', 'wb+') as f:
    #     pickle.dump(model, f)
    # with open('model', 'rb') as f:
    #     unpickler = pickle.Unpickler(f)
    #     model = unpickler.load()
    likely_author = model.predict([spacy_model(tweet_body).vector])
    return likely_author
