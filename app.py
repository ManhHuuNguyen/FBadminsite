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
special_token = "EAACEdEose0cBANWZAVUi5u48QZA29GatILHpcZBLC3ccbmUscpuUCe2JoZC7dFWZCMyEzLYGb03lBMm7SDkYsgEpWrrzBKHYWZB1GHlq92AiAZB8r2JzOwf6ABFi9nQ4ZC6hnoCVU3eGmapYUZCzHK5Ita5sZCN86qVuHxjrSff82IJivdAoo3MZCxaYzCl7KiVEZBYZD"

# connect to database
connection = pymongo.MongoClient(config.host, config.port)
db = connection["adminsitedb"]
db.authenticate(config.db_name, config.db_password)

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
            print(real_post_id)
            r = requests.delete("https://graph.facebook.com/{}?method=delete&access_token={}".
                                format(real_post_id, special_token))
            # update admin's number
            admin_collection.update({"_id": session["current_user"]}, {"$inc": {'post_deleted': 1}})

        elif type == 'user_ban':
            # add to history
            author_id = json_post.get('id')
            admin_id = session["current_user"]
            reason = json_post.get('reason')
            author = user_collection.find_one({"_id": author_id})
            author_name = author["name"]
            history.insert_one({"type": "USER BAN", "admin_id": admin_id, "reason": reason, "author": author_name, "author_id": author_id})
            # add to list of the condemned
            banned_collection.insert_one({"_id": author_id, 'createdAt': datetime.utcnow(), "name": author["name"]})
            # delete in db
            post_collection.delete_many({"author_id": author_id})
            # delete on facebook
            # update admin's number
            admin_collection.update({"_id": session["current_user"]}, {"$inc": {'user_banned': 1}})

        elif type == "unban":
            user_id = json_post.get("id")
            banned_collection.delete_one({"_id": user_id})
        return "Log in successfully. Congrats!"


@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@app.route('/ban_list')
def banlist():
    if "current_user" in session:
        return render_template("ban_list.html")
    return render_template("bad_request.html")


@app.route("/return_banlist")
def return_banlist():
    return dumps([user for user in banned_collection.find({})])


@app.route("/history")
def history_page():
    if "current_user" in session:
        return render_template("history.html")
    return render_template("bad_request.html")


@app.route("/return_history")
def return_history():
    if session['superstatus'] == 'F':
        return dumps([item for item in history.find({"admin_id": session["current_user"]})])
    return dumps(item for item in history.find({}))


@app.route("/main")
def mainpage():
    if "current_user" in session:
    # test
    # session["current_user"] = "643833832487975"
    # session["image"] = "https://www.google.org/assets/static/images/logo_googledotorg-171e7482e5523603fc0eed236dd772d8.svg"
    # session['superstatus'] = "T"
    # test
        print(session["current_user"])
        return render_template("main.html")
    return render_template("bad_request.html")


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
    me = facebook.get('/me?fields=id,name,picture')
    # check with db
    result = admin_collection.find_one({"_id": me.data['id']})
    if result:
        session['image'] = me.data['picture']['data']['url']
        session["current_user"] = me.data['id']
        session['superstatus'] = result['superstatus']
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
    result = admin_collection.find_one({"_id": session["current_user"]})
    return dumps([result['name'], session['image'], result['post_deleted'], result['user_banned'], result['superstatus']])


@app.route("/return_admins")
def return_admins():
    return dumps([admin for admin in admin_collection.find({})])

if __name__ == '__main__':
    app.run()
