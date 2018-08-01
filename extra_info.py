
url = r"http://127.0.0.1:8080/api/new_robot"
new_robot = {"username":"david", "robot_name":"testbot_003", "password":"david"}
json_data = json.dumps(new_robot)

token_response = requests.post(url=url, data=json_data)
token_dict = json.loads(token_response.content)
token = token_dict["logging_token"] #token for this robot is '13c63eb8-f8c7-4858-91fc-00f403d4749e'
