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

from vk_analyze import get_vk_group_id
from vk_analyze import get_vk_post_ids
from vk_analyze import get_vk_last_weeks_commentators_and_likers_ids


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
    uid_target = get_vk_group_id(vk_token=vk_token, group_name=target)

    vk_posts_file = 'all_vk_posts_file.pickle'
    vk_commentators_file = 'all_vk_ids_list.pickle'

    vk_post_ids_list = (get_vk_post_ids(token=vk_token, uid=uid_target,
                                        picle_file_pathname=vk_posts_file,
                                        pages_limit=pages_limit))

    #vk_post_ids_list = [1772281, 1773533]
    vk_core_audience = get_vk_last_weeks_commentators_and_likers_ids(
        vk_post_ids_list, uid=uid_target, token=vk_token,
        picle_file_pathname=vk_commentators_file,
        pages_limit=pages_limit, weeks=2)
    return vk_core_audience


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    ##FB





    # TOKEN_VK = os.getenv("TOKEN_VK")
    # vk_target = 'cocacola'
    #
    #
    # vk_core_audience = analyze_vkontakte(vk_token=TOKEN_VK,
    #                                      target=vk_target, pages_limit=False)
    # print({'Vkontakte Core Audience': vk_core_audience})
    # print(len(vk_core_audience))


    # LOGIN_INST = os.getenv("LOGIN_INST")
    # PASSWORD_INST = os.getenv("PASSWORD_INST")
    # comments_top, posts_top = analyze_instagram(target=r'cocacolarus',
    #                                         login=LOGIN_INST,
    #                                         password=PASSWORD_INST)
    # print_results('Instagram Comments Top', comments_top)
    # print_results('Instagram Posts Top', posts_top)









