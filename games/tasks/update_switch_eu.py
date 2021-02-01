from celery import shared_task

from requests.exceptions import Timeout, ConnectionError
import requests

from classification.models.tag import TagGroup
from games.models import SwitchGameEU
from games.serializers import SwitchGameEUSerializer
from games.tasks.update_utils import treated_request, create_tag_if_not_exists


@shared_task()
def update_switch_eu():
    print('Updating Switch EU games...')

    url = 'http://search.nintendo-europe.com/en/select'
    params = {
        'fq': 'type:GAME AND system_type:nintendoswitch* AND product_code_txt:*',
        'q': '*',
        'rows': 9999,
        'sort': 'sorting_title asc',
        'start': 0,
        'wt': 'json',
    }

    # Make the request, and stop the task if there's any problem
    req = treated_request(url, params, 'EU Switch games')
    if req is None:
        return

    tag_group_publisher, tag_group_pub_created = \
        TagGroup.objects.get_or_create(name='Publisher')

    tag_group_developer, tag_group_dev_created = \
        TagGroup.objects.get_or_create(name='Developer')

    tag_group_age, tag_group_age_created = \
        TagGroup.objects.get_or_create(name='Age Rating')

    tag_group_characteristics, tag_group_created = \
        TagGroup.objects.get_or_create(name='Characteristics')

    # Add every game to the database
    print('{} games found'.format(len(req.json()['response']['docs'])))

    for game in req.json()['response']['docs']:
        if SwitchGameEU.objects.filter(
                game_code_unique=game['product_code_txt'][0].strip()[4:9]).exists():
            continue

        serializer = SwitchGameEUSerializer(data=game)

        if serializer.is_valid():
            # print('Added: {}'.format(game['title']))
            switch_game_eu = serializer.save()

            # If game has a publisher defined, add it as a tag
            if 'developer' in game:
                create_tag_if_not_exists(
                    game['developer'],
                    tag_group_developer,
                    switch_game_eu.switchgame)

            # If game has a publisher defined, add it as a tag
            if 'publisher' in game:
                create_tag_if_not_exists(
                    game['publisher'],
                    tag_group_publisher,
                    switch_game_eu.switchgame)

            # If game has an age rating defined, add it as a tag
            if 'age_rating_sorting_i' in game and game['age_rating_sorting_i'] != 0:
                create_tag_if_not_exists(
                    'PEGI ' + str(game['age_rating_sorting_i']),
                    tag_group_age,
                    switch_game_eu.switchgame)

            # If game has physical version set to true
            if 'physical_version_b' in game and game['physical_version_b'] == True:
                create_tag_if_not_exists(
                    'Physical Release',
                    tag_group_characteristics,
                    switch_game_eu.switchgame)
        else:
            print('[ERROR] ({}): {}'.format(game['title'], serializer.errors))


# One off task made to update the production database
@shared_task()
def update_switch_eu_age_tag():
    print('Updating Switch EU games age rating...')

    url = 'http://search.nintendo-europe.com/en/select'
    params = {
        'fq': 'type:GAME AND system_type:nintendoswitch* AND product_code_txt:*',
        'q': '*',
        'rows': 9999,
        'sort': 'sorting_title asc',
        'start': 0,
        'wt': 'json',
    }

    # Make the request, and stop the task if there's any problem
    req = treated_request(url, params, 'EU Switch games')
    if req is None:
        return

    # Create/ Get the 'Age Rating' Tag Group
    tag_group_age, tag_group_created = \
        TagGroup.objects.get_or_create(name='Age Rating')

    # Adds age rating tags for every game already on the database
    print('{} games found'.format(len(req.json()['response']['docs'])))

    for game in req.json()['response']['docs']:
        if not SwitchGameEU.objects.filter(
                game_code_unique=game['product_code_txt'][0].strip()[4:9]).exists():
            continue

        serializer = SwitchGameEUSerializer(data=game)

        if serializer.is_valid():
            switch_game_eu = SwitchGameEU.objects.get(
                game_code_unique=game['product_code_txt'][0].strip()[4:9])

            # If game has an age rating defined, add it as a tag
            if 'age_rating_sorting_i' in game and game['age_rating_sorting_i'] != 0:
                create_tag_if_not_exists(
                    'PEGI ' + str(game['age_rating_sorting_i']),
                    tag_group_age,
                    switch_game_eu.switchgame)


# One off task made to update the production database
@shared_task()
def update_switch_eu_physical_tag():
    print('Updating Switch EU games physical release tag...')

    url = 'http://search.nintendo-europe.com/en/select'
    params = {
        'fq': 'type:GAME AND system_type:nintendoswitch* AND product_code_txt:*',
        'q': '*',
        'rows': 9999,
        'sort': 'sorting_title asc',
        'start': 0,
        'wt': 'json',
    }

    # Make the request, and stop the task if there's any problem
    req = treated_request(url, params, 'EU Switch games')
    if req is None:
        return

    # Create/ Get the 'Characteristics' Tag Group
    tag_group_characteristics, tag_group_created = \
        TagGroup.objects.get_or_create(name='Characteristics')

    # Adds physical release tags for every game already on the database
    print('{} games found'.format(len(req.json()['response']['docs'])))

    for game in req.json()['response']['docs']:
        if not SwitchGameEU.objects.filter(
                game_code_unique=game['product_code_txt'][0].strip()[4:9]).exists():
            continue

        serializer = SwitchGameEUSerializer(data=game)

        if serializer.is_valid():
            switch_game_eu = SwitchGameEU.objects.get(
                game_code_unique=game['product_code_txt'][0].strip()[4:9])

            # If game has physical version set to true
            if 'physical_version_b' in game and game['physical_version_b'] == True:
                create_tag_if_not_exists(
                    'Physical Release',
                    tag_group_characteristics,
                    switch_game_eu.switchgame)
