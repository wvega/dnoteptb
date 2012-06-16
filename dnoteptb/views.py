# -*- coding: utf8 -*-
import calendar
import cgi
import datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from ragendja.template import render_to_response as render

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.template import Context, loader


from dnoteptb import util
from dnoteptb.clients import TwitterOAuthClient, consumer
from dnoteptb.models import User, Hit, Player, OAuthRequestToken
from dnoteptb.oauth.oauth import OAuthRequest, OAuthSignatureMethod_HMAC_SHA1

# constants

CALLBACK_URL = 'http://localhost:8000/ready/'
CALLBACK_URL = 'http://dnoteptb.appspot.com/ready/'

DNOTEPTB_OK = 1
DNOTEPTB_FIRST_PLAYER = 1 << 1
DNOTEPTB_TOO_SOON_ERROR = 1 << 2
DNOTEPTB_SAME_PLAYER = 1 << 3

# views

def index(request):
    user = None
    if request.session.get('token', None) is not None:
        client = TwitterOAuthClient(request)
        user = User.all().filter('token', request.session.get('token', None)).get()

        if user is None:
            return HttpResponseRedirect('/logout')

        # fill in missing information
        if user.name is None:
            token = user.OAuthToken()
            oauth_request = OAuthRequest.from_consumer_and_token(consumer, token=token, http_method='GET', http_url='http://twitter.com/account/verify_credentials.json')
            oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
            response = client.access_resource(oauth_request)
            info = simplejson.loads(response)
            user.name = info['name']
            user.timezone = info['time_zone']
            user.put()

    # find current game
    game = util.get_running_game()
    # find players
    players = util.get_players(game)
    # find last hit
    last = util.get_last_hit(game)

    if last is not None:
        delta = util.timedelta2seconds(datetime.datetime.now() - last.start)
        timestamp = calendar.timegm(last.start.utctimetuple())
    else:
        delta = 0
        timestamp = 0
    
    return render(request, 'index.html', {'user': user, 'players': players, 'last': last, 'delta': delta, 'timestamp': timestamp})


def press(request):
    if request.session.get('token', None) is None:
        return HttpResponseRedirect('/login/press')
    user = User.all().filter('token', request.session.get('token', None)).get()
    now = datetime.datetime.now()

    if user is None:
        return HttpResponseRedirect('/login/press')

    # stop @dgiraldo_ from cheating
    if user.username == 'unknown1902':
        return HttpResponseRedirect('/gotcha')

    game = util.get_running_game()

    player = Player.all().ancestor(game).filter('user', user).get()
    if player is None:
        player = Player(game=game, user=user, parent=game)
        player.put()
        memcache.delete('players-%s' % game.key())

    def transaction(game, player):
        # get previous hit
        previous = util.get_last_hit(game)

        if previous is None:
            # insert new hit and return
            hit = Hit(player=player, start=now, parent=player)
            hit.put()
            memcache.delete('last-hit-%s' % game.key())
            return DNOTEPTB_FIRST_PLAYER
        elif previous.player.key() == player.key():
            if (now - previous.start).seconds < 43200:
                return DNOTEPTB_TOO_SOON_ERROR

        # insert new hit
        hit = Hit(player=player, start=now, parent=player)
        hit.put()
        memcache.delete('last-hit-%s' % game.key())

        # mark previous hit as completed
        previous.end = now
        previous.completed = True
        previous.put()

        # an user doesn't get points if he/she was the last user who pressed the
        # button
        if player.key() == previous.player.key():
            return DNOTEPTB_SAME_PLAYER

        # increase current player's score
        score = util.timedelta2seconds(previous.end - previous.start)
        player.score += score
        player.put()
        # decrease previous player's score
        previous.player.score -= score
        previous.player.put()
        
        memcache.delete('players-%s' % game.key())
        
        return DNOTEPTB_OK
        
    status = db.run_in_transaction(transaction, game=game, player=player)

    return HttpResponseRedirect('/')

