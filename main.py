from flask import Flask, jsonify, request
import pymongo
import pprint
import datetime
import json
import uuid

def myround(num):
    return round(num, 2)

class DataBase(object):
    """ autom8 logging prototype: MongoDB Client"""

    client = 'mongodb://localhost:27017/'
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(DataBase.client)
        DataBase.DATABASE = client["autom8_database"]
        pprint.pprint("Connection Success!")
        DataBase.user_collection = DataBase.DATABASE["users"]
        DataBase.bot_collection = DataBase.DATABASE["robots"]
        DataBase.log_collection = DataBase.DATABASE["logs"]

    @staticmethod
    def new_user(username, password):
        if len(list(db.user_collection.find({"username":"%s"%username}))) > 0:
            return "Please Choose A New User Name"
        else:
            data = {}
            data["username"] = username
            data["password"]  = password
            DataBase.user_collection.insert_one(data)
            return data

    @staticmethod
    def new_bot(username, password, bot_name):
        query_1 = list(DataBase.user_collection.find({"username":"%s"%username}))
        if len(query_1) == 1:
            real_pass = query_1[0]["password"]
            register_success = (real_pass == password)
        else:
            return "no user found"

        if not register_success:
            return "user password failed"
        else:
            query_2 = list(DataBase.bot_collection.find({"username":"%s"%username,
                                                   "robot_name":"%s"%bot_name}))
            print(query_2)

            if len(query_2) == 0:
                data = {}
                logging_token = str(uuid.uuid1())
                data["username"] = username
                data["robot_name"] = bot_name
                data["logging_token"]  = logging_token
                data["creation_time"] = str(datetime.datetime.now())
                DataBase.bot_collection.insert_one(data)
                print("Robot Created Success. Your logging token is: %s"%logging_token)
                return logging_token
            else:
                return "robot already created!"

    @staticmethod
    def insert_log(token, robot_name, log_string, username, log_type):
        query_1 = list(DataBase.bot_collection.find({"username":username, "robot_name":robot_name}))
        if query_1[0]["logging_token"] == token:
            data = {}
            data["robot_name"] = robot_name
            data["username"] = username
            data["log_string"] = log_string
            data["log_type"] =  log_type
            data["datetime"] = str(datetime.datetime.now())
            DataBase.log_collection.insert_one(data)
            print("pushed to db")
            return data
        else:
            return "Token Incorrect !"

    @staticmethod
    def check_if_robot_and_token_exist(token, robot_name, username):
        query = list(DataBase.bot_collection.find({"username":"%s"%username, "robot_name":"%s"%robot_name}))

        if len(query) == 0:
            return False

        elif query[0]["logging_token"] != token:
            return False
        else:
            return True



app = Flask(__name__)
db = DataBase()
db.initialize()


#post request with json format {"username":"miguelgarma", "password":"miguelgarma"}
@app.route('/api/new_user', methods=['POST'])
def create_user(db=db):
        data = json.loads(request.data)
        username = data["username"]
        print("username: %s"%username)
        password = data["password"]
        print("password: %s"%password)
        print("trying result...")
        result = db.new_user(username=username, password=password)

        if result == "Please Choose A New User Name":

            return jsonify({"message":"error, user already exists"})
        else:
            pass

        return jsonify({"message":"user created!"})

#new robot will create a new bot {"username":"miguelgarma", "robot_name":"newRobot", "password":"miguelgarma"}
# it will return a token {
#    "logging_token": "c21e6305-8fa5-4a5d-b913-3a79a8431379",
#    "robot_name": "newRobot",
#    "username": "miguelgarma"}

@app.route('/api/new_robot', methods=['POST'])
def create_bot(db=db):
        data = json.loads(request.data)
        username = data["username"]
        bot_name = data["robot_name"]
        password = data["password"]

        result = db.new_bot(username, password, bot_name)

        if ((result == "no user found") or (result == "robot already created!") or (result == "user password failed")):
            return jsonify({"message":result})
        else:
            logging_token = result


        final_result = {"username":username, "robot_name":bot_name, "logging_token":logging_token}
        return jsonify(final_result)

#With the token you can log your RPA
# {"logging_token":"c21e6305-8fa5-4a5d-b913-3a79a8431379", "username":"miguelgarma", "robot_name":"newRobot", "log_string":"Hello World !", "log_type":"regular_log" }
@app.route('/api/log', methods=['POST'])
def create_log(db=db):
        data = json.loads(request.data)
        logging_token = data["logging_token"]
        username = data["username"]
        robot_name = data["robot_name"]
        log_string = data["log_string"]
        log_type = data["log_type"]

        result = db.insert_log(logging_token, robot_name, log_string, username, log_type)

        if (result == "Token Incorrect !"):

            return jsonify({"message":result})
        else:
            myResult = result

        print(myResult)
        final_result = myResult
        final_result["status"] = "success"
        final_result["_id"] = str(final_result["_id"])
        return jsonify(final_result)

@app.route('/api/check_robot_token', methods=['POST'])
def check_robot_token_api(db=db):
        data = json.loads(request.data)
        logging_token = data["logging_token"]
        username = data["username"]
        robot_name = data["robot_name"]

        result = db.check_if_robot_and_token_exist(token=logging_token, robot_name=robot_name, username=username)

        if result == True:
            final_result = {"message":"token authentication success", "status":"success"}
        elif result == False:
            final_result = {"message":"token authentication failed", "status":"failed"}


        print(result)
        return jsonify(final_result)



if __name__ == '__main__':
    app.run(debug=True, port=8080)
