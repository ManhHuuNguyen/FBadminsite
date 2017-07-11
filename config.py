# # testgroup
# APP_ID = "777625919075124"
# APP_SECRET = "b9e7ab1c9eabeac21596486e39956faf"
# GROUP_ID = "1576746889024748"
#
# secret_key = 'lfka1fjgakeqw12ereqtyropmjdrezsddmvmb124'
#
# # mongo host
# host = "ds111262.mlab.com"
# # mongo port
# port = 11262
#
# # db
# db_name = "admin"
# db_password = "admin"
import os
APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
GROUP_ID = os.environ.get("GROUP_ID")

secret_key = os.environ.get("secret_key")
host = os.environ.get("host")
port = os.environ.get("port")
db_name = os.environ.get("db_name")
db_password = os.environ.get("db_password")