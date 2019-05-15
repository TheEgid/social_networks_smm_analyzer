import requests
import datetime
from itertools import count
from services import storage_json_io_decorator
from services import merge_list


def get_vk_group_id(token, group_name):
    params = { 'group_ids': group_name, 'access_token': token }
    response = requests.get('https://api.vk.com/method/groups.getById?v=5.95',
                            params=params)
    response.raise_for_status()
    vk_group_id = -1 * response.json()['response'][0]['id']  # with "-" (vk.com/dev/wall.post#owner_id)
    return vk_group_id


@storage_json_io_decorator('test_data', 'all_vk_posts.json')
def get_vk_posts(uid, token, pages_limit):
    allpages = 1
    vk_post_ids = []
    _url = "https://api.vk.com/method/wall.get?v=5.95"
    params = {'access_token': token, 'owner_id': uid, 'count': 100}
    for page_numbers in count(start=0, step=100):
        params['offset'] = page_numbers
        response = requests.get(_url, params=params)
        response.raise_for_status()
        if not pages_limit:
            allpages = response.json()['response']['count']
        for rezult in response.json()['response']['items']:
            vk_post_ids.append(rezult)
        if page_numbers >= allpages:
            break
    return [vk_post['id'] for vk_post in vk_post_ids]


def add_vk_comments_threads(vk_comments_list):
    all_comments_list = []
    threads_list = merge_list([comment['thread']['items'] for comment in
                               vk_comments_list if comment['thread']['items']])
    comments_with_threads_list = vk_comments_list + threads_list
    for comment in comments_with_threads_list:
        try:
            all_comments_list.append({comment['date']: comment['from_id']})
        except KeyError:
            pass
    return all_comments_list


def get_vk_comments_from_post_id(vk_post_id, uid, token, pages_limit):
    allpages = 100
    vk_comments = []
    _url = "https://api.vk.com/method/wall.getComments?v=5.95"
    params = {'access_token': token, 'owner_id': uid, 'count': 100,
               'post_id': vk_post_id, 'extended': 1, 'thread_items_count': 10}
    for page_numbers in count(start=0, step=100):
        params['offset'] = page_numbers
        response = requests.get(_url, params=params)
        response.raise_for_status()
        if not pages_limit:
            allpages = response.json()['response']['count']
        for rezult in response.json()['response']['items']:
            vk_comments.append(rezult)
        if page_numbers >= allpages:
            break
    return add_vk_comments_threads(vk_comments)


def get_vk_commentator_filtered_last_weeks(comment_dict, weeks):
    qty_days = weeks * 7
    now = datetime.datetime.now()
    past_time_point = now - datetime.timedelta(qty_days)
    if isinstance(comment_dict, dict):
        for comment_date, comment_author_id in comment_dict.items():
            if datetime.datetime.fromtimestamp(comment_date) >= past_time_point:
                return comment_author_id


def get_vk_likers_from_post_id(post_id, uid, token, pages_limit):
    allpages = 1000
    vk_likers = []
    _url = "https://api.vk.com/method/likes.getList?v=5.95"
    params = {'access_token': token, 'owner_id': uid, 'count': 1000,
               'item_id': post_id, 'type': 'post', 'skip_own': 1}
    for page_numbers in count(start=0, step=1000):
        params['offset'] = page_numbers
        response = requests.get(_url, params=params)
        response.raise_for_status()
        if not pages_limit:
            allpages = response.json()['response']['count']
        for rezult in response.json()['response']['items']:
            vk_likers.append(rezult)
        if page_numbers >= allpages:
            break
    return set(vk_likers)


@storage_json_io_decorator('test_data', 'all_vk_last_weeks_commentators.json')
def get_vk_last_weeks_commentators(vk_post_ids, uid, token, pages_limit, weeks):
    last_weeks_commentators = []
    for post_id in vk_post_ids:
        vk_comments = get_vk_comments_from_post_id(post_id, uid, token,
                                                   pages_limit)
        last_weeks_commentators.append([
            get_vk_commentator_filtered_last_weeks(comment, weeks) for
            comment in vk_comments])
    return list(set(merge_list(last_weeks_commentators)))


@storage_json_io_decorator('test_data', 'all_vk_likers.json')
def get_all_vk_likers(vk_post_ids, uid, token, pages_limit):
    all_likers = [get_vk_likers_from_post_id(post_id, uid, token, pages_limit)
                  for post_id in vk_post_ids]
    return list(set(merge_list(all_likers)))
