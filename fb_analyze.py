import requests
import os
from dateutil import parser
from datetime import datetime
from datetime import timezone
from datetime import timedelta

from services import storage_picle_io
from services import listmerge


def get_fb_post_ids(group_id, token, picle_file_pathname):
    url = f'https://graph.facebook.com/{group_id}/feed'
    params = {'access_token': token, 'v': 3.2}
    fb_data_list = []
    if not os.path.exists(picle_file_pathname):
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        while True:
            paging = response.json()["paging"]['next']
            fb_data_list.append(response.json()['data'])
            response = requests.get(paging)
            response.raise_for_status()
            if not response.json()['data']:
                break
    fb_data_list = storage_picle_io(in_data=fb_data_list,
                                        picle_file_pathname=picle_file_pathname)
    return [post['id'] for post in listmerge(fb_data_list)]


def get_fb_comments_from_post_id(post_id, token):
    url = f'https://graph.facebook.com/{post_id}/comments'
    params = {'filter': 'stream', 'access_token': token, 'v': 3.2}
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response.json()['data']


def convert_datetime_from_string(_string):
  if isinstance(_string, str):
      _string = parser.parse(_string)
  return _string


def get_all_fb_comments(fb_post_ids_list, token,
                                  picle_file_pathname):
    fb_comments = []
    if not os.path.exists(picle_file_pathname):
        for post_id in fb_post_ids_list:
            comments = get_fb_comments_from_post_id(post_id, token)
            fb_comments.append(comments)

    fb_comments = storage_picle_io(in_data=fb_comments,
                                   picle_file_pathname=picle_file_pathname)

    return listmerge([comment for comment in fb_comments if comment])


def get_fb_commentator_last_months(comment_dict, months=1):
    qty_days_in_year, qty_months_in_year = 365, 12
    now = datetime.now(timezone.utc)
    past_time_point = now - timedelta(months * qty_days_in_year //
                                      qty_months_in_year)
    if isinstance(comment_dict, dict):
        created_time = convert_datetime_from_string(comment_dict['created_time'])
        if created_time >= past_time_point:
            return comment_dict['from']['id']


