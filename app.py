from flask import *
from flask_oauthlib.client import OAuth
import pymongo
import config
from bson.json_util import dumps
from facepy import GraphAPI
import requests

# special access token used for delete only
special_token = "EAACEdEose0cBANoyeSET7hzZBgM4omTDRfK41LDZClIQRSd4tWQZBfvGQYjxRA2XNTv3weVTmClGx8axZBCgeQJVkNE2ZCtAq89GGKQrZAX3fRD9KsFIkiFOKrGDbEay1GfZB53yg1SB97YbCWEV5njVZAOz3xT2kmgZA1gMupiZAj0r3lCJs91GbGD51XdSH4URoZD"

app = Flask(__name__)
oauth = OAuth()

# connect to database
connection = pymongo.MongoClient(config.host, config.port)
db = connection["adminsitedb"]
db.authenticate(config.db_name, config.db_password)

post_collection = db['posts']
user_collection = db['users']
admin_collection = db['admins']
history = db['history']
hereherehere = "hearhearhear"
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
            real_post_id = group_id + "_" + post_id
            # update admin's number
            admin_collection.update({"_id": session["current_user"]}, {"$inc": {'post_deleted': 1}})
            r = requests.delete("https://graph.facebook.com/DELETE /v2.9/{}".format(real_post_id), params={'access_token': special_token})
        return "Log in successfully. Congrats!"


@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None, _external=True))


@app.route('/ban_list')
def banlist():
    return render_template("ban_list.html")


@app.route("/history")
def history_page():
    return render_template("history.html", name=session['admin_name'], picture=session['image'], post_num=0, user_num=0)


@app.route("/return_history")
def return_history():
    return dumps([item for item in history.find({})])


@app.route("/main")
def mainpage():
    # the lines below are for testing purposes only -- remember to delete them
    return render_template("main.html", name=session['admin_name'], picture=session['image'], post_num=0, user_num=0)


@app.route("/logout")
def log_out():
    session.pop('current_user')
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
        session['current_user'] = me.data['id']
        session['image'] = me.data['picture']['data']['url']
        session['admin_name'] = me.data['name']
        return redirect(url_for('mainpage'))
    return "Well well well... What do we have here? A burglar, or a thief? I know who you are user {}".format(me.data['id'])


@app.route('/', methods=['GET', 'POST'])
def authentication_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.run()
