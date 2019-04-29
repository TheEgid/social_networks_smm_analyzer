import os
import sys
import logging
import argparse
from instabot import Bot
from dotenv import load_dotenv
import pprint

from services import filter_last_months
from ig_analyze import get_inst_post_ids
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from ig_analyze import get_all_inst_comments

from vk_analyze import get_vk_group_id
from vk_analyze import get_vk_post_ids
from vk_analyze import get_vk_last_weeks_commentators_and_likers_ids

from fb_analyze import get_all_fb_posts
from fb_analyze import get_all_fb_comments
from fb_analyze import get_fb_commentator_last_months
from fb_analyze import get_all_fb_reactions
from fb_analyze import get_compressed_reactions_dict
from fb_analyze import collect_reactions


def analyze_instagram(target, login, password, months=3):
    bot = Bot()
    bot.login(username=login, password=password)
    inst_post_ids_file = 'all_inst_post_ids_list.pickle'
    inst_comments_file = 'all_inst_comments_list.pickle'
    inst_posts = get_inst_post_ids(target, bot,
                                      inst_post_ids_file)
    inst_comments = get_all_inst_comments(inst_posts, bot,
                                               inst_comments_file)
    top_commentators = get_inst_top_commentators(inst_comments, months)
    top_posts_commentators = get_inst_top_posts_commentators(inst_comments,
                                                             months)
    return top_commentators, top_posts_commentators


def analyze_vkontakte(target, vk_token, weeks=2, pages_limit=True):
    uid_target = get_vk_group_id(vk_token=vk_token, group_name=target)

    vk_posts_file = 'all_vk_posts_list.pickle'
    vk_commentators_file = 'all_vk_ids_list.pickle'

    vk_posts = get_vk_post_ids(token=vk_token, uid=uid_target,
                                       picle_file_pathname=vk_posts_file,
                                       pages_limit=pages_limit)

    vk_core_audience = get_vk_last_weeks_commentators_and_likers_ids(
        vk_posts, uid=uid_target, token=vk_token,
        picle_file_pathname=vk_commentators_file,
        pages_limit=pages_limit, weeks=weeks)
    return set(vk_core_audience)


def analyze_facebook(target, fb_token, months=1):
    fb_posts = get_all_fb_posts(group_id=target, token=fb_token)

    all_fb_comments = get_all_fb_comments(fb_posts, token=fb_token)
    last_months_commentators = [get_fb_commentator_last_months(comment, months)
                       for comment in all_fb_comments]
    last_months_commentators = list(filter(None, last_months_commentators))

    all_fb_reactions = get_all_fb_reactions(fb_posts, token=fb_token)
    last_months_reactions = [filter_last_months(reaction, 'post_time', months)
                             for reaction in all_fb_reactions]
    last_months_reactions = list(filter(None, last_months_reactions))

    reactions_dict = get_compressed_reactions_dict(last_months_reactions)

    fb_respondents = {_id: collect_reactions(_reactions) for _id, _reactions in
                      reactions_dict.items()}
    return set(last_months_commentators), fb_respondents


def get_args_parser():
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter_class)
    parser.add_argument('command', type=str,
                        help='Social networks - valid arguments only: instagram, vkontakte, facebook')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Test mode')
    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    LOGIN_INST = os.getenv("LOGIN_INST")
    PASSWORD_INST = os.getenv("PASSWORD_INST")
    TOKEN_FB = os.getenv("TOKEN_FB")
    TOKEN_VK = os.getenv("TOKEN_VK")

    TARGET_GROUP_NAME_INST = os.getenv("TARGET_GROUP_NAME_INST")
    TARGET_GROUP_NAME_VK = os.getenv("TARGET_GROUP_NAME_VK")
    TARGET_GROUP_ID_FB = os.getenv("TARGET_GROUP_ID_FB")

    args = get_args_parser().parse_args()
    if args.test:
        logging.info(' Test mode: temp data from json file')
    else:
        logging.info(' Normal mode: delete temp files')
        #delete_pickle_files()


    # if args.command == 'instagram':
    #     comments_top, posts_top = analyze_instagram(target=TARGET_GROUP_NAME_INST,
    #                                                 login=LOGIN_INST,
    #                                                 password=PASSWORD_INST)
    #     print({'Instagram Comments Top': comments_top})
    #     print({'Instagram Posts Top': posts_top})
    #
    # if args.command == 'vkontakte':
    #     vk_core_audience = analyze_vkontakte(target=TARGET_GROUP_NAME_VK,
    #                                          vk_token=TOKEN_VK, pages_limit=False)
    #     print({'Vkontakte Core Audience': vk_core_audience})

    if args.command == 'facebook':
        audience, reactions = analyze_facebook(target=TARGET_GROUP_ID_FB,
                                               fb_token=TOKEN_FB)
        pprint.pprint({'Facebook Core Audience': audience,
                      'Facebook Reactions': reactions})


if __name__ == '__main__':
    main()





