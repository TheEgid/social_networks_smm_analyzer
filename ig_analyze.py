import os
import datetime
from collections import Counter
from collections import defaultdict
from services import storage_picle_io


def get_inst_comments_from_post_id(post_id, bot):
    inst_comments = []
    for comment in bot.get_media_comments_all(post_id):
        inst_comments.append(
            {'post_id': post_id,
             'created_time': comment['created_at_utc'],
             'author_user_id': comment['user_id'],
             'author_username': comment['user']['username'],
             'text': comment['text']})
    return inst_comments


def get_inst_post_ids(username, bot, picle_file_pathname):
    user_id = bot.get_user_id_from_username(username)
    post_ids_list = []
    if not os.path.exists(picle_file_pathname):
        post_ids_list = bot.get_total_user_medias(user_id)

    post_ids_list = storage_picle_io(in_data=post_ids_list,
                                     picle_file_pathname=picle_file_pathname)
    return post_ids_list


def get_all_inst_comments(post_id_list, bot, picle_file_pathname):
    inst_comments_list = []
    if not os.path.exists(picle_file_pathname):
        inst_comments_list = [get_inst_comments_from_post_id(x, bot) for x in
                              post_id_list]
        inst_comments_list = list(filter(None, inst_comments_list))

    inst_comments_list = storage_picle_io(in_data=inst_comments_list,
                                        picle_file_pathname=picle_file_pathname)
    return inst_comments_list


def get_inst_commentators_last_months(comment_dict, months):
    qty_days_in_year, qty_months_in_year = 365, 12
    now = datetime.datetime.now()
    past_time_point = now - datetime.timedelta(
        months * qty_days_in_year / qty_months_in_year)
    if isinstance(comment_dict, dict):
        if datetime.datetime.fromtimestamp(
                comment_dict['created_time']) >= past_time_point:
            return comment_dict['author_username']


def get_inst_top_commentators(posts_with_comments_list, months=3):
    commentators_list = [get_inst_commentators_last_months(comment, months) for
                         post_with_comments in posts_with_comments_list for
                         comment in post_with_comments]
    top_commentators = Counter(commentators_list).most_common()
    return [x for x in top_commentators if x[0] is not None]


def get_inst_top_varied_posts_commentators(posts_with_comments_list, months=3):
    commentators_list = [list(set(
        [get_inst_commentators_last_months(comment, months) for comment in
         post_comments])) for post_comments in posts_with_comments_list]
    top_varied_posts_commentators = defaultdict(int)
    for post_comments in commentators_list:
        for author in post_comments:
            if author is not None:
                top_varied_posts_commentators[author] += 1
    return sorted(top_varied_posts_commentators.items(), key=lambda kv: kv[1],
                  reverse=True)


def analyze_instagram(target_instagram_username, bot, inst_post_ids_file,
                      inst_comments_file):
    post_ids_list = get_inst_post_ids(target_instagram_username, bot,
                                      inst_post_ids_file)
    inst_comments_list = get_all_inst_comments(post_ids_list, bot,
                                               inst_comments_file)

    analysis1 = get_inst_top_commentators(inst_comments_list)
    analysis2 = get_inst_top_varied_posts_commentators(inst_comments_list)
    return analysis1, analysis2


def print_resunts(result):
    result1, result2 = result
    comments_dict = {}
    'Comments Top'
    'Posts Top'
    pass