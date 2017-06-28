#!/usr/bin/env python3

# to be run by cron
from facepy import GraphAPI
import time
import pymongo
import requests

connection = pymongo.MongoClient("ds111262.mlab.com", 11262)
db = connection["adminsitedb"]
db.authenticate("admin", "admin")
post_collection = db['posts']
allpost_collection = db["all_posts"]
banned_collection = db['the_condemned']
history = db['history']
timestamp = db["timestamp"]
computer_id = "1010101010101"

group_id = "1576746889024748"
app_id = "777625919075124"
app_secret = "b9e7ab1c9eabeac21596486e39956faf"
special_token = "EAACEdEose0cBAIA197Buj6ALWZBEuqesRsVIjoeGaOs3r6WCbt7ZBIahGJybrgocLDIJq9fjZAJXWZAp5qyWkqMlq3bGcldBZA0liWXBCZCRgr86ZCIZCAVKY1hkzZA79ZCG9chU9Y7FoPzsvEHPXrtITD5m0kbmKreoj0wxtzY2Fr12exmaM458kV8KJj0whU4H0ZD"

access_token = app_id + "|" + app_secret
graph = GraphAPI(access_token)

time_doc = timestamp.find_one({"_id": "123456789"})
last_time = time_doc["last_time"]

bad_word_repertoire = ["dm", "dcm", "fuck", "ong chu viettel", "vcl", "filter"]


def content_filter(string):
    return any([bad_word in string.lower() for bad_word in bad_word_repertoire])


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
    return list_of_posts, list_of_comments


post_list, cmt_list = crawl_the_group()
end_time = str(int(time.time()))
timestamp.update(time_doc, {"$set": {"last_time": end_time}})

for post in post_list:
    try:
        # check for banned user
        banned = banned_collection.find_one({"_id": post["from"]["id"]})
        if banned:
            # regardless of its status, delete and credit to computer
            history.insert_one({"type": "POST DELETION",
                                "admin_id": computer_id,
                                "reason": "author already banned",
                                "author": post["from"]["name"],
                                "author_id": post["from"]["id"],
                                "content": post["message"]})
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(post["id"], special_token))
        else:
            # the smell test
            if content_filter(post["message"]):
                post_collection.update({"_id": post["id"].split("_")[1]},
                                       {"$set": {"content": post["message"],
                                                 "author": post["from"]["name"],
                                                 "author_id": post["from"]["id"],
                                                 "time": post["created_time"],
                                                 "parent_id": "1576746889024748"}}, upsert=True)
            # pass smell test or not, add it to all post (not happens to banned user posts, which are automatically deleted)
            allpost_collection.update({"_id": post["id"].split("_")[1]},
                                      {"$set": {"content": post["message"],
                                                "author": post["from"]["name"],
                                                "author_id": post["from"]["id"],
                                                "time": post["created_time"],
                                                "parent_id": "1576746889024748"}}, upsert=True)

    except KeyError:
        pass

for comment in cmt_list:
    try:
        # check for banned user
        banned = banned_collection.find_one({"_id": comment["from"]["id"]})
        if banned:
            # regardless of its status, delete and credit to computer
            history.insert_one({"type": "POST DELETION",
                                "admin_id": computer_id,
                                "reason": "author already banned",
                                "author": comment["from"]["name"],
                                "author_id": comment["from"]["id"],
                                "content": comment["message"]})
            real_post_id = comment["parent_id"] + "_" + comment["id"]
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(real_post_id, special_token))
        else:
            # the smell test
            if content_filter(comment["message"]):
                post_collection.update({"_id": comment["id"]},
                                       {"$set": {"content": comment["message"],
                                                 "author": comment["from"]["name"],
                                                 "author_id": comment["from"]["id"],
                                                 "time": comment["created_time"],
                                                 "parent_id": comment["parent_id"]}}, upsert=True)
            # pass smell test or not, add it to all post (not happens to banned user posts, which are automatically deleted)
            allpost_collection.update({"_id": comment["id"]},
                                      {"$set": {"content": comment["message"],
                                                "author": comment["from"]["name"],
                                                "author_id": comment["from"]["id"],
                                                "time": comment["created_time"],
                                                "parent_id": comment["parent_id"]}}, upsert=True)

    except KeyError:
        pass
