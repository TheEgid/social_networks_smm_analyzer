import os
import sys
import logging
import argparse
from instabot import Bot
from dotenv import load_dotenv

from services import delete_pickle_files
from ig_analyze import get_inst_post_ids
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from ig_analyze import get_all_inst_comments
from vk_analyze import get_vk_group_id
from vk_analyze import get_vk_post_ids
from vk_analyze import get_vk_last_weeks_commentators_and_likers_ids
from fb_analyze import get_fb_posts
from fb_analyze import get_all_fb_comments
from fb_analyze import get_fb_commentator_last_months
from fb_analyze import get_all_fb_reactions


def analyze_instagram(target, login, password, months=3):
    bot = Bot()
    bot.login(username=login, password=password)
    inst_post_ids_file = 'all_inst_post_ids_list.pickle'
    inst_comments_file = 'all_inst_comments_list.pickle'
    inst_posts = get_inst_post_ids(target, bot,
                                      inst_post_ids_file)
    inst_comments_list = get_all_inst_comments(inst_posts, bot,
                                               inst_comments_file)
    top_commentators = get_inst_top_commentators(inst_comments_list, months)
    top_posts_commentators = get_inst_top_posts_commentators(inst_comments_list,
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
    return list(vk_core_audience)


def analyze_facebook(target, fb_token, months=1):
    fb_posts_file = 'all_fb_posts_list.pickle'
    fb_comments_file = 'all_fb_comments_list.pickle'
    fb_reactions_file = 'all_fb_reactions_list.pickle'

    fb_posts = get_fb_posts(group_id=target,
                                  token=fb_token,
                                  picle_file_pathname=fb_posts_file)

    all_fb_comments = get_all_fb_comments(fb_posts, token=fb_token,
                                          picle_file_pathname=fb_comments_file)

    fb_commentators = [get_fb_commentator_last_months(comment, months=months)
                       for comment in all_fb_comments if
                       get_fb_commentator_last_months(comment, months=months)]

    fb_respondents = get_all_fb_reactions(fb_posts, token=fb_token,
                                          picle_file_pathname=fb_reactions_file)

    return fb_commentators, fb_respondents


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('instruction',
                        type=str, help= 'social networks - valid arguments only: instagram, vkontakte, facebook')
    parser.add_argument("test", nargs='?',
                        type=str, help="test mode: argument test")
    return parser


def analyze_args_and_get_instruction(args):
    if args.instruction not in ['instagram', 'vkontakte', 'facebook']:
        exit(f' Error: Bad argument {args.instruction}')
    else:
        logging.info(f' Run {args.instruction} analyzer')
    if args.test not in ['test', None]:
        exit(f'Error: Bad argument {args.test}')
    if args.test in ['test']:
        logging.info(' Test mode: data from .pickle files')
    else:
        logging.info(' Normal mode: delete old .pickle files')
        delete_pickle_files()
    return args.instruction


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

    arg_parser = get_args_parser()
    instruction = analyze_args_and_get_instruction(arg_parser.parse_args())

    if instruction == 'instagram':
        comments_top, posts_top = analyze_instagram(target=TARGET_GROUP_NAME_INST,
                                                    login=LOGIN_INST,
                                                    password=PASSWORD_INST)

        print({'Instagram Comments Top': comments_top})
        print({'Instagram Posts Top': posts_top})

    if instruction == 'vkontakte':
        vk_core_audience = analyze_vkontakte(target=TARGET_GROUP_NAME_VK,
                                             vk_token=TOKEN_VK, pages_limit=False)
        print({'Vkontakte Core Audience': vk_core_audience})

    if instruction == 'facebook':
        fb_core_audience, fb_reactions = analyze_facebook(target=TARGET_GROUP_ID_FB,
                                                          fb_token=TOKEN_FB)

        print({'Facebook Core Audience': fb_core_audience})
        print({'Facebook Reactions': fb_reactions})


if __name__ == '__main__':
    main()





