
$project
========

A site to facilitate the burden of managing large Facebook groups.  

Features
--------
- Automatically pull posts and comments from facebook group
- Delete posts/comments
- Ban/Unban user for an extended period of time
- Automatically filter posts/comments from banned users or contain offensive content

Installation
------------

Install $project by running:
- Create an application on heroku.com here: www.heroku.com
- Create a mlab account here: https://mlab.com/ (for database)
- Create a database named adminsitedb
- Create a collection inside the database named timestamp.
- In timestamp collection add a document: {"last_time": "1"}
- Add environment variable to heroku environment:
		APP_ID = {your facebook app id} 
		APP_SECRET = {your facebook app secret}
		db_name = {your mlab's admin name, not to be confused with your mlab's account's name} You can find it on mlab database's user tab 
		db_password {your mlab's admin password, not to be confused with your mlab's account's password} You can find it on mlab's database user tab 
		GROUP_ID = {Your facebook group id}
		host = {your mlab assigned host} i.e. ds111262.mlab.com 
		port = {your mlab assigned port} i.e. 11260
		secret_key = {your flask secret key} you could invent one yourself, as randomly as possible
		special_token = {your temporary facebook graph api user access token with all permission granted}
- Go to file env_var.json and fill in similar variable
- Run cron_script.py file to update all previous posts/comments
- Add a cron job to run cron_script.py every five minutes

Further customization
------------
To customize superadmins, add the facebook id (string type) of admin to the array(list) superadmin_list on line 22 in file app.py
To customize your reasons (for ban/delete), look for tag select in file main.html from line 72 to line 80 
To customize words that would trigger filter, look for array(list) bad_word_repertoire in file cron_script.py on line 30.

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: manhnguyenhuu7898@gmail.com

License
-------

The project is licensed under the BSD license.


