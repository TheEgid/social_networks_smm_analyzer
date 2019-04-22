import os
from collections import Counter
from collections import defaultdict
from services import filter_last_months
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
    post_ids = []
    if not os.path.exists(picle_file_pathname):
        post_ids = bot.get_total_user_medias(user_id)

    post_ids = storage_picle_io(in_data=post_ids,
                                     picle_file_pathname=picle_file_pathname)
    return post_ids


def get_all_inst_comments(post_id_list, bot, picle_file_pathname):
    inst_comments = []
    if not os.path.exists(picle_file_pathname):
        inst_comments = [get_inst_comments_from_post_id(x, bot) for x in
                              post_id_list]
        inst_comments = [filter(None, inst_comments)]

    inst_comments = storage_picle_io(in_data=inst_comments,
                                        picle_file_pathname=picle_file_pathname)
    return inst_comments


def get_inst_commentator_last_months(comment_dict, months):
    commentator = filter_last_months(comment_dict, 'created_time', months=months)
    if commentator is not None:
        return commentator['author_user_id']


def get_inst_top_commentators(posts_with_comments_list, months=3):
    commentators_list = [get_inst_commentator_last_months(comment, months) for
                         post_with_comments in posts_with_comments_list for
                         comment in post_with_comments]
    top_commentators = Counter(commentators_list).most_common()
    return [x for x in top_commentators if x[0] is not None]


def get_inst_top_posts_commentators(posts_with_comments_list, months=3):
    commentators_list = [list(set(
        [get_inst_commentator_last_months(comment, months) for comment in
         post_comments])) for post_comments in posts_with_comments_list]
    top_varied_posts_commentators = defaultdict(int)
    for post_comments in commentators_list:
        for author in post_comments:
            if author is not None:
                top_varied_posts_commentators[author] += 1
    return sorted(top_varied_posts_commentators.items(), key=lambda kv: kv[1],
                  reverse=True)
