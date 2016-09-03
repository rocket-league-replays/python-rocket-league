import os

import pytest
from rocket_league.client import RocketLeagueAPI

authenticated = pytest.mark.skipif(
    not os.getenv('ROCKETLEAGUE_API_KEY', None),
    reason="Environment variable 'ROCKETLEAGUE_API_KEY' not set or empty."
)

# Ensure we're hitting the correct endpoints and using the correct request method.
rl = RocketLeagueAPI('', debug=True)


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
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/1/'
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
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/1/'
        assert request_method == 'GET'
        assert data is None

    def test_verify_player_id_too_many_values(self):
        # Ensure only a single ID is allowed.
        with pytest.raises(ValueError):
            rl.get_player_titles('steam', [1, 2])

    # POST /api/v1/<platform>/playerskills/
    def test_verify_player_id_post(self):
        request_method, request_url, data = rl.get_player_skills('steam', [1, 2, 3])
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/'
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
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/population/'
        assert data is None

    def test_get_regions(self):
        request_method, request_url, data = rl.get_regions()
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/regions/'
        assert data is None

    def test_skill_leaderboard(self):
        request_method, request_url, data = rl.get_skill_leaderboard('steam', 10)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/skills/10/'
        assert data is None

    def test_stats_leaderboard(self):
        request_method, request_url, data = rl.get_stats_leaderboard('steam')
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/'
        assert data is None

    def test_stats_leaderboard_stat_type(self):
        request_method, request_url, data = rl.get_stats_leaderboard('steam', 'goals')
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/'
        assert data is None

    def test_stats_value_for_user(self):
        request_method, request_url, data = rl.get_stats_value_for_user('steam', 'goals', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/1/'
        assert data is None

    def test_player_skills(self):
        request_method, request_url, data = rl.get_player_skills('steam', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/1/'
        assert data is None

    def test_player_titles(self):
        request_method, request_url, data = rl.get_player_titles('steam', 1)
        assert request_method == 'GET'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playertitles/1/'
        assert data is None

    # Ensure we're hitting all of the correct endpoints.
    # POST /api/v1/<platform>/leaderboard/stats/<stat_type>/
    # POST /api/v1/<platform>/playerskills/
    def test_get_stats_value_for_user_post(self):
        request_method, request_url, data = rl.get_stats_value_for_user('steam', 'goals', [1, 2, 3])
        assert request_method == 'POST'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/'
        assert data == {'player_ids': [1, 2, 3]}

    def test_get_player_skills_post(self):
        request_method, request_url, data = rl.get_player_skills('steam', [1, 2, 3])
        assert request_method == 'POST'
        assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/'
        assert data == {'player_ids': [1, 2, 3]}


class TestUnauthenticatedCalls(object):

    def test_unauthenticated_call(self):
        rl = RocketLeagueAPI('', debug_request=True)
        response = rl.get_regions()

        assert response.status_code == 401
        assert response.text == '{"detail":"Invalid token header. No credentials provided."}'

    def test_unauthenticated_call_json(self):
        rl = RocketLeagueAPI('')
        response = rl.get_regions()

        assert response == {"detail": "Invalid token header. No credentials provided."}


# Test account: 76561198022035654
# Test real requests to the API.
@authenticated
class TestAuthenticatedCalls(object):

    def test_authenticated_get_regions(self):
        rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY', ''), debug_request=True)
        response = rl.get_regions()

        assert response.status_code == 200
        assert len(response.json()) > 0
