import requests
from collections import defaultdict
from itertools import chain
from services import storage_json_io_decorator
from services import filter_last_months


@storage_json_io_decorator('test_data', 'all_fb_posts.json')
def get_all_fb_posts(group_id, token):
    url = f'https://graph.facebook.com/{group_id}/feed'
    params = {'access_token': token, 'v': 3.2}
    fb_data_list = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        paging = response.json()["paging"]['next']
        fb_data_list.extend(response.json()['data'])
        response = requests.get(url=paging, params=params)
        response.raise_for_status()
        if not response.json()['data']:
            break
    return [{'id': post['id'], 'updated_time': post['updated_time']} for post
            in fb_data_list]


def get_fb_comments_from_post(post, token):
    post_id = post['id']
    url = f'https://graph.facebook.com/{post_id}/comments'
    params = {'filter': 'stream', 'access_token': token, 'v': 3.2}
    fb_comments = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        fb_comments.extend(response.json()['data'])
        if response.json()['data']:
            paging = response.json()['paging']['cursors']['after']
            params['after'] = paging
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            fb_comments.extend(response.json()['data'])
        else:
            break
    return fb_comments


@storage_json_io_decorator('test_data', 'all_fb_comments.json')
def get_all_fb_comments(fb_posts, token):
    fb_comments = [get_fb_comments_from_post(post, token) for post in fb_posts]
    return chain.from_iterable([comment for comment in fb_comments if comment])


def get_fb_commentator_last_months(comment_dict, months):
    comment_dict = filter_last_months(comment_dict, 'created_time', months)
    try:
        return comment_dict['from']['id']
    except (KeyError, TypeError):
        pass


def get_fb_reactions_from_post_id(post, token):
    post_id = post['id']
    url = f'https://graph.facebook.com/{post_id}/reactions'
    params = {'filter': 'stream', 'access_token': token, 'v': 3.2}
    fb_reactions = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        fb_reactions.extend(response.json()['data'])
        if response.json()['data']:
            paging = response.json()['paging']['cursors']['after']
            params['after'] = paging
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            fb_reactions.extend(response.json()['data'])
        else:
            break
    for reaction in fb_reactions:
        reaction['post_time'] = post['updated_time']
    return fb_reactions


def get_compressed_reactions_dict(reactions):
    reactions_dict = defaultdict(list)
    for reaction in reactions:
        reactions_dict[reaction['id']].append(reaction['type'])
    return dict(reactions_dict)


@storage_json_io_decorator('test_data', 'all_fb_reactions.json')
def get_all_fb_reactions(fb_posts, token):
    fb_reactions = []
    for post in fb_posts:
        reactions = get_fb_reactions_from_post_id(post, token)
        fb_reactions.extend(reactions)
    return fb_reactions
