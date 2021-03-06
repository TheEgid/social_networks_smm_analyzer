import requests
import datetime
from itertools import count, chain
from services import storage_json_io_decorator


class VKApiResponseError(Exception):
    """Declare special exception."""
    pass


def get_vk_group_id(token, group_name):
    params = {'group_ids': group_name, 'access_token': token, 'v': 5.95}
    response = requests.get('https://api.vk.com/method/groups.getById',
                            params=params).json()
    if response.get('error'):
        _msg = response['error']['error_msg']
        raise(VKApiResponseError(_msg))
    vk_group_id = -1 * response['response'][0]['id']  # with "-" (vk.com/dev/wall.post#owner_id)
    return vk_group_id


@storage_json_io_decorator('test_data', 'all_vk_posts.json')
def get_vk_posts(uid, token, pages_limit=10000):
    vk_posts = []
    vk_count = 100
    _url = "https://api.vk.com/method/wall.get"
    params = {'access_token': token, 'owner_id': uid, 'v': 5.95, 'count': vk_count}
    for page_number in count(start=0, step=vk_count):
        params['offset'] = page_number
        response = requests.get(_url, params=params).json()
        if response.get('error'):
            raise(VKApiResponseError(response['error']['error_msg']))
        for post in response['response']['items']:
            vk_posts.append([post['id'], post['comments']['count'],
                                post['likes']['count']])
        if page_number >= pages_limit or \
                page_number >= response['response']['count']:
            break
    return vk_posts


def add_vk_comments_threads(vk_comments_list):
    all_comments_list = []
    threads_list = [comment['thread']['items'] for comment in
                    vk_comments_list if comment['thread']['items']]
    threads_list = list(chain.from_iterable(threads_list))
    comments_with_threads_list = vk_comments_list + threads_list
    for comment in comments_with_threads_list:
        try:
            all_comments_list.extend([{comment['date']: comment['from_id']}])
        except KeyError:
            pass
    return all_comments_list


def get_vk_comments_from_post(vk_post, uid, token, pages_limit=1000):
    post_id, comments_count, likes_count = vk_post
    vk_comments = []
    _url = "https://api.vk.com/method/wall.getComments"
    params = {'access_token': token, 'owner_id': uid, 'count': 100, 'v': 5.95,
              'post_id': post_id, 'extended': 1, 'thread_items_count': 10}
    for page_number in count(start=0, step=pages_limit):
        params['offset'] = page_number
        response = requests.get(_url, params=params).json()
        if response.get('error'):
            raise(VKApiResponseError(response['error']['error_msg']))
        for result in response['response']['items']:
            vk_comments.append(result)
        if page_number >= pages_limit or page_number >= comments_count:
            break
    all_vk_comments_from_post = add_vk_comments_threads(vk_comments)
    return all_vk_comments_from_post


def get_vk_commentator_who_commited_last_weeks(comments_dict, weeks=2):
    qty_days = weeks * 7
    now = datetime.datetime.now()
    past_time_point = now - datetime.timedelta(qty_days)
    if isinstance(comments_dict, dict):
        for comment_date, comment_author_id in comments_dict.items():
            if datetime.datetime.fromtimestamp(comment_date) >= past_time_point:
                return comment_author_id


def get_vk_likers_from_post(vk_post, uid, token, pages_limit=1000):
    post_id, comments_count, likes_count = vk_post
    vk_likers = []
    _url = "https://api.vk.com/method/likes.getList"
    params = {'access_token': token, 'owner_id': uid, 'v': 5.95, 'count': 1000,
              'item_id': post_id, 'type': 'post', 'skip_own': 1}
    for page_number in count(start=0, step=pages_limit):
        params['offset'] = page_number
        response = requests.get(_url, params=params).json()
        if response.get('error'):
            raise(VKApiResponseError(response['error']['error_msg']))
        for result in response['response']['items']:
            vk_likers.append(result)
        if page_number >= pages_limit or page_number >= likes_count:
            break
    return set(vk_likers)


@storage_json_io_decorator('test_data', 'all_vk_last_weeks_commentators.json')
def get_vk_last_weeks_commentators(vk_posts, uid, token, weeks):
    last_weeks_commentators = []
    for post in vk_posts:
        vk_comments = get_vk_comments_from_post(post, uid, token)
        last_weeks_commentators.extend(
            [get_vk_commentator_who_commited_last_weeks(comments, weeks) for
             comments in vk_comments])
    return list(set(last_weeks_commentators))


@storage_json_io_decorator('test_data', 'all_vk_likers.json')
def get_all_vk_likers(vk_posts, uid, token):
    all_likers = [get_vk_likers_from_post(post, uid, token)
                  for post in vk_posts]
    return list(set(chain.from_iterable(all_likers)))
