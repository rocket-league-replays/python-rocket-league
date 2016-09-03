import requests
from rlapi import VERSION


class RocketLeagueAPI(object):

    PLATFORMS = ['steam', 'ps4', 'xboxone']
    STAT_TYPES = ['assists', 'goals', 'mvps', 'saves', 'shots', 'wins']
    PLAYLISTS = [10, 11, 12, 13]

    API_VERSION = '1'
    API_BASE_URL = 'https://api.rocketleaguegame.com/api/v' + API_VERSION + '/'

    def __init__(self, token=None, *args, **kwargs):
        self.TOKEN = token
        self.DEBUG_REQUEST = kwargs.get('debug_request', False)
        self.DEBUG_RESPONSE = kwargs.get('debug_response', False)

    def verify_platform(self, platform):
        assert platform in self.PLATFORMS

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
        request_url = self.API_BASE_URL + endpoint + '/'

        if self.DEBUG_REQUEST:
            return request_method, request_url, data

        request = getattr(requests, request_method.lower())(request_url, headers={
            'Authorization': 'Token ' + self.TOKEN,
            'User-Agent': 'python-rocket-league ' + '.'.join(str(ver) for ver in VERSION),
        }, data=data)

        # Allow developers to look into the Response object.
        if self.DEBUG_RESPONSE:
            return request

        return request.json()

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
