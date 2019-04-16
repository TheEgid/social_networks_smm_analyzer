import os
import sys
import logging
from instabot import Bot
from dotenv import load_dotenv
import argparse


from services import delete_pickle_files
from services import print_results
from ig_analyze import get_inst_post_ids
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from ig_analyze import get_all_inst_comments
from vk_analyze import get_vk_group_id
from vk_analyze import get_vk_post_ids
from vk_analyze import get_vk_last_weeks_commentators_and_likers_ids
from fb_analyze import get_fb_post_ids
from fb_analyze import get_all_fb_comments
from fb_analyze import get_fb_commentator_last_months


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str,
                        help='social networks - valid arguments only: \
                        instagram, vkontakte, facebook')
    parser.add_argument("test", nargs='?', type=str,
                        help="test mode: argument test")
    return parser


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

    vk_post_ids_list = get_vk_post_ids(token=vk_token, uid=uid_target,
                                        picle_file_pathname=vk_posts_file,
                                        pages_limit=pages_limit)

    vk_core_audience = get_vk_last_weeks_commentators_and_likers_ids(
        vk_post_ids_list, uid=uid_target, token=vk_token,
        picle_file_pathname=vk_commentators_file,
        pages_limit=pages_limit, weeks=2)
    return vk_core_audience


def analyze_facebook(target, fb_token):
    fb_posts_file = 'all_fb_posts_file.pickle'
    fb_comments_file = 'all_fb_comments_list.pickle'

    fb_post_ids = get_fb_post_ids(group_id=target,
                                       token=fb_token,
                                       picle_file_pathname=fb_posts_file)

    all_fb_comments = get_all_fb_comments(fb_post_ids, token=fb_token,
                                          picle_file_pathname=fb_comments_file)

    fb_commentators = [get_fb_commentator_last_months(comment, months=1) \
                       for comment in all_fb_comments]

    return set(list(filter(None, fb_commentators)))


def main():
    logging.basicConfig(level=logging.INFO)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    LOGIN_INST = os.getenv("LOGIN_INST")
    PASSWORD_INST = os.getenv("PASSWORD_INST")
    TOKEN_FB = os.getenv("TOKEN_FB")
    GROUP_ID_FB = os.getenv("GROUP_ID_FB")
    TOKEN_VK = os.getenv("TOKEN_VK")

    vk_target = 'cocacola'

    arg_parser = get_args_parser()
    args = arg_parser.parse_args()

    if args.command not in ['instagram', 'vkontakte', 'facebook']:
        exit(f' Error: Bad argument {args.command}')
    else:
        logging.info(f' Run {args.command} analyzer')

    if args.test not in ['test', None]:
        exit(f'Error: Bad argument {args.test}')

    if args.test == 'test':
        logging.info(' Test mode: data from .pickle files')
    else:
        logging.info(' Normal mode: delete old .pickle files')
        delete_pickle_files()

    if args.command == 'instagram':
        comments_top, posts_top = analyze_instagram(target=r'cocacolarus',
                                                login=LOGIN_INST,
                                                password=PASSWORD_INST)
        print_results('Instagram Comments Top', comments_top)
        print_results('Instagram Posts Top', posts_top)

    if args.command == 'vkontakte':
        vk_core_audience = analyze_vkontakte(vk_token=TOKEN_VK,
                                             target=vk_target,
                                             pages_limit=False)
        print({'Vkontakte Core Audience': vk_core_audience})

    if args.command == 'facebook':
        fb_core_audience = analyze_facebook(target=GROUP_ID_FB, fb_token=TOKEN_FB)
        print({'Facebook Core Audience': fb_core_audience})


if __name__ == '__main__':
    main()









