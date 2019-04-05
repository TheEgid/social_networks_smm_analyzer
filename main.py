import os
import sys
import pprint
from instabot import Bot
from dotenv import load_dotenv
import argparse
from services import print_results
from ig_analyze import get_inst_post_ids
from ig_analyze import get_inst_top_commentators
from ig_analyze import get_inst_top_posts_commentators
from ig_analyze import get_all_inst_comments


def analyze_instagram(target, login, password):
    bot = Bot()
    bot.login(username=login, password=password)
    inst_post_ids_file = 'all_inst_post_ids_list.pickle'
    inst_comments_file = 'all_inst_comments_list.pickle'
    post_ids_list = get_inst_post_ids(target, bot,
                                      inst_post_ids_file)
    inst_comments_list = get_all_inst_comments(post_ids_list, bot,
                                               inst_comments_file)
    top_commentators = get_inst_top_commentators(inst_comments_list)
    top_posts_commentators = get_inst_top_posts_commentators(inst_comments_list)
    return top_commentators, top_posts_commentators


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()

    LOGIN_INST = os.getenv("LOGIN_INST")
    PASSWORD_INST = os.getenv("PASSWORD_INST")
    comments_top, posts_top = analyze_instagram(target=r'cocacolarus',
                                                login=LOGIN_INST,
                                                password=PASSWORD_INST)
    print_results('Comments Top', comments_top)
    print_results('Posts Top', posts_top)







