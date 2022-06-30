import praw
import pandas as pd
import sys
import configparser
import pathlib

parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
parser.read(f"{script_path}/configuration.conf")

CLIENT_ID = parser.get("reddit_config", "client_id")
SECRET = parser.get("reddit_config", "secret")

output_name = sys.argv[1]
file_name = output_name + ".csv"

POST_FIELDS = ('id', 'title', 'score', 'num_comments', 'author', 
               'created_utc', 'url', 'upvote_ratio', 'over_18',  
               'spoiler', 'stickied')


def api_connect():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=SECRET,
        user_agent="my user agent"
    )
    return reddit

def subreddit_posts(instance):
    subreddit = instance.subreddit("dataengineering")
    #subreddit = instance.subreddit("aws")
    posts = subreddit.top(time_filter = "day")
    return posts

def extract_data(posts):
    list_of_items = []
    for submission in posts:
        to_dict = vars(submission)
        sub_dict = {fields : to_dict[fields] for fields in POST_FIELDS}
        list_of_items.append(sub_dict)
    
    return list_of_items

def write_csv(data):
    df = pd.DataFrame(data)
    df.to_csv(f"/tmp/{file_name}", index=False)

def main():
    reddit_api = api_connect()
    posts = subreddit_posts(reddit_api)
    reddit_data = extract_data(posts)
    write_csv(reddit_data)


if __name__ == "__main__":
    main()