from scraper import *
import pymongo
import config

connection = pymongo.MongoClient(config.host, config.port)
db = connection["adminsitedb"]
db.authenticate(config.db_name, config.db_password)
post_collection = db['posts']
user_collection = db['users']
history = db['history']
banned_collection = db['the_condemned']

# clear database
post_collection.delete_many({})
user_collection.delete_many({})
history.delete_many({})
banned_collection.delete_many({})

posts, comments, users = crawl_the_group()
for user in users:
    user_collection.insert_one({"_id": user["id"], "name": user["name"]})
for post in posts:
    try:
        post_collection.insert_one({"_id": post["id"].split("_")[1],
                                    "content": post["message"],
                                    "author": post["from"]["name"],
                                    "author_id": post["from"]["id"],
                                    "time": post["created_time"]})
    except KeyError:
        print("No key")
for comment in comments:
    try:
        post_collection.insert_one({"_id": comment["id"],
                                    "content": comment["message"],
                                    "author": comment["from"]["name"],
                                    "author_id": comment["from"]["id"],
                                    "time": comment["created_time"]})
    except KeyError:
        print("No key")
