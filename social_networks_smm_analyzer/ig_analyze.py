from collections import Counter
from collections import defaultdict
from services import filter_last_months
from services import storage_json_io_decorator


def get_inst_comments_from_post(post_id, bot):
    inst_comments = []
    for comment in bot.get_media_comments_all(post_id):
        comment['post_id'] = post_id
        inst_comments.append(comment)
    return inst_comments


@storage_json_io_decorator('test_data', 'all_inst_posts.json')
def get_inst_posts(username, bot):
    user_id = bot.get_user_id_from_username(username)
    return bot.get_total_user_medias(user_id)


@storage_json_io_decorator('test_data', 'all_inst_comments.json')
def get_inst_comments(post_ids, bot):
    inst_comments = [get_inst_comments_from_post(post_id, bot)
                     for post_id in post_ids]
    return list(filter(None, inst_comments))


def get_inst_commentator_last_months(comment_dict, months=3):
    commentator = filter_last_months(comment_dict, 'created_at_utc', months)
    if commentator is not None:
        return commentator['user_id']


def get_inst_top_commentators(posts_with_comments_list, months):
    commentators_list = [get_inst_commentator_last_months(comment, months) for
                         post_with_comments in posts_with_comments_list for
                         comment in post_with_comments]
    commentators_list = list(filter(None, commentators_list))
    return Counter(commentators_list).most_common()


def get_inst_top_posts_commentators(posts_with_comments_list, months):
    commentators_list = [list(set(
        [get_inst_commentator_last_months(comment, months) for comment in
         post_comments])) for post_comments in posts_with_comments_list]
    top_varied_posts_commentators = defaultdict(int)
    for post_comments in commentators_list:
        for author in post_comments:
            if author is not None:
                top_varied_posts_commentators[author] += 1
    return sorted(top_varied_posts_commentators.items(),
                  key=lambda kv: kv[1], reverse=True)
