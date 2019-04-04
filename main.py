import os
import sys
import pprint
from instabot import Bot
from dotenv import load_dotenv
import argparse
from services import print_results
from ig_analyze import analyze_instagram




if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.split(dir_path)[0])
    load_dotenv()
    LOGIN_INST = os.getenv("LOGIN_INST")
    PASSWORD_INST = os.getenv("PASSWORD_INST")
    target_instagram_username = r'cocacolarus'
    bot = Bot()
    bot.login(username=LOGIN_INST, password=PASSWORD_INST)
    inst_post_ids_file = 'all_inst_post_ids_list.pickle'
    inst_comments_file = 'all_inst_comments_list.pickle'

    comments_top, posts_top = analyze_instagram(target_instagram_username,
                                           bot,
                                           inst_post_ids_file,
                                           inst_comments_file)

    print_results('Comments Top', comments_top)
    print_results('Posts Top', posts_top)


