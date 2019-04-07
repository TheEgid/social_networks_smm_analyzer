import os
import requests
import datetime
from itertools import count
from services import storage_picle_io
from services import listmerge


def get_all_vk_posts(uid, token, picle_file_pathname, pages_limit):
    allpages = 1
    vk_posts_list = []
    _url = "https://api.vk.com/method/wall.get?v=5.92"
    params = {'access_token': token, 'owner_id': uid, 'count': 100}
    if not os.path.exists(picle_file_pathname):
        for page_numbers in count(start=0, step=100):
            params.update({'offset': page_numbers})
            response = requests.get(_url, params=params)
            if response.ok:
                if pages_limit is False:
                    allpages = response.json()['response']['count']
                for rezult in response.json()['response']['items']:
                    vk_posts_list.append(rezult)
                if page_numbers >= allpages:
                    break
            else:
                raise ValueError('response vk error!')
    vk_comments_list = storage_picle_io(in_data=vk_posts_list,
                                        picle_file_pathname=picle_file_pathname)
    return vk_comments_list


def get_vk_comments_raw_from_post_id(uid, token, vk_post_id, pages_limit):
    allpages = 100
    vk_comments_raw = []
    _url = "https://api.vk.com/method/wall.getComments?v=5.92"
    params = {'access_token': token, 'owner_id': uid, 'count': 100,
              'post_id': vk_post_id, 'extended': 1, 'thread_items_count': 10}
    for page_numbers in count(start=0, step=100):
        params.update({'offset': page_numbers})
        response = requests.get(_url, params=params)
        if response.ok:
            if pages_limit is False:
                allpages = response.json()['response']['count']
            for rezult in response.json()['response']['items']:
                vk_comments_raw.append(rezult)
            if page_numbers >= allpages:
                break
        else:
            raise ValueError('response vk error!')
    return vk_comments_raw


def get_vk_comments_with_threads(vk_comments_raw):
    all_comments = []
    threads = listmerge([x['thread']['items'] for x in \
                         vk_comments_raw if x['thread']['items']])
    vk_comments_with_threads_raw = vk_comments_raw + threads
    for comment in vk_comments_with_threads_raw:
        try:
            all_comments.append({comment['date']: comment['from_id']})
        except KeyError:
            pass
    return all_comments


def get_all_vk_comments(vk_post_ids_list, uid, token, picle_file_pathname, pages_limit):
    all_vk_comments = []
    if not os.path.exists(picle_file_pathname):
        for post_id in vk_post_ids_list:
            raw = get_vk_comments_raw_from_post_id(vk_post_id=post_id,
                                                   uid=uid, token=token,
                                                   pages_limit=pages_limit)
            all_comments = get_vk_comments_with_threads(raw)
            all_vk_comments.append(all_comments)
    all_vk_comments = storage_picle_io(in_data=all_vk_comments,
                                        picle_file_pathname=picle_file_pathname)
    return listmerge(all_vk_comments)


def filter_vk_commentators_last_weeks(comment_dict, weeks=2):
    qty_days = weeks*7
    now = datetime.datetime.now()
    past_time_point = now - datetime.timedelta(qty_days)
    if isinstance(comment_dict, dict):
        for key, value in comment_dict.items():
            if datetime.datetime.fromtimestamp(key) >= past_time_point:
                return value