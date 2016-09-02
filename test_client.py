import os

import pytest
from client import RocketLeagueAPI

# Ensure we're hitting the correct endpoints and using the correct request method.
rl = RocketLeagueAPI('', debug=True)


def test_dir():
    assert dir(rl)[0].startswith('get_')
    assert dir(rl)[-1].startswith('get_')


def test_invalid_attribute():
    with pytest.raises(AttributeError):
        rl.test

    with pytest.raises(AttributeError):
        rl.test()


def test_invalid_get():
    with pytest.raises(AttributeError) as e:
        rl.get_foo

    assert "AttributeError: 'RocketLeagueAPI' object has no attribute 'get_foo'" in str(e)


def test_invalid_endpoint():
    with pytest.raises(AttributeError) as e:
        rl.regions

    assert "Did you mean 'get_regions'?" in str(e)


def test_missing_parameters():
    with pytest.raises(AssertionError):
        rl.get_player_skills()


def test_invalid_platform():
    with pytest.raises(AssertionError):
        rl.get_player_skills('foo', 1)


# GET /api/v1/<platform>/playerskills/<player_id>/
def test_request_proxy_valid():
    endpoint, request_method, args = rl.get_player_skills('steam', 1)
    assert endpoint['endpoint'] == 'playerskills'
    assert request_method == 'GET'
    assert args == ['steam', 1]


def test_request_proxy_empty_list():
    with pytest.raises(ValueError):
        rl.get_player_skills('steam', [])


def test_request_proxy_empty_string():
    with pytest.raises(ValueError):
        rl.get_player_skills('steam', '')


def test_request_proxy_single_value():
    # Ensure the single ID is transformed into its non-list representation.
    endpoint, request_method, args = rl.get_player_skills('steam', [1])
    assert endpoint['endpoint'] == 'playerskills'
    assert request_method == 'GET'
    assert args == ['steam', 1]


# POST /api/v1/<platform>/playerskills/
def test_request_proxy_post():
    endpoint, request_method, args = rl.get_player_skills('steam', [1, 2, 3])
    assert endpoint['endpoint'] == 'playerskills'
    assert request_method == 'POST'
    assert args == ['steam', [1, 2, 3]]


# Ensure we're hitting all of the correct endpoints.
# GET  /api/v1/population/
# GET  /api/v1/regions/
# GET  /api/v1/<platform>/leaderboard/skills/<playlist>/
# GET  /api/v1/<platform>/leaderboard/stats/
# GET  /api/v1/<platform>/leaderboard/stats/<stat_type>/
# GET  /api/v1/<platform>/leaderboard/stats/<stat_type>/<player_id>/
# GET  /api/v1/<platform>/playerskills/<player_id>/
# GET  /api/v1/<platform>/playertitles/<player_id>/
def test_request_get():
    request_method, request_url, data = rl.request(*rl.get_population())
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/population/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_regions())
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/regions/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_skill_leaderboard('steam', 10))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/skills/10/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_stats_leaderboard('steam'))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_stats_leaderboard('steam', 'goals'))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_stats_value_for_user('steam', 'goals', 1))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/1/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_player_skills('steam', 1))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/1/'
    assert data is None

    request_method, request_url, data = rl.request(*rl.get_player_titles('steam', 1))
    assert request_method == 'GET'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playertitles/1/'
    assert data is None


# Ensure we're hitting all of the correct endpoints.
# POST /api/v1/<platform>/leaderboard/stats/<stat_type>/
# POST /api/v1/<platform>/playerskills/
def test_request_post():
    request_method, request_url, data = rl.request(*rl.get_stats_leaderboard('steam', 'goals', [1, 2, 3]))
    assert request_method == 'POST'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/leaderboard/stats/goals/'
    assert data == {'player_ids': [1, 2, 3]}

    request_method, request_url, data = rl.request(*rl.get_player_skills('steam', [1, 2, 3]))
    assert request_method == 'POST'
    assert request_url == 'https://api.rocketleaguegame.com/api/v1/steam/playerskills/'
    assert data == {'player_ids': [1, 2, 3]}


def test_unauthenticated_call():
    rl = RocketLeagueAPI('', debug_request=True)
    response = rl.get_regions()

    assert response.status_code == 401
    assert response.text == '{"detail":"Invalid token header. No credentials provided."}'


def test_unauthenticated_call_json():
    rl = RocketLeagueAPI('')
    response = rl.get_regions()

    assert response == {"detail": "Invalid token header. No credentials provided."}


def test_authenticated_call():
    rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY', ''), debug_request=True)
    response = rl.get_regions()

    assert response.status_code == 200
    assert len(response.json()) > 0
