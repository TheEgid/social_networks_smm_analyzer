import os
import sys
import pprint
from instabot import Bot
from dotenv import load_dotenv
import argparse
import datetime
from services import print_results
from ig_analyze import get_inst_post_ids
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from ig_analyze import get_all_inst_comments

from vk_analyze import get_vk_post_ids
from vk_analyze import get_vk_comments
from vk_analyze import get_vk_comment_author_id_last_weeks


def analyze_instagram(target, login, password):
    bot = Bot()
    bot.login(username=login, password=password)
    inst_post_ids_file = 'all_inst_post_ids_list.pickle'
    inst_comments_file = 'all_inst_comments_list.pickle'
    post_ids_list = get_inst_post_ids(target, bot,
                                      inst_post_ids_file)
    inst_comments_list = get_all_inst_comments(post_ids_list, bot,
                                               inst_comments_file)
    top_commentators = get_inst_top_commentators(inst_comments_list, months=3)
    top_posts_commentators = get_inst_top_posts_commentators(inst_comments_list,
                                                                    months=3)
    return top_commentators, top_posts_commentators


def analyze_vkontakte(target, vk_token, pages_limit=True):
    vk_posts_file = 'all_vk_posts_file.pickle'
    vk_comments_file = 'all_vk_comments_list.pickle'
    vk_post_ids_list = (get_vk_post_ids(token=vk_token, uid=target,
                                picle_file_pathname=vk_posts_file,
                                pages_limit=False))

    all_vk_comments = get_vk_comments(vk_post_ids_list=vk_post_ids_list,
                                          uid=target, token=vk_token,
                                          picle_file_pathname=vk_comments_file,
                                          pages_limit=pages_limit)

    vk_commentators_last_weeks = [get_vk_comment_author_id_last_weeks(x, weeks=2)\
        for x in  all_vk_comments if get_vk_comment_author_id_last_weeks(x)]

    print(len(all_vk_comments))
    print(len(list(vk_commentators_last_weeks)))



if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    TOKEN_VK = os.getenv("TOKEN_VK")
    uid_vk_target = '-16297716'

    analyze_vkontakte(vk_token=TOKEN_VK, target=uid_vk_target, pages_limit=False)





#!!!!!!!!!!!!!!
# LOGIN_INST = os.getenv("LOGIN_INST")
# PASSWORD_INST = os.getenv("PASSWORD_INST")
# comments_top, posts_top = analyze_instagram(target=r'cocacolarus',
#                                             login=LOGIN_INST,
#                                             password=PASSWORD_INST)
# print_results('Comments Top', comments_top)
# print_results('Posts Top', posts_top)







