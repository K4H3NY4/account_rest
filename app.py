from flask import Flask, request, jsonify, session ,make_response
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import random
import datetime
from twilio.rest import Client
from flask_cors import CORS


#init application
app = Flask(__name__)
CORS(app)

#setting base directory path

#config database
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.update(
PERMANENT_SESSION_LIFETIME=600,
SESSION_COOKIE_SECURE=True,
SESSION_COOKIE_HTTPONLY=False,
)

db = SQLAlchemy(app)

app.secret_key = 'random secret key'


#user class

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String,unique=True)
    password = db.Column(db.String)

    def __init__(self, first_name,last_name,email,phone,password):
        self.first_name = first_name 
        self.last_name = last_name
        self.email = email
        self.password = password
        self.phone = phone



#message class
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    status = db.Column(db.String, default='Scheduled')
    receiver_number = db.Column(db.String)
    time_scheduled = db.Column(db.String)
    created_at = db.Column(db.String)
    user_id =db.Column(db.Integer, db.ForeignKey('user.id') )

    def __init__(self,message,status,receiver_number,time_scheduled,created_at,user_id):
        self.message = message
        self.status = status
        self.receiver_number = receiver_number
        self.time_scheduled = time_scheduled
        self.created_at = created_at
        self.user_id = user_id
   
      
