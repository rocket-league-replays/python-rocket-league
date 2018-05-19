import json

import requests
from rlapi.constants import *


class RocketLeagueAPI(object):

    PLATFORMS = [
        PLATFORM_STEAM,
        PLATFORM_PLAYSTATION,
        PLATFORM_XBOX,
        PLATFORM_SWITCH,
    ]

    STAT_TYPES = [
        STAT_ASSISTS,
        STAT_GOALS,
        STAT_MVPS,
        STAT_SAVES,
        STAT_SHOTS,
        STAT_WINS,
    ]

    PLAYLISTS = [
        PLAYLIST_RANKED_DUELS,
        PLAYLIST_RANKED_DOUBLES,
        PLAYLIST_RANKED_SOLO_STANDARD,
        PLAYLIST_RANKED_STANDARD,
    ]

    def __init__(self, token=None, *args, **kwargs):
        self.TOKEN = token
        self.DEBUG_REQUEST = kwargs.get('debug_request', False)
        self.DEBUG_RESPONSE = kwargs.get('debug_response', False)

    def debug_request(self, response):
        req = response.request

        command = "curl -X {method} -H {headers} {data} '{uri}'"
        method = req.method
        uri = req.url
        data = "-d '{}'".format(req.body) if req.body else ''
        headers = ["'{0}: {1}'".format(k, v) for k, v in req.headers.items()]
        headers = " -H ".join(headers)
        return command.format(method=method, headers=headers, data=data, uri=uri)

    def verify_platform(self, platform):
        assert platform in self.PLATFORMS, "Platform should be {}. You provided {}.".format(
            ', '.join(self.PLATFORMS[:-1]) + ' or ' + self.PLATFORMS[-1],
            platform,
        )

    def verify_stat_type(self, stat_type):
        if stat_type is not None:
            assert stat_type in self.STAT_TYPES

    def verify_playlist(self, playlist):
        assert playlist in self.PLAYLISTS

    def verify_player_id(self, player_id, allow_multiple=True):
        request_method = 'GET'

        # Is the player_id iterable?
        if isinstance(player_id, list):
            if len(player_id) == 0:
                raise ValueError('You must supply at least one player ID.')
            elif len(player_id) == 1:
                player_id = player_id[0]
            elif len(player_id) > 100:
                raise ValueError('You may only supply up to 100 player IDs.')
            else:
                if not allow_multiple:
                    raise ValueError('You may only supply one player ID.')

                request_method = 'POST'
        elif len(str(player_id)) == 0:
            raise ValueError('You must supply at least one player ID.')

        if allow_multiple:
            return request_method, player_id

    def request(self, endpoint, request_method='GET', data=None):
        request_url = API_BASE_URL + endpoint + '/'

        if self.DEBUG_REQUEST:
            return request_method, request_url, data

        if request_method == 'POST':
            data = json.dumps(data)

        request = getattr(requests, request_method.lower())(request_url, headers={
            'Authorization': 'Token ' + self.TOKEN,
            'User-Agent': 'python-rocket-league ' + '.'.join(str(ver) for ver in VERSION),
        }, data=data)

        # Allow developers to look into the Response object.
        if self.DEBUG_RESPONSE:
            return request

        try:
            return request.json()
        except json.decoder.JSONDecodeError:
            return request.text

    # GET /api/v1/population/
    def get_population(self):
        return self.request('population')

    # GET /api/v1/regions/
    def get_regions(self):
        return self.request('regions')

    # GET /api/v1/<platform>/leaderboard/skills/<playlist>/
    def get_skill_leaderboard(self, platform, playlist):
        self.verify_platform(platform)
        self.verify_playlist(playlist)

        return self.request('{platform}/leaderboard/skills/{playlist}'.format(
            platform=platform,
            playlist=playlist,
        ))

    # GET /api/v1/<platform>/leaderboard/stats/
    # GET /api/v1/<platform>/leaderboard/stats/<stat_type>/
    def get_stats_leaderboard(self, platform, stat_type=None):
        self.verify_platform(platform)
        self.verify_stat_type(stat_type)

        return self.request('{platform}/leaderboard/stats{stat_type}'.format(
            platform=platform,
            stat_type='/' + stat_type if stat_type else '',
        ))

    # GET  /api/v1/<platform>/playerskills/<player_id>/
    # POST /api/v1/<platform>/playerskills/
    def get_player_skills(self, platform, player_id):
        self.verify_platform(platform)
        request_method, player_id = self.verify_player_id(player_id)

        data = None
        if request_method == 'POST':
            data = {
                'player_ids': player_id,
            }

        return self.request('{platform}/playerskills{player_id}'.format(
            platform=platform,
            player_id='/' + str(player_id) if request_method == 'GET' else '',
        ), request_method, data)

    # GET /api/v1/<platform>/playertitles/<player_id>/
    def get_player_titles(self, platform, player_id):
        self.verify_platform(platform)
        self.verify_player_id(player_id, allow_multiple=False)

        return self.request('{platform}/playertitles/{player_id}'.format(
            platform=platform,
            player_id=player_id,
        ))

    # GET  /api/v1/<platform>/leaderboard/stats/<stat_type>/<player_id>/
    # POST /api/v1/<platform>/leaderboard/stats/<stat_type>/
    def get_stats_value_for_user(self, platform, stat_type, player_id):
        self.verify_platform(platform)
        self.verify_stat_type(stat_type)
        request_method, player_id = self.verify_player_id(player_id)

        data = None
        if request_method == 'POST':
            data = {
                'player_ids': player_id,
            }

        return self.request('{platform}/leaderboard/stats/{stat_type}{player_id}'.format(
            platform=platform,
            stat_type=stat_type,
            player_id='/' + str(player_id) if request_method == 'GET' else '',
        ), request_method, data)

    # Custom method, smooths over the fact that `get_stats_value_for_user` only
    # returns one stat at a time.
    def get_stats_values_for_user(self, platform, player_id):
        # Disable the debug response system.
        debug_response = self.DEBUG_RESPONSE
        self.DEBUG_RESPONSE = False

        data = {
            stat_type: self.get_stats_value_for_user(platform, stat_type, player_id)
            for stat_type in self.STAT_TYPES
        }

        # Merge all of the stats together.
        player_stats = {}

        for stat_type in data:
            # If any of the values come back with a 500 error, exclude them.
            if data[stat_type] == "<h1>Server Error (500)</h1>":
                continue

            for player in data[stat_type]:
                if platform == 'steam':
                    online_id = player['user_id']
                else:
                    online_id = player['user_name']

                if online_id not in player_stats:
                    player_stats[online_id] = {}

                player_stats[online_id][player['stat_type']] = player['value']

        self.DEBUG_RESPONSE = debug_response

        return player_stats
