import os

import pytest
from rlapi.client import RocketLeagueAPI

API_KEY = os.getenv('ROCKETLEAGUE_API_KEY', None)
authenticated = pytest.mark.skipif(
    not API_KEY,
    reason="Environment variable 'ROCKETLEAGUE_API_KEY' not set or empty."
)

rl = RocketLeagueAPI('', debug_request=True)

if API_KEY:
    rl_auth = RocketLeagueAPI(API_KEY, debug_response=True)


class TestAttributeValidation(object):

    def test_invalid_attribute(self):
        with pytest.raises(AttributeError):
            rl.test

        with pytest.raises(AttributeError):
            rl.test()

    def test_invalid_get(self):
        with pytest.raises(AttributeError) as e:
            rl.get_foo

        assert "AttributeError: 'RocketLeagueAPI' object has no attribute 'get_foo'" in str(e)

    def test_missing_parameters(self):
        with pytest.raises(TypeError):
            rl.get_player_skills()

    def test_invalid_platform(self):
        with pytest.raises(AssertionError):
            rl.get_player_skills('foo', 1)

    # GET /api/v1/<platform>/playerskills/<player_id>/
    def test_verify_player_id_valid(self):
        request_method, request_url, data = rl.get_player_skills('steam', 1)
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playerskills/1/'
        assert request_method == 'GET'
        assert data is None

    def test_verify_player_id_empty_list(self):
        with pytest.raises(ValueError):
            rl.get_player_skills('steam', [])

    def test_verify_player_id_empty_string(self):
        with pytest.raises(ValueError):
            rl.get_player_skills('steam', '')

    def test_verify_player_id_single_value(self):
        # Ensure the single ID is transformed into its non-list representation.
        request_method, request_url, data = rl.get_player_skills('steam', [1])
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playerskills/1/'
        assert request_method == 'GET'
        assert data is None

    def test_verify_player_id_too_many_values(self):
        # Ensure only a single ID is allowed.
        with pytest.raises(ValueError):
            rl.get_player_titles('steam', [1, 2])

        # Ensure a maximum of 100 player IDs are allowed.
        with pytest.raises(ValueError):
            rl.verify_player_id([1] * 101)

    # POST /api/v1/<platform>/playerskills/
    def test_verify_player_id_post(self):
        request_method, request_url, data = rl.get_player_skills('steam', [1, 2, 3])
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playerskills/'
        assert request_method == 'POST'
        assert data == {'player_ids': [1, 2, 3]}


