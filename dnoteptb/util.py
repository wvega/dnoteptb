
# coding: utf-8
import calendar
import datetime
import random

from google.appengine.api import memcache
from google.appengine.ext import db

from django.utils import simplejson

from dnoteptb.models import Game, Hit

# Memcache

def get_running_game():
    game = memcache.get('running-game')
    if game is None:
        game = Game.all().filter('running', True).order('start').get()
        if game is None:
            game = Game(name='The First Game', start=datetime.datetime.now(), running=True)
            game.put()
        memcache.set('running-game', game)
    return game


def get_players(game):
    players = memcache.get('players-%s' % game.key())
    if players is None:
        players = game.players.order('-score')
        memcache.set('players-%s' % game.key(), players)
    return players


def get_last_hit(game):
    last = memcache.get('last-hit-%s' % game.key())
    if last is None:
        last = Hit.all().ancestor(game).order('-created').get()
        memcache.set('last-hit-%s' % game.key(), last)
    return last

#

def prepare_scores_stats(hits):
    previous_user, current_user = (None, None)
    last_score, score_increment, score_decrement = (None, None, None)
    min_score, max_score = (0, 0)
    start_date, last_date = (None, None)
    index = 0;

    # Data passed to Flot library
    # [{'legend': '', 'data': [(x1, y1), (x2, y2), ...]}, {'legend': '', 'data': [(x1, y1), (x2, y2), ...]}, ...]
    data = []
    # Index table
    # {'username': data-index}
    players = {}

    # Create chart data from Datastore registers
    for hit in hits:
        current_user = hit.player.user.username
        hit_date = calendar.timegm(hit.start.utctimetuple()) * 1000
        if start_date == None:
            start_date = hit_date
        if current_user not in players:
            players[current_user] = index
            data.append({'label': current_user, 'data': [(hit_date, 0)]})
            index += 1

        if last_score is not None and current_user != previous_user:
            last_date = hit_date

            # new winner player's score
            score_increment = data[players[current_user]]['data'][-1][1] + last_score
            data[players[current_user]]['data'].append((last_date, score_increment))
            if score_increment > max_score:
                max_score = score_increment

            # new loser player's score
            if previous_user is not None:
                score_decrement = data[players[previous_user]]['data'][-1][1] - last_score
                data[players[previous_user]]['data'].append((last_date, score_decrement))
                if score_decrement < min_score:
                    min_score = score_decrement

        if hit.end is not None:
            last_score = timedelta2seconds(hit.end - hit.start)
            hit.score = last_score
        previous_user = current_user

    return simplejson.dumps({'data': data, 'min': min_score > 0 and min_score * 0.94 or min_score * 1.06,
                                           'max': max_score > 0 and max_score * 1.06 or max_score * 0.94,
                                           'start': start_date and start_date * 0.99999,
                                           'end': last_date and last_date * 1.00001})

#

def timedelta2seconds(delta):
    return delta.days * 84600 + delta.seconds + delta.microseconds / 1000000

def randcolor(color=""):
    if len(color) == 6:
        return color
    return randcolor(color + hex(random.randrange(0, 255))[2:][:1])