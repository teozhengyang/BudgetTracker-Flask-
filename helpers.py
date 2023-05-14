import re

from functools import wraps
from flask import redirect, session, render_template

# ensure user is logged in when accessing routes using decorator from https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# error message for any 'incorrect' input
def error(bottom):
    # function to escape special characters using memegen#special-characters
    def escape(text):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            text = text.replace(old, new)
        return text
    # return "apology.html"
    top = "Please Try Again"
    return render_template("error.html", top=escape(top), bottom=escape(bottom))

# validate email
def validate_email(address):
    # email requirements
    reg = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    # create pattern based on requirements
    pattern = re.compile(reg)
    # compare between user input email and pattern
    match = re.search(pattern, address)
    if match:
        return True
    return False

# validate password
def validate_password(pw):
    # password requirements (contain at least one capital letter, one number, one symbol and at least 8 characters long)
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[a-zA-Z\d!@#$%^&*]{8,}$"
    # create patttern based on requirements
    pattern = re.compile(reg)
    # compare between user input password and pattern
    match = re.search(pattern, pw)
    if match:
        return True
    return False