class Twilio_keys(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    account_sid = db.Column(db.String, unique=True)
    auth_token = db.Column(db.String, unique=True)
    code = db.Column(db.String)

    def __init__(self,account_sid,auth_token,code):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.code = code


@app.route('/', methods=['GET'])
def get():
    return 'Welcome to Account REST API'    



#register user
@app.route('/register', methods=['POST'])
def add_user():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    phone = request.json['phone']
    password = request.json['password']

 
    conn = sqlite3.connect('database.db')
    conn_db = conn.cursor()
    conn_db.execute("SELECT * FROM user where email = ? OR phone = ?;",(email,phone))
    record = conn_db.fetchall()
    if(len(record) == 0):
        new_user = User(first_name,last_name,email,phone,password)
        db.session.add(new_user)
        db.session.commit()

        response ='User account created'
        return response
    else:
        response = "User email or phone already exists"
        return response


  
#login user
@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    try:
        user_profile = User.query.filter_by(email=email).first()

        if( user_profile.password == password):
            #return str(user_profile)
            return jsonify(id=user_profile.id,
                           first_name=user_profile.first_name,
                           last_name=user_profile.last_name,
                           success=1
                        
            
            )
        else:
            return jsonify(message='Password Error',
                           
                           success=0
            
            )

    except:
        return jsonify(message='Email Error',
                           
                           status=0
            
            )
    

#user profile
@app.route('/profile', methods=['GET'])
def profile():
    try:
        user_id = request.json['user_id']
        user_profile = User.query.get(user_id)
        #return session["user_id"]
    
        return jsonify(        
            first_name=user_profile.first_name,
            last_name=user_profile.last_name,
            phone=user_profile.phone   
            )
    except:
        return 'Please login'

#edit firstname
@app.route('/edit', methods=['PUT'])
def edit():
    try:
        user_id = request.json['user_id']
        user = User.query.get(user_id)
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        user.first_name = first_name
        user.last_name = last_name
        db.session.commit()
        return 'record updated'
    except:
        return 'login to edit profile'

#reset password
@app.route('/change-password', methods=['PUT'])
def edit_password():
    try:
        user_id = request.json['user_id']
        user = User.query.get(user_id)
        new_password = request.json['new_password']
        confirm_password = request.json['confirm_password']
        if(new_password == confirm_password):
            user.password = confirm_password
            db.session.commit()
            return 'Password Successfully Changed'
        else:
            return 'Error: Passwords do not match'
    except:
        return 'login to change password'


#forget password
@app.route('/forgot-password', methods=['PUT'])
def forgot_password():
    try:
        email = request.json['email']
        user_email = User.query.filter_by(email=email).first()
        email=user_email.email
        e = ['a','b','c','e','d','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        random.shuffle(e)
        easy_password = "" 
        password_gen = easy_password.join(e)
        password = password_gen[:7]
        user_email.password = password
        db.session.commit()  

        send_ph = 'whatsapp:'+str(user_email.phone)
        twilio_key =Twilio_keys.query.limit(1).first()
        client = Client(twilio_key.account_sid, twilio_key.auth_token) 
        messages = "*PASSWORD RESET*. Your new password is *" + password + "*"
        #message = client.messages.create(from_='whatsapp:+14155238886',body=messages,to=send_ph ) 
            
        return 'Success: Password was reset'
        #return jsonify(email=user_email.email)

    except:
        return 'Email does not exist'





#add message
@app.route('/add-message', methods=['POST'])
def add_message():
    try:
        x = datetime.datetime.now()
        current_time = x.strftime("%d""-""%B""-""%Y"" ""%H"":""%M")
        current_date = str(current_time)
        #def __init__(self,message,status,receiver_number,time_scheduled,created_at,user_id):
        
        message = request.json['message']
        receiver_number = request.json['receiver_number']
        time_scheduled = request.json['time_scheduled']
        user_id = request.json['user_id']
        status = 'Scheduled'
        created_at = current_date
    
        new_message = Message(message,status,receiver_number,time_scheduled,created_at,user_id)
        db.session.add(new_message)
        db.session.commit()
        return 'Message added'
    except:
        return 'Error: Message not added '


#display all messages
@app.route('/messages', methods=['POST'])
def all_messages():
        user = request.json['user_id']
        user_messages = Message.query.filter_by(user_id=user).all()
        output =[]
        for user_message in user_messages:
            user_message_data={}
            user_message_data['message']=user_message.message
            user_message_data['receiver_number']=user_message.receiver_number
            user_message_data['status']=user_message.status
            user_message_data['time_scheduled']=user_message.time_scheduled
            output.append(user_message_data)

        return jsonify({"user_messages":output})


  

#display one message
@app.route('/message/<int:id>', methods=['GET'])
def single_message(id):
    try:
        user_messages = Message.query.get(id)
        user_id = request.json['user_id']
        if(user_messages.user_id == int(user_id)):
        
            return jsonify(        
                    message=user_messages.message,
                    receiver_number = user_messages.receiver_number,
                    status = user_messages.status,
                    time_scheduled = user_messages.time_scheduled
                    )
        else:
            return 'Error: Message not found'

    except:
        return 'Error: Something went wrong'

#delete one message
@app.route('/message/<int:id>', methods=['DELETE'])
def delete_message(id):
    try:
        user_messages = Message.query.get(id)
        user_id = request.json['user_id']
        if(user_messages.user_id == int(user_id)):
            db.session.delete(user_messages)
            db.session.commit()
        
            return 'Message deleted'
        else:
            return 'Error: Message not found'

    except:
        return 'Error: Something went wrong'


#change message content
@app.route('/message/<int:id>/content', methods=['PUT'])
def change_content(id):
    try:
        user_messages = Message.query.get(id)
        message = request.json['message']
         

        if(user_messages.user_id == int(session["user_id"])):
            user_messages.message = message
            db.session.commit()
            
            return 'Success: Message was updated'
        else:
                return 'Error: Message not found'
    except:
        return 'Error: Something went wrong'

#change status
@app.route('/message/<int:id>/status', methods = ['PUT'])
def change_status(id):
    try:
        user_id = request.json['user_id']
        user_messages = Message.query.get(id)
        status = request.json['status']
        
        if(user_messages.user_id == int(user_id)):
            user_messages.status = status
            db.session.commit()
            
            return 'Success: Status was Changed'
        else:
                return 'Error: Message not found' 
    except:
        return 'Error: Something went wrong'


#add twilio keys
@app.route('/twilio', methods =['POST'])
def add_keys():
    account_sid = request.json['account_sid']
    auth_token = request.json['auth_token']
    code = request.json['code']
    try:
        new_keys = Twilio_keys(account_sid,auth_token,code)
        db.session.add(new_keys)
        db.session.commit()
        return 'twilio keys added'
    except:
        return 'Keys already exists'



#display Key
@app.route('/twilio', methods=['GET'])
def display_keys():
    twilio_key =Twilio_keys.query.limit(1).first()
    return jsonify(
        account_sid = twilio_key.account_sid,
        auth_token = twilio_key.auth_token,
        code = twilio_key.code
    )


#edit twilio keys
@app.route('/twilio', methods =['PUT'])
def edit_keys():
    account_sid = request.json['account_sid']
    auth_token = request.json['auth_token']
    code = request.json['code']
    try:
        new_keys = Twilio_keys(account_sid,auth_token,code)
        #db.session.add(new_keys)
        db.session.commit()
        return 'twilio keys updated'
    except:
        return 'Keys already exists'

#delete twilio key
@app.route('/twilio/<int:id>', methods=['DELETE'])
def delete_keys(id):
    try:
       
        twilio_key = Twilio_keys.query.get(id)
        db.session.delete(twilio_key)
        db.session.commit()
        return 'Keys deleted'      

    except:
        return 'Error: Something went wrong'


#logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return 'successful logged out'





if __name__ == "__main__":
    
    app.run(debug=True)
    












