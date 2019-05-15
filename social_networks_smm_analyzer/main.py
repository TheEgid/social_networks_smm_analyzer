import os
import sys
import logging
import argparse
from instabot import Bot
from dotenv import load_dotenv
from collections import Counter
import pprint

from services import filter_last_months
#from services import test_switch
from services import test_switch_var
from ig_analyze import get_inst_posts
from ig_analyze import get_inst_comments
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from vk_analyze import get_vk_group_id
from vk_analyze import get_vk_posts
from vk_analyze import get_all_vk_likers
from vk_analyze import get_vk_last_weeks_commentators
from fb_analyze import get_all_fb_posts
from fb_analyze import get_all_fb_comments
from fb_analyze import get_fb_commentator_last_months
from fb_analyze import get_all_fb_reactions
from fb_analyze import get_compressed_reactions_dict
#from fb_analyze import collect_reactions


def analyze_instagram(target, login, password, months=3):
    bot = Bot()
    bot.login(username=login, password=password)
    inst_posts = get_inst_posts(target, bot)

    inst_comments = get_inst_comments(inst_posts, bot)

    top_commentators = get_inst_top_commentators(inst_comments, months)
    top_posts_commentators = get_inst_top_posts_commentators(inst_comments,
                                                             months)
    return top_commentators, top_posts_commentators


def analyze_vkontakte(target, vk_token, weeks=2, pages_limit=True):
    uid_target = get_vk_group_id(token=vk_token, group_name=target)
    vk_posts = get_vk_posts(token=vk_token, uid=uid_target, pages_limit=pages_limit)

    vk_last_weeks_commentators = set(get_vk_last_weeks_commentators(vk_posts,
        uid=uid_target, token=vk_token, pages_limit=pages_limit, weeks=weeks))

    vk_likers = set(get_all_vk_likers(vk_posts, uid=uid_target, token=vk_token,
                                  pages_limit=pages_limit))

    vk_core_audience = set.intersection(vk_last_weeks_commentators, vk_likers)
    return set(filter(None, vk_core_audience))


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

    fb_respondents = {_id: dict(Counter(_reactions)) for _id, _reactions in 
                      reactions_dict.items()}
    
    return set(last_months_commentators), fb_respondents


def get_args_parser():
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter_class)

    msg = 'Only these arguments are valid: instagram, vkontakte, facebook'
    parser.add_argument('command', type=str, help=msg)
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Test mode')
    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    login_inst = os.getenv("LOGIN_INST")
    password_inst = os.getenv("PASSWORD_INST")
    token_fb = os.getenv("TOKEN_FB")
    token_vk = os.getenv("TOKEN_VK")

    target_group_name_inst = os.getenv("TARGET_GROUP_NAME_INST")
    target_group_name_vk = os.getenv("TARGET_GROUP_NAME_VK")
    target_group_name_fb = os.getenv("TARGET_GROUP_ID_FB")

    parser = get_args_parser()
    args = parser.parse_args()

    if args.test:
        logging.info(' Test mode')
        test_switch_var.append(True)
        #test_switch(True)
    else:
        logging.info(' Normal mode')
        #test_switch(False)

    if args.command == 'instagram':
        comments_top, posts_top = analyze_instagram(target=target_group_name_inst,
                                                    login=login_inst,
                                                    password=password_inst)
        pprint.pprint({'Instagram Comments Top': comments_top,
                       'Instagram Posts Top': posts_top})

    elif args.command == 'vkontakte':
        vk_core_audience = analyze_vkontakte(target=target_group_name_vk,
                                             vk_token=token_vk, pages_limit=False)
        pprint.pprint({'Vkontakte Core Audience': vk_core_audience})

    elif args.command == 'facebook':
        audience, reactions = analyze_facebook(target=target_group_name_fb,
                                               fb_token=token_fb)
        pprint.pprint({'Facebook Core Audience': audience,
                       'Facebook Reactions': reactions})
    else:
        parser.print_help()
        parser.error('positional arguments error')


if __name__ == '__main__':
    main()