class TestEndpoints(object):
    # Ensure we're hitting all of the correct endpoints.
    # GET  /api/v1/population/
    # GET  /api/v1/regions/
    # GET  /api/v1/<platform>/leaderboard/skills/<playlist>/
    # GET  /api/v1/<platform>/leaderboard/stats/
    # GET  /api/v1/<platform>/leaderboard/stats/<stat_type>/
    # GET  /api/v1/<platform>/leaderboard/stats/<stat_type>/<player_id>/
    # GET  /api/v1/<platform>/playerskills/<player_id>/
    # GET  /api/v1/<platform>/playertitles/<player_id>/

    def test_get_population(self):
        request_method, request_url, data = rl.get_population()
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/population/'
        assert data is None

    def test_get_regions(self):
        request_method, request_url, data = rl.get_regions()
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/regions/'
        assert data is None

    def test_skill_leaderboard(self):
        request_method, request_url, data = rl.get_skill_leaderboard('steam', 10)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/leaderboard/skills/10/'
        assert data is None

    def test_stats_leaderboard(self):
        request_method, request_url, data = rl.get_stats_leaderboard('steam')
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/leaderboard/stats/'
        assert data is None

    def test_stats_leaderboard_stat_type(self):
        request_method, request_url, data = rl.get_stats_leaderboard('steam', 'goals')
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/leaderboard/stats/goals/'
        assert data is None

    def test_stats_value_for_user(self):
        request_method, request_url, data = rl.get_stats_value_for_user('steam', 'goals', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/leaderboard/stats/goals/1/'
        assert data is None

    def test_player_skills(self):
        request_method, request_url, data = rl.get_player_skills('steam', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playerskills/1/'
        assert data is None

    def test_player_titles(self):
        request_method, request_url, data = rl.get_player_titles('steam', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playertitles/1/'
        assert data is None

    # Ensure we're hitting all of the correct endpoints.
    # POST /api/v1/<platform>/leaderboard/stats/<stat_type>/
    # POST /api/v1/<platform>/playerskills/
    def test_get_stats_value_for_user_post(self):
        request_method, request_url, data = rl.get_stats_value_for_user('steam', 'goals', [1, 2, 3])
        assert request_method == 'POST'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/leaderboard/stats/goals/'
        assert data == {'player_ids': [1, 2, 3]}

    def test_get_player_skills_post(self):
        request_method, request_url, data = rl.get_player_skills('steam', [1, 2, 3])
        assert request_method == 'POST'
        assert request_url == 'https://api.rocketleague.com/api/v1/steam/playerskills/'
        assert data == {'player_ids': [1, 2, 3]}


class TestUnauthenticatedCalls(object):

    def test_unauthenticated_call(self):
        rl = RocketLeagueAPI('', debug_response=True)
        response = rl.get_regions()

        assert response.status_code == 401
        assert response.text == '{"detail":"Invalid token header. No credentials provided."}'

    def test_unauthenticated_call_json(self):
        rl = RocketLeagueAPI('')
        response = rl.get_regions()

        assert response == {"detail": "Invalid token header. No credentials provided."}


# Test accounts:
# 76561198328949073: Doesn't own the game, non-ASCII chars in name.
# 76561198022035654: Player that's never logged in.
# 76561198008869772: Owns the game, has played.
# 76561198024807207: Random high-level player.

# Test real requests to the API.
@authenticated
class TestAuthenticatedCalls(object):

    def test_authenticated_get_population(self):
        response = rl_auth.get_population()

        assert response.status_code == 200
        assert len(response.json()) > 0
        assert 'Steam' in response.json()

    def test_authenticated_get_regions(self):
        response = rl_auth.get_regions()

        assert response.status_code == 200
        assert len(response.json()) > 0
        assert {'region': 'EU', 'platforms': 'Steam,PS4,XboxOne'} in response.json()

    def test_authenticated_get_skill_leaderboard_steam_10(self):
        response = rl_auth.get_skill_leaderboard('steam', 10)

        assert response.status_code == 200
        assert len(response.json()) == 100

    def test_authenticated_get_skill_leaderboard_ps4_11(self):
        response = rl_auth.get_skill_leaderboard('ps4', 11)

        assert response.status_code == 200
        assert len(response.json()) == 100

    def test_authenticated_get_skill_leaderboard_xboxone_12(self):
        response = rl_auth.get_skill_leaderboard('xboxone', 12)

        assert response.status_code == 200
        assert len(response.json()) == 100

    def test_authenticated_get_skill_leaderboard_steam_13(self):
        response = rl_auth.get_skill_leaderboard('steam', 13)

        assert response.status_code == 200
        assert len(response.json()) == 100

    def test_authenticated_get_stats_leaderboard_steam_assists(self):
        response = rl_auth.get_stats_leaderboard('steam', 'assists')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_stats_leaderboard_steam_goals(self):
        response = rl_auth.get_stats_leaderboard('steam', 'goals')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_stats_leaderboard_ps4_mvps(self):
        response = rl_auth.get_stats_leaderboard('ps4', 'mvps')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_stats_leaderboard_ps4_saves(self):
        response = rl_auth.get_stats_leaderboard('ps4', 'saves')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_stats_leaderboard_xboxone_shots(self):
        response = rl_auth.get_stats_leaderboard('xboxone', 'shots')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_stats_leaderboard_xboxone_wins(self):
        response = rl_auth.get_stats_leaderboard('xboxone', 'wins')

        assert response.status_code == 200
        assert 0 <= len(response.json()) <= 100

    def test_authenticated_get_player_skills_doesnt_own_game(self):
        response = rl_auth.get_player_skills('steam', 76561198328949073)

        assert response.status_code == 400
        assert response.json() == {'detail': 'Player ID/name not found'}

    def test_authenticated_get_player_skills_never_logged_in(self):
        response = rl_auth.get_player_skills('steam', 76561198022035654)

        assert response.status_code == 200
        assert response.json() == [
            {
                'player_skills': [],
                'user_id': 76561198022035654,
                'user_name': 'RocketLeagueReplays.com'
            }
        ]

    def test_authenticated_get_player_skills_with_data(self):
        response = rl_auth.get_player_skills('steam', 76561198024807207)
        data = response.json()[0]

        """
        [
            {
                'user_name': '[SA] Snaski',
                'user_id': 76561198024807207,
                'player_skills': [
                    {
                        'playlist': 10,
                        'tier': 0,
                        'skill': 164,
                        'tier_max': 0,
                        'matches_played': 1,
                        'division': 0
                    },
                    {
                        'playlist': 11,
                        'tier': 13,
                        'skill': 1294,
                        'tier_max': 13,
                        'matches_played': 106,
                        'division': 2
                    },
                    {
                        'playlist': 12,
                        'tier': 10,
                        'skill': 999,
                        'tier_max': 10,
                        'matches_played': 64,
                        'division': 3
                    },
                    {
                        'playlist': 13,
                        'tier': 12,
                        'skill': 1223,
                        'tier_max': 12,
                        'matches_played': 60,
                    'division': 3
                    }
                ]
            }
        ]
        """

        assert response.status_code == 200

        assert len(data['player_skills']) == 4
        assert data['user_id'] == 76561198024807207

        assert data['player_skills'][0]['playlist'] == 10
        assert data['player_skills'][0]['matches_played'] > 0

        assert data['player_skills'][1]['playlist'] == 11
        assert data['player_skills'][1]['matches_played'] > 0

        assert data['player_skills'][2]['playlist'] == 12
        assert data['player_skills'][2]['matches_played'] > 0

        assert data['player_skills'][3]['playlist'] == 13
        assert data['player_skills'][3]['matches_played'] > 0

    def test_authenticated_get_player_titles_no_titles(self):
        response = rl_auth.get_player_titles('steam', 76561198022035654)

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_authenticated_get_player_titles_has_titles(self):
        response = rl_auth.get_player_titles('steam', 76561198024807207)

        assert response.status_code == 200
        assert len(response.json()) > 0
        assert {'title': 'Season2GrandChampion'} in response.json()

    def test_authenticated_get_stats_value_for_user(self):
        response = rl_auth.get_stats_value_for_user('steam', 'assists', 76561198024807207)
        data = response.json()[0]

        """
        [
            {
                'stat_type': 'assists',
                'user_id': 76561198024807207,
                'user_name': '[SA] Snaski',
                'value': 5766
            }
        ]
        """

        assert response.status_code == 200
        assert data['stat_type'] == 'assists'
        assert data['user_id'] == 76561198024807207
        assert data['value'] > 0

    # The API is currently broken for this use-case. This test should highlight when it's fixed.
    def test_authenticated_get_stats_value_for_xbox_user_with_space(self):
        response = rl_auth.get_stats_value_for_user('xboxone', 'assists', 'Liquid Cight')
        assert response.status_code == 500
        assert response.text == '<h1>Server Error (500)</h1>'

    def test_authenticated_get_stats_values_for_steam_user(self):
        data = rl_auth.get_stats_values_for_user('steam', 76561198024807207)

        """
        {
            76561198024807207: {
                'saves': 14099,
                'wins': 7803,
                'mvps': 3757,
                'shots': 42193,
                'goals': 18017,
                'assists': 9284
            }
        }
        """

        assert 76561198024807207 in data

        assert 'saves' in data[76561198024807207]
        assert data[76561198024807207]['saves'] >= 0

        assert 'wins' in data[76561198024807207]
        assert data[76561198024807207]['wins'] >= 0

        assert 'mvps' in data[76561198024807207]
        assert data[76561198024807207]['mvps'] >= 0

        assert 'shots' in data[76561198024807207]
        assert data[76561198024807207]['shots'] >= 0

        assert 'goals' in data[76561198024807207]
        assert data[76561198024807207]['goals'] >= 0

        assert 'assists' in data[76561198024807207]
        assert data[76561198024807207]['assists'] >= 0

    def test_authenticated_get_stats_values_for_xbox_user(self):
        data = rl_auth.get_stats_values_for_user('xboxone', 'Intact')

        """
        {
            'Intact': {
                'wins': 2917,
                'shots': 17976,
                'goals': 9237,
                'saves': 5033,
                'assists': 2585,
                'mvps': 1688
            }
        }
        """

        assert 'Intact' in data

        assert 'saves' in data['Intact']
        assert data['Intact']['saves'] >= 0

        assert 'wins' in data['Intact']
        assert data['Intact']['wins'] >= 0

        assert 'mvps' in data['Intact']
        assert data['Intact']['mvps'] >= 0

        assert 'shots' in data['Intact']
        assert data['Intact']['shots'] >= 0

        assert 'goals' in data['Intact']
        assert data['Intact']['goals'] >= 0

        assert 'assists' in data['Intact']
        assert data['Intact']['assists'] >= 0

    # This will return no data as the sub-calls fail. This test will fail with the API bug is fixed.
    def test_authenticated_get_stats_values_for_xbox_user_with_space(self):
        data = rl_auth.get_stats_values_for_user('xboxone', 'Liquid Cight')
        assert data == {}
