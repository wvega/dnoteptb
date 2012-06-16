# -*- coding: utf8 -*-

from google.appengine.ext import db

from dnoteptb.oauth.oauth import OAuthToken

################################# OAuth Stuff ##################################

class OAuthRequestToken(db.Model):
    """OAuth Request Token."""
    token = db.StringProperty()
    secret = db.StringProperty()
    callback = db.StringProperty()
    callback_confirmed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def save(cls, token):
        callback_confirmed = (token.callback_confirmed.lower() == 'true') or False
        kw = dict(token=token.key, secret=token.secret, callback=token.callback, callback_confirmed=callback_confirmed)
        return OAuthRequestToken.get_or_insert(key_name=token.key, **kw)

    def OAuthToken(self):
        token = OAuthToken(key=self.token, secret=self.secret)
        if self.callback is not None:
            token.set_callback(self.callback)
        return token

################################# Users Stuff ##################################

class User(db.Model):
    userid = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    name = db.StringProperty(default=None, indexed=False)
    timezone = db.StringProperty(default=None)
    last = db.ReferenceProperty(indexed=False) # Reference to Hit
    created = db.DateTimeProperty(auto_now_add=True, indexed=False)
    # OAuthAcessToken
    token = db.StringProperty()
    secret = db.StringProperty()

    def OAuthToken(self):
        return OAuthToken(key=self.token, secret=self.secret)

################################## Game Stuff ##################################

class Game(db.Model):
    name = db.StringProperty(indexed=False)
    start = db.DateTimeProperty(required=True)
    end = db.DateTimeProperty()
    running = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)

class Player(db.Model):
    # Every Game has many Players
    game = db.ReferenceProperty(Game, collection_name='players', required=True)
    # Every User has a profile (Player) for each game he/she has participated on
    user = db.ReferenceProperty(User, collection_name='profiles', required=True)
    score = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class Hit(db.Model):
    player = db.ReferenceProperty(Player, collection_name='hits', required=True)
    start = db.DateTimeProperty(required=True)
    end = db.DateTimeProperty(default=None)
    completed = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)