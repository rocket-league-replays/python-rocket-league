import requests


class RocketLeagueAPI(object):

    PLATFORMS = ['steam', 'ps4', 'xboxone']
    STAT_TYPES = ['assists', 'goals', 'mvps', 'saves', 'shots', 'wins']
    PLAYLISTS = [10, 11, 12, 13]

    API_BASE_URL = 'https://api.rocketleaguegame.com/api/'
    API_VERSION = '1'
    API_ENDPOINTS = {
        'player_skills': {
            'endpoint': 'playerskills',
            'methods': ['GET', 'POST'],
            'parameters': ['platform', 'player_id'],
        },
        'player_titles': {
            'endpoint': 'playertitles',
            'methods': ['GET'],
            'parameters': ['platform', 'player_id'],
        },
        'population': {
            'endpoint': 'population',
            'methods': ['GET'],
            'parameters': [],
        },
        'regions': {
            'endpoint': 'regions',
            'methods': ['GET'],
            'parameters': [],
        },
        'skill_leaderboard': {
            'endpoint': 'leaderboard/skills',
            'methods': ['GET'],
            'parameters': ['platform', 'playlist'],
        },
        'stats_leaderboard': [
            {
                'endpoint': 'leaderboard/stats',
                'methods': ['GET'],
                'parameters': ['platform'],
            },
            {
                'endpoint': 'leaderboard/stats',
                'methods': ['GET'],
                'parameters': ['platform', 'stat_type'],
            }
        ],
        'stats_value_for_user': {
            'endpoint': 'leaderboard/stats',
            'methods': ['GET', 'POST'],
            'parameters': ['platform', 'stat_type', 'player_id'],
        },
    }

    def __init__(self, token=None, *args, **kwargs):
        self.TOKEN = token
        self.DEBUG = kwargs.get('debug', False)
        self.DEBUG_REQUEST = kwargs.get('debug_request', False)

    def __dir__(self):
        return [
            'get_{}'.format(key)
            for key in self.API_ENDPOINTS.keys()
        ]

    def __getattr__(self, name):
        # Ensure the property starts with 'get_'.
        if not name.startswith('get_'):
            raise AttributeError("'{}' object has no attribute '{}'.{}".format(
                self.__class__.__name__,
                name,
                " Did you mean 'get_{}'?".format(name) if name in self.API_ENDPOINTS.keys() else '',
            ))

        # Ensure the endpoint exists.
        stripped_name = name[4:]

        if stripped_name not in self.API_ENDPOINTS:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__,
                name,
            ))

        self.endpoint = stripped_name
        return self.request_proxy

    def request_proxy(self, *args):
        # Turn the args into a list immediately, as we may need to mutate it.
        args = list(args)

        # Ensure we have the correct parameters.
        endpoint = self.API_ENDPOINTS[self.endpoint]

        if 'optional_parameters' in endpoint:
            assert (
                len(args) >= len(endpoint['parameters']) and
                len(args) <= len(endpoint['parameters']) + len(endpoint['optional_parameters'])
            )
        else:
            assert len(args) == len(endpoint['parameters'])

        request_method = 'GET'

        # Ensure we have a valid platform.
        if 'platform' in endpoint['parameters']:
            assert args[endpoint['parameters'].index('platform')] in self.PLATFORMS

        # Ensure we have a valid stat type.
        if 'stat_type' in endpoint['parameters']:
            assert args[endpoint['parameters'].index('stat_type')] in self.STAT_TYPES

        # Ensure we have a valid playlist.
        if 'playlist' in endpoint['parameters']:
            assert args[endpoint['parameters'].index('playlist')] in self.PLAYLISTS

        # Work out if we need to make a POST or GET request.
        if 'player_id' in endpoint['parameters']:
            # Which arg is the player_id?
            arg_index = endpoint['parameters'].index('player_id')

            # Is the player_id iterable?
            if isinstance(args[arg_index], list):
                if len(args[arg_index]) == 0:
                    raise ValueError('You must supply at least one player ID.')
                elif len(args[arg_index]) == 1:
                    args[arg_index] = args[arg_index][0]
                else:
                    request_method = 'POST'
            elif len(str(args[arg_index])) == 0:
                raise ValueError('You must supply at least one player ID.')

        if self.DEBUG:
            return endpoint, request_method, args

        return self.request(endpoint, request_method, args)

    def request(self, endpoint, request_method, args):
        request_url = '{}v{}/'.format(
            self.API_BASE_URL,
            self.API_VERSION,
        )

        if 'platform' in endpoint['parameters']:
            request_url += '{}/'.format(
                args[0]
            )

        request_url += '{}/'.format(
            endpoint['endpoint'],
        )

        # If the last parameter is `player_id`, then we need to append the rest
        # of the values except the last.

        if len(args) > 1:
            max_iterator = len(args)

            if endpoint['parameters'][-1] == 'player_id':
                max_iterator -= 1

            for index in range(1, max_iterator):
                request_url += '{}/'.format(
                    args[index],
                )

            if endpoint['parameters'][-1] == 'player_id' and request_method == 'GET':
                request_url += '{}/'.format(
                    args[-1],
                )

        data = None
        if request_method == 'POST':
            data = {
                'player_ids': args[endpoint['parameters'].index('player_id')]
            }

        if self.DEBUG:
            return request_method, request_url, data

        request = getattr(requests, request_method.lower())(request_url, headers={
            'Authorization': 'Token {}'.format(self.TOKEN)
        }, data=data)

        if self.DEBUG_REQUEST:
            return request

        return request.json()
