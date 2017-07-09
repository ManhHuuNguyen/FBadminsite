from facepy import GraphAPI

group_id = "1513217328975937"
app_id = "624189277737439"
app_secret = "6f176cd13fc63799de5dc8357acccfcc"

access_token = app_id + "|" + app_secret
graph = GraphAPI(access_token)

file = open('training_File.csv', 'w')


def get_comments(_id):
    comments = graph.get(_id + "/comments?fields=message", page=True,
                         retry=3, limit=1000)
    for cmt in comments:
        comment_content = cmt['data']
        for content in comment_content:
            file.write(content["message"])
            file.write("\n")
            comments2 = graph.get(content['id'] + "/comments?fields=message", page=True, retry=3, limit=1000)
            for cmt2 in comments2:
                comment_content2 = cmt2['data']
                for each_cmt2 in comment_content2:
                    file.write(each_cmt2["message"])
                    file.write("\n")


def crawl_the_group():
    pages = graph.get(group_id + "/feed?&fields=message", page=True, retry=3, limit=1000)
    i = 0
    for pg in pages:
        print("pg " + str(i))
        i += 1
        post_content = pg['data']
        if len(post_content) != 0:
            for post in post_content:
                post_id = post['id']
                try:
                    file.write(post["message"])
                    file.write("\n")
                    get_comments(post_id)
                except KeyError:
                    pass


crawl_the_group()
