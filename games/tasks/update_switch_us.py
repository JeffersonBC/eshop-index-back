from celery import shared_task

import requests
from requests.exceptions import Timeout, ConnectionError

import re

from classification.models.tag import TagGroup
from games.models import SwitchGameUS
from games.serializers import SwitchGameUSSerializer
from games.tasks.update_utils import treated_request, create_tag_if_not_exists


@shared_task()
def update_switch_us():
    print('Updating Switch US games...')

    url = 'http://www.nintendo.com/json/content/get/filter/game'
    params = {
        'system': 'switch',
        'sort': 'title',
        'direction': 'asc',
        'limit': 200,
        'offset': 0
    }

    tag_group_genre, tag_group_created = \
        TagGroup.objects.get_or_create(name='Genre')

    tag_group_characteristics, tag_group_created = \
        TagGroup.objects.get_or_create(name='Characteristics')

    for offset in range(0, 3000, 200):
        # Make the request, and skip current offset if there's any problem
        params['offset'] = offset
        req = treated_request(url, params, 'US Switch games')
        if req is None:
            print('Request for us games failed at offset {}, skipping.'
                  .format(offset))
            continue

        # If offset hasn't gone beyond the last game yet
        if 'game' in req.json()['games']:
            print('{} games found at offset {}'
                  .format(len(req.json()['games']['game']), offset))

            # Add every game to the database
            for game in req.json()['games']['game']:
                game_code = re.sub(r'[\-\. ]+', '', game['game_code'])

                # If unique code is empty (usually unreleased games), skip game
                if game_code[4:9] is '':
                    print('Empty unique code found for {}'
                          .format(game['title']))
                    continue

                # If game already in DB, skip it
                if SwitchGameUS.objects \
                        .filter(game_code_unique=game_code[4:9]) \
                        .exists():
                    # print('Game {} already in DB.'.format(game['title']))
                    continue

                # If game not yet in DB, save it
                else:
                    serializer = SwitchGameUSSerializer(data=game)
                    if serializer.is_valid():
                        # print('Added: {}'.format(game['title']))
                        switch_game_us = serializer.save()
                    else:
                        print('[ERROR] ({}): {}'.format(game['title'],
                              serializer.errors))
                        continue

                # For each tag, create if it doesn't exist yet and assign it to
                # the game
                if game['free_to_start'] == 'true':
                    create_tag_if_not_exists(
                        'Free to Play',
                        tag_group_characteristics,
                        switch_game_us.switchgame)

                if isinstance(game['categories']['category'], str):
                    # Checking if string is necessary for games with a single
                    # category (multiple categories come in an array)
                    create_tag_if_not_exists(
                        game['categories']['category'],
                        tag_group_genre,
                        switch_game_us.switchgame)

                else:
                    for tag_name in game['categories']['category']:
                        create_tag_if_not_exists(
                            tag_name,
                            tag_group_genre,
                            switch_game_us.switchgame)

        # If offset went beyond the last game, break the for loop
        else:
            break


@shared_task()
def update_switch_us_free_tag():
    print('Updating Switch US games "Free To Play" tag...')

    url = 'http://www.nintendo.com/json/content/get/filter/game'
    params = {
        'system': 'switch',
        'sort': 'title',
        'direction': 'asc',
        'limit': 200,
        'offset': 0
    }

    tag_group_characteristics, tag_group_created = \
        TagGroup.objects.get_or_create(name='Characteristics')

    for offset in range(0, 3000, 200):
        # Make the request, and skip current offset if there's any problem
        params['offset'] = offset
        req = treated_request(url, params, 'US Switch games')
        if req is None:
            print('Request for us games failed at offset {}, skipping.'
                  .format(offset))
            continue

        # If offset hasn't gone beyond the last game yet
        if 'game' in req.json()['games']:
            print('{} games found at offset {}'
                  .format(len(req.json()['games']['game']), offset))

            # Iterate over every game already in the database
            for game in req.json()['games']['game']:
                game_code = re.sub(r'[\-\. ]+', '', game['game_code'])

                # If unique code is empty (unreleased games), skip game
                if game_code[4:9] is '':
                    print('Empty unique code found for {}'
                          .format(game['title']))
                    continue

                # If game not yet in DB, skip it
                if not SwitchGameUS.objects \
                        .filter(game_code_unique=game_code[4:9]) \
                        .exists():
                    continue

                switch_game_us = SwitchGameUS.objects \
                    .get(game_code_unique=game_code[4:9])

                if game['free_to_start'] == 'true':
                    create_tag_if_not_exists(
                        'Free to Play',
                        tag_group_characteristics,
                        switch_game_us.switchgame)

        # If offset went beyond the last game, break the for loop
        else:
            break