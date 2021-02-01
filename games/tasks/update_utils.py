import requests
from requests.exceptions import Timeout, ConnectionError

from classification.models.tag import Tag, ConfirmedTag


def treated_request(url, params, task_name):
    try:
        req = requests.get(url, params=params)
    except Timeout:
        print('Request for {} failed due to a time out, aborting.'
              .format(task_name))
        return None
    except ConnectionError:
        print('Request for {} failed due to a connection error, aborting.'
              .format(task_name))
        return None
    except:
        print('Request for {} failed due to an unknown error, aborting.'
              .format(task_name))
        return None

    return req


def create_tag_if_not_exists(tag_name, tag_group, game):
    tag, tag_created = Tag.objects.get_or_create(
        name=tag_name,
        tag_group=tag_group)

    if tag_created:
        print('Added tag: {}'.format(tag_name))

    ConfirmedTag.objects.get_or_create(
        tag=tag,
        game=game,
        confirmed_by=ConfirmedTag.NINTENDO)
