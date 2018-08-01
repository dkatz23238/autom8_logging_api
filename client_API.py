import requests
import json
import datetime

class autom8_logging_client(object):

    """ connects via HTTP to secured RPA logging server """

    def __init__(self, username, robot_name, token, base_url):
        self.base_url = base_url
        self.username = username
        self.robot_name = robot_name
        self.token = token
        self.start_confirmation_sent = False
        self.start_confirmation_data = []
        self.start_confirmation_success = False
        self.end_confirmation_sent = False
        self.end_confirmation_data = []
        self.end_confirmation_success = False
        self.reprstr = "autom8 logging client // Robot Name: %s // Username: %s" %(self.robot_name, self.username)

        self.valid_conection = False

        #checks if token is valid

        validity_check_data = {"logging_token":self.token,
                               "username":self.username,
                                "robot_name":self.robot_name}
        validity_check_data_json = json.dumps(validity_check_data)

        response = requests.post(url=r"%s/api/check_robot_token"%self.base_url,
                                 data=validity_check_data_json)

        response_dict = json.loads(response.content)

        if response_dict["status"] == "success":
            self.valid_conection = True
        elif response_dict["status"] == "failed":
            self.valid_conection = False


        self.validate_print()
    def __str__(self):
        return self.reprstr

    def __repr__(self):
        return self.reprstr

    def start_bot(self):
        """ sends start signal to autom8 logging platform """

        endpoint = r"%s/api/log"%self.base_url
        data_dict = {"logging_token":self.token,
                     "username":self.username,
                     "robot_name":self.robot_name,
                     "log_string":"start_bot_confirmation",
                     "log_type":"start_bot"}

        post = requests.post(url=endpoint, data = json.dumps(data_dict))
        if post.status_code == 200:
            self.start_confirmation_sent = True
            self.start_confirmation_data.append(json.loads(post.content))
            if self.start_confirmation_data[-1]["status"] == "success":
                self.start_confirmation_success = True
            else:
                print("start ping failed please check credentials and token")
            print("Success: robot start ping sent at %s" %str(datetime.datetime.now()))
        else:
            print("Error: robot start ping failed")

        return post

    def end_bot(self):
        """ sends start signal to autom8 logging platform """

        endpoint = r"%s/api/log"%self.base_url
        data_dict = {"logging_token":self.token,
                     "username":self.username,
                     "robot_name":self.robot_name,
                     "log_string":"end_bot_confirmation: process complete",
                     "log_type":"end_bot"}

        post = requests.post(url=endpoint, data = json.dumps(data_dict))
        if post.status_code == 200:
            self.end_confirmation_sent = True
            self.end_confirmation_data.append(json.loads(post.content))
            if self.end_confirmation_data[-1]["status"] == "success":
                self.end_confirmation_success = True
            else:
                print("start ping failed please check credentials and token")
            print("Success: robot end ping sent at %s" %str(datetime.datetime.now()))
        else:
            print("Error: robot end ping failed")

        return post

    def log_message(self, log_string):
        """ sends start signal to autom8 logging platform """

        endpoint = r"%s/api/log"%self.base_url

        data_dict = {"logging_token":self.token,
                     "username":self.username,
                     "robot_name":self.robot_name,
                     "log_string":log_string,
                     "log_type":"regular_log"}

        post = requests.post(url=endpoint, data = json.dumps(data_dict))

        if post.status_code == 200:
            pass

        return post

    def validate_print(self):
        if self.valid_conection == False:
            print("TOKEN ERROR PLEASE CHECK CREDENTIALS")
        else:
            print("TOKEN AUTHENTICATION SUCCESS!")

client = autom8_logging_client(username="david",
                               robot_name="testbot_003",
                               token="13c63eb8-f8c7-4858-91fc-00f403d4749e",
                               base_url=r"http://127.0.0.1:8080")

client.start_bot()
client.log_message("I am doing this.")
client.end_bot()
