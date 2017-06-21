#!/usr/bin/env python3
from facepy import GraphAPI
import time
import pymongo
import requests

connection = pymongo.MongoClient("ds111262.mlab.com", 11262)
db = connection["adminsitedb"]
db.authenticate("admin", "admin")
post_collection = db['posts']
user_collection = db['users']
banned_collection = db['the_condemned']

group_id = "1576746889024748"
app_id = "777625919075124"
app_secret = "b9e7ab1c9eabeac21596486e39956faf"
special_token = "EAACEdEose0cBANWZAVUi5u48QZA29GatILHpcZBLC3ccbmUscpuUCe2JoZC7dFWZCMyEzLYGb03lBMm7SDkYsgEpWrrzBKHYWZB1GHlq92AiAZB8r2JzOwf6ABFi9nQ4ZC6hnoCVU3eGmapYUZCzHK5Ita5sZCN86qVuHxjrSff82IJivdAoo3MZCxaYzCl7KiVEZBYZD"

access_token = app_id + "|" + app_secret
graph = GraphAPI(access_token)

f = open("/home/manh/Desktop/time.txt", "r")
last_time = f.readline().strip("\n")
f.close()


def get_comments(_id, list_of_comments):
    comments = graph.get(
        _id + "/comments?limit=50&time_format=U&fields=created_time,message,id,from&&since=" + last_time, page=True,
        retry=3, limit=1000)
    for cmt in comments:
        comment_content = cmt['data']
        for each_comment in comment_content:
            each_comment["parent_id"] = _id.split("_")[1]
        list_of_comments += comment_content
        for content in comment_content:
            comments2 = graph.get(
                content[
                    'id'] + "/comments?limit=50&time_format=U&fields=created_time,message,id,from&&since=" + last_time,
                page=True,
                retry=3, limit=1000)
            for cmt2 in comments2:
                comment_content2 = cmt2['data']
                for each_comment in comment_content2:
                    each_comment["parent_id"] = _id.split("_")[1]
                list_of_comments += comment_content2


def crawl_the_group():
    list_of_posts = []
    list_of_comments = []
    list_of_users = []
    users = graph.get(group_id + "/members".format(last_time), page=True, retry=3, limit=10000)
    for user in users:
        list_of_users += user['data']
    pages = graph.get(group_id + "/feed?limit=50&time_format=U&fields=created_time,message,id,from&&since=" + last_time,
                      page=True, retry=3,
                      limit=1000)

    for pg in pages:
        post_content = pg['data']
        if len(post_content) != 0:
            list_of_posts += post_content
            for post in post_content:
                post_id = post['id']
                get_comments(post_id, list_of_comments)
    return list_of_posts, list_of_comments, list_of_users


post_list, cmt_list, user_list = crawl_the_group()
end_time = str(int(time.time()))
f = open("/home/manh/Desktop/time.txt", "w")
f.write(end_time)
f.close()

for user in user_list:
    user_collection.update({"_id": user["id"]}, {"$set": {"name": user["name"]}}, upsert=True)

for post in post_list:
    print(post["id"].split("_")[1], "1576746889024748", post["message"])
    try:
        # check for banned user
        banned = banned_collection.find_one({"_id": post["from"]["id"]})
        if banned:
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(post["id"], special_token))
        else:
            post_collection.update({"_id": post["id"].split("_")[1]},
                                   {"$set": {"content": post["message"],
                                             "author": post["from"]["name"],
                                             "author_id": post["from"]["id"],
                                             "time": post["created_time"],
                                             "parent_id": "1576746889024748"}}, upsert=True)
    except KeyError:
        pass

for comment in cmt_list:
    print(comment["id"], comment["parent_id"], comment["message"])
    try:
        # check for banned user
        banned = banned_collection.find_one({"_id": comment["from"]["id"]})
        if banned:
            real_post_id = comment["parent_id"] + "_" + comment["id"]
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(real_post_id, special_token))
        else:
            post_collection.update({"_id": comment["id"]},
                                   {"$set": {"content": comment["message"],
                                             "author": comment["from"]["name"],
                                             "author_id": comment["from"]["id"],
                                             "time": comment["created_time"],
                                             "parent_id": comment["parent_id"]}}, upsert=True)
    except KeyError:
        pass
