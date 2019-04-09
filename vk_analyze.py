import os
import requests
import datetime
from itertools import count
from services import storage_picle_io
from services import listmerge


def get_vk_post_ids(uid, token, picle_file_pathname, pages_limit):
    allpages = 1
    vk_post_ids_list = []
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
                    vk_post_ids_list.append(rezult)
                if page_numbers >= allpages:
                    break
            else:
                raise ValueError('response vk error!')
    vk_post_ids_list = storage_picle_io(in_data=vk_post_ids_list,
                                        picle_file_pathname=picle_file_pathname)
    return [x['id'] for x in vk_post_ids_list]


def get_vk_comments_raw_from_post_id(uid, token, vk_post_id, pages_limit):
    allpages = 100
    vk_comments_raw_list = []
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
                vk_comments_raw_list.append(rezult)
            if page_numbers >= allpages:
                break
        else:
            raise ValueError('response vk error!')
    return vk_comments_raw_list


def add_vk_comments_threads(vk_comments_raw_list):
    all_comments_list = []
    threads_list = listmerge([comment['thread']['items'] for comment in \
                         vk_comments_raw_list if comment['thread']['items']])
    comments_with_threads_list = vk_comments_raw_list + threads_list
    for comment in comments_with_threads_list:
        try:
            all_comments_list.append({comment['date']: comment['from_id']})
        except KeyError:
            pass
    return all_comments_list


def get_vk_comments(vk_post_ids_list, uid, token, picle_file_pathname, pages_limit):
    vk_comments = []
    if not os.path.exists(picle_file_pathname):
        for post_id in vk_post_ids_list:
            row_comments = get_vk_comments_raw_from_post_id(vk_post_id=post_id,
                                                   uid=uid, token=token,
                                                   pages_limit=pages_limit)
            comments_with_threads = add_vk_comments_threads(row_comments)
            vk_comments.append(comments_with_threads)
    vk_comments = storage_picle_io(in_data=vk_comments,
                                        picle_file_pathname=picle_file_pathname)
    return listmerge(vk_comments)


def get_vk_comment_author_id_last_weeks(comment_dict, weeks=2):
    qty_days = weeks*7
    now = datetime.datetime.now()
    past_time_point = now - datetime.timedelta(qty_days)
    if isinstance(comment_dict, dict):
        for comment_date, comment_author_id in comment_dict.items():
            if datetime.datetime.fromtimestamp(comment_date) >= past_time_point:
                return comment_author_id
