from flask import *
from flask_oauthlib.client import OAuth
import pymongo
import config
from bson.json_util import dumps
from facepy import GraphAPI
import requests
from datetime import datetime

app = Flask(__name__)
oauth = OAuth()

# special token for delete only
special_token = "EAACEdEose0cBAHy4B8EJHEkh3mS2BN1yzMYbYQilYS1OnIinEWPgAZAwBIFqVm4E5HY76jHm1MoZAAnZB28NagZAIzOJ8TcgSzhYxWooKHJlRiOvsB6rSZAZBD0yujoh7YyPhUus8OGDMqOwqzY000zFh2ijP1ZCB3XG7EFvQWx023mlFsnMBMBVPmda2ORKm0ZD"

# connect to database
connection = pymongo.MongoClient(config.host, config.port)
db = connection["adminsitedb"]
db.authenticate(config.db_name, config.db_password)
superadmin_list = ["627528440778188", "643833832487975"]
computer_id = "1010101010101"

post_collection = db['posts']
user_collection = db['users']
admin_collection = db['admins']
banned_collection = db['the_condemned']
history = db['history']

# user's ban will be lifted in a week's time
banned_collection.ensure_index("createdAt", expireAfterSeconds=604800)  # equivalent to 1 week

APP_ID = config.APP_ID
APP_SECRET = config.APP_SECRET
app.secret_key = config.secret_key
access_token = APP_ID + "|" + APP_SECRET
group_id = config.GROUP_ID
graph = GraphAPI(access_token)

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=APP_ID,
                            consumer_secret=APP_SECRET,
                            request_token_params={'scope': ['email', 'publish_actions', "user_managed_groups "]}
                            )


@facebook.tokengetter
def get_facebook_token():
    return session.get('oauth_token')


@app.route('/return_data', methods=["GET", "POST"])
def return_data():
    if request.method == 'GET':
        return dumps([post for post in post_collection.find({})])
    else:
        json_post = request.get_json()
        type = json_post.get('type')
        if type == 'post_deletion':
            # add to history
            post_id = json_post.get('id')
            post_to_delete = post_collection.find_one({"_id": post_id})
            reason = json_post.get('reason')
            admin_id = session["current_user"]
            text = post_to_delete['content']
            author = post_to_delete['author']
            author_id = post_to_delete['author_id']
            history.insert_one({"type": "POST DELETION", "admin_id": admin_id, "reason": reason, "content": text, "author": author, "author_id": author_id})
            # delete in db
            post_collection.delete_one(post_to_delete)
            # delete on fb
            real_post_id = post_to_delete["parent_id"] + "_" + post_id
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(real_post_id, special_token))

        elif type == 'user_ban':
            # add to history
            time_ban = json_post.get('timeBan')
            post_id = json_post.get('id')
            admin_id = session["current_user"]
            reason = json_post.get('reason')
            post = post_collection.find_one({"_id": post_id})
            author_name = post["author"]
            author_id = post['author_id']
            content = post["content"]
            history.insert_one({"type": "USER BAN", "admin_id": admin_id, "reason": reason, "author": author_name, "author_id": author_id})
            now = datetime.now()
            timeban = now.isoformat()
            banned_collection.insert_one({"_id": author_id, 'createdAt': datetime.utcnow(), "name": author_name, "timeban": timeban})
            # delete on facebook + delete that single post, credited to computer
            if time_ban == '1':
                real_post_id = post["parent_id"] + "_" + post_id
                history.insert_one({"type": "POST DELETION",
                                    "admin_id": computer_id,
                                    "reason": "author already banned",
                                    "author": author_name,
                                    "author_id": author_id,
                                    "content": content})
                r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(real_post_id, special_token))

            else:
                # delete all posts that are in question (not every post literally), also credited to computer
                id_and_content = [((post["parent_id"] + "_" + post["_id"]), post["content"]) for post in post_collection.find({"author_id": author_id})]
                for each in id_and_content:
                    history.insert_one({"type": "POST DELETION",
                                        "admin_id": computer_id,
                                        "reason": "author already banned",
                                        "author": author_name,
                                        "author_id": author_id,
                                        "content": each[1]})
                    r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                        format(each[0], special_token))
            # delete in db
            post_collection.delete_many({"author_id": author_id})

        elif type == "unban":
            user_id = json_post.get("id")
            reason = json_post.get('reason')
            name = json_post.get('name')
            history.insert_one({"type": "USER UNBAN",
                                "admin_id": session["current_user"],
                                "reason": reason,
                                "author": name,
                                "author_id": user_id,
                                "content": ""})
            banned_collection.delete_one({"_id": user_id})
        return "Log in successfully. Congrats!"


@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@app.route('/ban_list')
def banlist():
    return render_template("banlist.html")


@app.route("/return_banlist")
def return_banlist():
    return dumps([user for user in banned_collection.find({})])


@app.route("/history")
def history_page():
    return render_template("history.html")


@app.route("/return_history")
def return_history():
    if session['superstatus'] == 'F':
        return dumps([item for item in history.find({"admin_id": session["current_user"]})])
    return dumps(item for item in history.find({}))


@app.route("/main")
def mainpage():
    # test
    # session["current_user"] = "643833832487975"
    # session["image"] = "https://scontent.fhan3-1.fna.fbcdn.net/v/t1.0-9/10696343_287006974837331_256486935600665516_n.jpg?oh=8fcd53c6c3ff46587379e0ef11f4751c&oe=59CDEFDE"
    # session['superstatus'] = "T"
    # test
    return render_template("main.html")


@app.route("/logout")
def log_out():
    session.pop('current_user')
    session.pop('image')
    session.pop('superstatus')
    return redirect(url_for("authentication_page"))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=id,name,picture,groups')
    # check with db
    if group_id in [group["id"] for group in me.data["groups"]["data"]]:
        session['image'] = me.data['picture']['data']['url']
        session["current_user"] = me.data['id']
        if me.data['id'] in superadmin_list:
            session['superstatus'] = "T"
        else:
            session["superstatus"] = "F"
        return redirect(url_for('mainpage'))
    return "Well well well... What do we have here? A burglar, or a thief? I know who you are user {}".format(me.data['id'])


@app.route('/', methods=['GET', 'POST'])
def authentication_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return redirect(url_for("login"))


@app.route('/return_admin_info')
def return_admin_info():
    name = admin_collection.find_one({"_id": session["current_user"]})["name"]
    post_deleted = len(list((history.find({"admin_id": session["current_user"], "type": "POST DELETION"}))))
    user_banned = len(list(history.find({"admin_id": session["current_user"], "type": "USER BAN"})))
    return dumps([name, session['image'], post_deleted, user_banned, session['superstatus'], session["current_user"]])


@app.route("/return_admins")
def return_admins():
    return dumps([(admin["name"],
                   len(list((history.find({"admin_id": admin["_id"], "type": "POST DELETION"})))),
                   len(list(history.find({"admin_id": admin["_id"], "type": "USER BAN"}))))
                  for admin in admin_collection.find({})])

if __name__ == '__main__':
    app.run()