def status(request, username='', time=0):
    game = util.get_running_game()
    last = util.get_last_hit(game)
    user = last.player.user
    players = None

    response = {'modified': False}
    delta = util.timedelta2seconds(datetime.datetime.now() - last.start)
    timestamp = calendar.timegm(last.start.utctimetuple())
    
    if username != '' and username != user.username:
        players = util.get_players(game)
        template = loader.get_template('players.html')
        context = Context({'players': players})
        response['html'] = template.render(context)
        response['modified'] = True
    elif long(time, 10) != timestamp:
        response['modified'] = True

    if response['modified']:
        response.update({'user': {'link': 'http://twitter.com/%s' % user.username,
                                  'name': user.name,
                                  'username': '@%s' % user.username},
                         'delta': delta,
                         'timestamp': timestamp})

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


def login(request, action=''):
    user = User.all().filter('token', request.session.get('token', None)).get()
    if user is not None:
        return HttpResponseRedirect('/')
    client = TwitterOAuthClient(request)
    
    # get request token
    oauth_request = OAuthRequest.from_consumer_and_token(consumer, callback='%s%s' % (CALLBACK_URL, action), http_url=client.request_token_url)
    oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
    token = client.fetch_request_token(oauth_request)

    # save request token
    OAuthRequestToken.save(token)

    # authorize request token
    oauth_request = OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
    return client.authorize_token(oauth_request)


def logout(request):
    response = HttpResponseRedirect('/')
    request.session.flush()
    return response


def ready(request, action=''):
    if 'oauth_verifier' not in request.REQUEST:
        return HttpResponseRedirect('/error')

    client = TwitterOAuthClient(request)
    token = OAuthRequestToken.all().filter('token', request.REQUEST['oauth_token']).get().OAuthToken()
    verifier = request.REQUEST['oauth_verifier']

    # get access token
    oauth_request = OAuthRequest.from_consumer_and_token(consumer, token=token, verifier=verifier, http_url=client.access_token_url)
    oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    (token, response) = client.fetch_access_token(oauth_request)

    # get user credentials
    params = cgi.parse_qs(response.content, keep_blank_values=False)
    userid = int(params['user_id'][0])

    user = User.all().filter('userid', userid).get()
    if user is None:
        user = User(username=params['screen_name'][0], userid=userid, token=token.key, secret=token.secret)
    else:
        user.token = token.key
        user.secret = token.secret
    user.put()
    
    request.session['token'] = token.key

    return HttpResponseRedirect('/%s' % action)


def flush(request):
    if request.session.get('token', None) is None:
        return HttpResponseRedirect('/login/press')
    user = User.all().filter('token', request.session.get('token', None)).get()

    if user.username != 'wvega':
        return HttpResponseRedirect('/')

    if memcache.flush_all():
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/gotcha')

def reboot(request):
    if request.session.get('token', None) is None:
        return HttpResponseRedirect('/login/press')
    user = User.all().filter('token', request.session.get('token', None)).get()

    if user.username != 'wvega':
        return HttpResponseRedirect('/')

    game = util.get_running_game()
    game.running = False
    game.end = datetime.datetime.now()
    game.put()

    if memcache.flush_all():
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/gotcha')

def stats(request, refresh):
    game = util.get_running_game()
    scores = None

    try:
        refresh = bool(int(refresh))
    except:
        refresh = False

    if refresh:
        memcache.delete('scores-stats-%s' % game.key())
    else:
        scores = memcache.get('scores-stats-%s' % game.key())
    
    if scores is not None:
        return render(request, 'stats.html', {'scores': scores})

    hits = Hit.all().ancestor(game).order('start').fetch(1000)
    scores = util.prepare_scores_stats(hits)
    memcache.set('scores-stats-%s' % game.key(), scores, time=3600)

    return render(request, 'stats.html', {'scores': scores})

def gotcha(request):
    return render(request, 'gotcha.html')