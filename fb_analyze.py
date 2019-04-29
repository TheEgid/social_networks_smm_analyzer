import requests
from collections import defaultdict
from services import storage_json_io_decorator
from services import merge_list
from services import filter_last_months


@storage_json_io_decorator('all_fb_posts.json')
def get_all_fb_posts(group_id, token):
    url = f'https://graph.facebook.com/{group_id}/feed'
    params = {'access_token': token, 'v': 3.2}
    fb_data_list = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        paging = response.json()["paging"]['next']
        fb_data_list.append(response.json()['data'])
        response = requests.get(url=paging, params=params)
        response.raise_for_status()
        if not response.json()['data']:
            break
    return [{'id': post['id'], 'updated_time': post['updated_time']} for post \
            in merge_list(fb_data_list)]


def get_fb_comments_from_post(post, token):
    post_id = post['id']
    url = f'https://graph.facebook.com/{post_id}/comments'
    params = {'filter': 'stream', 'access_token': token, 'v': 3.2}
    fb_comments = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        fb_comments.append(response.json()['data'])
        if response.json()['data']:
            paging = response.json()['paging']['cursors']['after']
            params['after'] = paging
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            fb_comments.append(response.json()['data'])
        else:
            break
    return merge_list(fb_comments)


@storage_json_io_decorator('all_fb_comments.json')
def get_all_fb_comments(fb_posts, token):
    fb_comments = [get_fb_comments_from_post(post, token) for post in fb_posts]
    return merge_list([comment for comment in fb_comments if comment])


def get_fb_commentator_last_months(comment_dict, months):
    comment_dict = filter_last_months(comment_dict, 'created_time', months)
    try:
        return comment_dict['from']['id']
    except (ValueError, KeyError):
        pass


def get_fb_reactions_from_post_id(post, token):
    post_id = post['id']
    url = f'https://graph.facebook.com/{post_id}/reactions'
    params = {'filter': 'stream', 'access_token': token, 'v': 3.2}
    fb_reactions = []
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    while True:
        fb_reactions.append(response.json()['data'])
        if response.json()['data']:
            paging = response.json()['paging']['cursors']['after']
            params['after'] = paging
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            fb_reactions.append(response.json()['data'])
        else:
            break
    reactions = merge_list(fb_reactions)
    for reaction in reactions:
        reaction['post_time'] = post['updated_time']
    return reactions


@storage_json_io_decorator('all_fb_reactions.json')
def get_all_fb_reactions(fb_posts, token):
    fb_reactions = []
    for post in fb_posts:
        reactions = get_fb_reactions_from_post_id(post, token)
        fb_reactions.append(reactions)
    return merge_list(fb_reactions)


def get_compressed_reactions_dict(reactions):
    reactions = [{reaction.pop('id'): reaction.pop('type')} for
                             reaction in reactions]
    reactions_dict = defaultdict(list)
    for reaction in reactions:
        for _id, _type in reaction.items():
            reactions_dict[_id].append(_type)
    return dict(reactions_dict)


def collect_reactions(reactions):
    react_types = {"LIKE": 0, "LOVE": 0, "WOW": 0, "HAHA": 0, "SAD": 0,
                   "ANGRY": 0}
    for react_type, _ in react_types.items():
        for reaction in reactions:
            if reaction == react_type:
                react_types[react_type] = react_types.get(react_type) + 1
    return react_types
