from flask import Flask, url_for, redirect, request, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from flask_migrate import Migrate


app = Flask(__name__)
############DB###########
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
Base = declarative_base()
migrate = Migrate(app, db)



class UserLevels(db.Model):
    __tablename__ = "user_levels"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(13), nullable=False)
    level = db.Column(db.Integer, nullable=False)


class Users(db.Model, Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.Integer, nullable=False, unique=True)
    phone_number = db.Column(db.String(13), nullable=False)
    user_creds_ = db.relationship("UserCredentials", backref="user")


class UserCredentials(db.Model, Base):
    __tablename__ = "users_creds"
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


db.create_all()
details_entered = []

@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global details_entered
    level = 0 
    hospitals = ["Wanige Health hospital", "Kiambu county hospital", "Tigoni Hospital ", "Kihara Hospital"]
    session_id = request.values.get("sessionId", None)
    serviceCode = request.values.get("serviceCode", None)
    phoneNumber = request.values.get("phoneNumber", None)
    text = request.values.get("text", None)
    text = text.split("*")[-1]
    
    exists = UserLevels.query.filter_by(phone_number=phoneNumber).first()
    if exists:
        exists.session_id = session_id
        db.session.commit()
        level_ = UserLevels.query.filter_by(session_id=session_id).first()
        if level_:
            level = level_.level
    else:
        user_level = UserLevels(session_id=session_id, phone_number=phoneNumber,
                                level=level)
        db.session.add(user_level)
        db.session.commit()
    if level == 7:
        response = "END Login"
    if level == 5: 
        try:               
            text = hospitals[int(text)-1]
        except ValueError: 
            level = 4

    if level == 6 and text == "1":
        details_entered.clear()
        details_entered.append("")        
        level = 0
    details_entered.append(text)
    
    if text == "":
        if level == 0:
            response = "CON Welcome to medics health care \n"
            response += "1. Register \n"
        elif level == 1:
            response = "CON First Name can not be empty!\n"
            response += "Enter a Valid First Name\n"
        elif level == 2:
            response = "CON Last Name can not be empty!\n"
            response += "Enter a valid Last Name"
        elif level == 3:
            response = "CON ID Number cannot be empty!\n"
            response += "Enter a valid ID Number"
        elif level == 4:
            response = "CON City cannot be empty!\n"
            response += "Enter a valid city"
        elif level == 5:
            response = "CON Your preferred public hospital can not be empty!\n"
            response += "Enter a valid public hospital"
    else:
        level += 1
        current_user_level = UserLevels.query.filter_by(session_id=session_id).first()
        current_user_level.level = level
        db.session.commit()
    if text:
        if level == 1:
            response = "CON Enter your first name\n"
        elif level == 2:
            response = "CON Enter your last name\n"
        elif level == 3:
            response = "CON Enter your ID Number\n"
        elif level == 4:
            response = "CON Enter your city\n"
        elif level == 5:
            response = "CON Choose your preferred public hospital\n" \
                       "1. Wangige sub county hospital\n" \
                       "2. Kiambu county hospital\n" \
                       "3. Tigoni hospital\n" \
                       "4. Kihara hospital\n"
        elif level == 6:
            response = "CON Your details are as follows \n"
            details_entered = details_entered[2:]
            for i in range (0, len(details_entered)):
                response += f"{details_entered[i]}\n"
            response += "Would you like to edit?\n"
            response += "1. YES\n"
            response += "2. NO\n"
        elif level == 7:
            response = "END Your details have been captured correctly\n" \
                       "Dial the USSD code again to continue!🤗"

    resp = make_response(response, 200)
    resp.headers['Content-Type'] = "text/plain"
    return resp




if __name__ == "__main__":
    app.run(debug=True)
