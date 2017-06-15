from facepy import GraphAPI
import config

group_id = config.GROUP_ID
app_id = config.APP_ID
app_secret = config.APP_SECRET

access_token = app_id + "|" + app_secret
graph = GraphAPI(access_token)


def get_comments(_id, list_of_comments):
    comments = graph.get(_id + "/comments?limit=50&time_format=U&fields=created_time,message,id,from", page=True,
                         retry=3, limit=1000)
    for cmt in comments:
        comment_content = cmt['data']
        list_of_comments += comment_content
        for content in comment_content:
            comments2 = graph.get(
                content['id'] + "/comments?limit=50&time_format=U&fields=created_time,message,id,from", page=True,
                retry=3, limit=1000)
            for cmt2 in comments2:
                comment_content2 = cmt2['data']
                list_of_comments += comment_content2


def crawl_the_group():
    list_of_posts = []
    list_of_comments = []
    list_of_users = []
    users = graph.get(group_id + "/members", page=True, retry=3, limit=10000)
    for user in users:
        list_of_users += user['data']
    pages = graph.get(group_id + "/feed?limit=50&time_format=U&fields=created_time,message,id,from", page=True, retry=3,
                      limit=1000)
    i = 0
    for pg in pages:
        print("pg " + str(i))
        i += 1
        post_content = pg['data']
        if len(post_content) != 0:
            list_of_posts += post_content
            for post in post_content:
                post_id = post['id']
                get_comments(post_id, list_of_comments)
    return list_of_posts, list_of_comments, list_of_users


# post_list, cmt_list, user_list = crawl_the_group()
# for cmt in cmt_list:
#     print(cmt)
# for post in post_list:
#     print(post)
# for user in user_list:
#     print(user)
