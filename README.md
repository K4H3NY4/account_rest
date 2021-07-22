# Account Rest API


[![Code Quality Score](https://www.code-inspector.com/project/25575/score/svg)]
[![Code_Quality_Status](https://www.code-inspector.com/project/25575/status/svg)]

- [Flask] 
- [Sql Alchemy]
- [Twilio]
- [Flask Cors] 
- [Bootstrap CSS] 


## Installation

Install the dependencies and start the server.

```sh
pip3 install flask
pip3 install flask_alchemy
pip3 install flask_cors
pip3 install twilio

python3 run app.py
```


 Enter server address in your preferred browser.

```sh
127.0.0.1:5000
```


## End Points


| End point | Method  | json |
| ------ | ------ | ----------|
| / | get | |
| /register |post | {"first_name":"","last_name":"",    "email":"",    "phone":"",   "password":""}|
| /login | get | {"email":"","password":""} |
| /logout | post|
| /profile | get|
| /change-password |put|{"new_password":"","confirm_password":""}|
|/forgot-password |put |{"email":""}|
|/add-message|post| {"message":"","receiver_number":"","time_scheduled":""} |
|/single-message/{id}|get|  |
|/messages|get|
|/change-message|put|{"message": ""}|
|/change-status|put|{"status": ""}|
|/delete-message/{id}|del|
|/display-twilio-keys|get|
|/add-twilio-keys|post| {"account_sid":"","auth_token":"","code":""} |
|/delete-twilio-keys/{id}|del|
|/edit-twilio-keys|put|{"account_sid":"","auth_token":"","code":""} |






