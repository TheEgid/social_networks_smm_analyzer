import requests
import os
from collections import defaultdict

from services import storage_picle_io
from services import merge_list
from services import filter_last_months


def get_fb_posts(group_id, token, picle_file_pathname):
    url = f'https://graph.facebook.com/{group_id}/feed'
    params = {'access_token': token, 'v': 3.2}
    fb_data_list = []
    if not os.path.exists(picle_file_pathname):
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        while True:
            paging = response.json()["paging"]['next']
            fb_data_list.append(response.json()['data'])
            response = requests.get(url=paging, params=params)
            response.raise_for_status()
            if not response.json()['data']:
                break
    fb_data_list = storage_picle_io(in_data=fb_data_list,
                                        picle_file_pathname=picle_file_pathname)
    return [{'id': post['id'], 'updated_time': post['updated_time']}
            for post in merge_list(fb_data_list)]


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


def get_fb_commentator_last_months(reaction_dict, months=1):
    respondent = filter_last_months(reaction_dict, 'created_time', months=months)
    if respondent is not None:
        return respondent['id']


def get_all_fb_comments(fb_posts, token,
                                  picle_file_pathname):
    fb_comments = []
    if not os.path.exists(picle_file_pathname):
        for post in fb_posts:
            comments = get_fb_comments_from_post(post, token)
            fb_comments.append(comments)

    fb_comments = storage_picle_io(in_data=fb_comments,
                                   picle_file_pathname=picle_file_pathname)

    return merge_list([comment for comment in fb_comments if comment])


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


def collect_reactions(reactions):
    types_reactions = {"LIKE": 0, "LOVE": 0, "WOW": 0, "HAHA": 0, "SAD": 0,
                       "ANGRY": 0}
    for type, _ in types_reactions.items():
        for reaction in reactions:
            if reaction == type:
                types_reactions[type] = types_reactions.get(type) + 1
    return types_reactions


def get_compressed_reactions_dict(reactions):
    reactions = [{reaction.pop('id'): reaction.pop('type')} for
                             reaction in reactions]
    reactions_dict = defaultdict(list)
    for reaction in reactions:
        for id, type in reaction.items():
            reactions_dict[id].append(type)
    return dict(reactions_dict)


def get_fb_get_reaction_last_months(reaction_dict, months=1):
    respondent = filter_last_months(reaction_dict, 'post_time', months=months)
    if respondent is not None:
        return reaction_dict


def get_all_fb_reactions(fb_posts, token, picle_file_pathname):
    fb_reactions = []
    if not os.path.exists(picle_file_pathname):
        for post in fb_posts:
            reactions = get_fb_reactions_from_post_id(post, token)
            fb_reactions.append(reactions)
    fb_reactions = merge_list(fb_reactions)
    fb_reactions = storage_picle_io(in_data=fb_reactions,
                                   picle_file_pathname=picle_file_pathname)
    last_months_reactions = [get_fb_get_reaction_last_months(reaction) for
                             reaction in fb_reactions if
                             get_fb_get_reaction_last_months(reaction)]
    last_months_reactions = get_compressed_reactions_dict(last_months_reactions)
    return {_id: collect_reactions(_reactions) for _id, _reactions
            in last_months_reactions.items()}
