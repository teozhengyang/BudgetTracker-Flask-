from cs50 import SQL
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, error, validate_email, validate_password

# Configure application as flask application
app = Flask(__name__)

# Configure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"]= "filesystem"
Session(app)

# configure sending messages to email addresses using Flask
app.config["MAIL_PORT"]=587
app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USERNAME"]="zybudgettracker@gmail.com"
app.config["MAIL_PASSWORD"]="TheAnswer3@"
mail = Mail(app)

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///project.db")

# Configure responses are not cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# login to web app
@app.route("/login", methods=["GET","POST"])
def login():
    # forget any user id
    session.clear()
    # when user submit email and password after registering new account
    if request.method == "POST":
        # access info submitted
        email = request.form.get("email")
        password = request.form.get("password")
        # check for blank username or password input
        if not email or not password:
            # return error function
            return error("Email and/or password should not be empty")
        # query 'users' table for email and password
        row = db.execute("SELECT id, email, hash FROM users WHERE email = ?", email)
        # check for correct email and password
        if len(row) != 1 or not check_password_hash(row[0]["hash"], password):
            # return error function
            return error("Invalid email and/or password")
        print(row[0])
        # remember which user is logged in
        session["user_id"] = row[0]['id']
        # return "/" route
        return redirect("/")
    # when user visit app for the first time (GET req)
    else:
        # return "login.html"
        return render_template("login.html")

# register account
@app.route("/register", methods=["GET","POST"])
def register():
    # when user submit username, password and confirmation of password to register (POST req)
    if request.method == "POST":
        # access info submitted via form
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # check for blank username, password, confirmation input
        if not email or not password or not confirmation:
            # return error function
            return error("Email and/or password should not be empty")
        # check for valid email
        if not validate_email(email):
            # return error function
            return error("Email format is wrong")
        # check that password and confirmation are the same
        if password != confirmation:
            # return error function
            return error("Passwords do not match")
        # check for valid password and confirmation
        if not validate_password(password):
            # return error function
            return error("Password should contain at least one capital letter, one number, one symbol and be at least 8 characters long")
        # hash password
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # add to "users" table
        db.execute("INSERT INTO users (email, hash) VALUES (?, ?)", email, hash_password)
        # send email to new users
        message = Message("Hello there!", sender="zybudgettracker@gmail.com", recipients=[email])
        message.body = "Welcome to ZY's budget tracker! Click on the 'More Information' to learn more or explore it on your own!"
        mail.send(message)
        # return "/login" route
        return redirect("/login")
    # when user click on 'Register' (GET req)
    else:
        # return "register.html"
        return render_template("register.html")

# index page (summary of net worth)
@app.route("/", methods=["GET"])
@login_required
def index():
    # query from 'users' table budget, savings, investments, net_worth
    old_user_info = db.execute("SELECT budget, savings, investments FROM users WHERE id = ?", session["user_id"])
    if not old_user_info[0]['budget']:
        old_user_info[0]['budget'] = 0
    if not old_user_info[0]['savings']:
        old_user_info[0]['savings'] = 0
    if not old_user_info[0]['investments']:
        old_user_info[0]['investments'] = 0
    net_worth = float(old_user_info[0]['budget']) + float(old_user_info[0]['savings']) + float(old_user_info[0]['investments'])
    # update new net worth
    db.execute("UPDATE users SET net_worth = ? WHERE id = ?", net_worth, session["user_id"])
    user_info = db.execute("SELECT budget, savings, investments, net_worth FROM users WHERE id = ?", session["user_id"])
    # percentage of budget, savings and investments as net worth
    budget = float(user_info[0]["budget"])
    savings = float(user_info[0]["savings"])
    investments = float(user_info[0]["investments"])
    net_worth = float(user_info[0]["net_worth"])
    if net_worth != 0:
        if savings == 0:
            savingspercent = 0
        else:
            savingspercent = round(((savings/net_worth) * 100), 2)
        if investments == 0:
            investmentspercent = 0
        else:
            investmentspercent = round(((investments/net_worth) * 100), 2)
        if budget == 0:
            budgetpercent = 0
        else:
            budgetpercent = round(((budget/net_worth) * 100), 2)
    # when user has not input any net worth value
    else:
        savingspercent = 0
        investmentspercent = 0
        budgetpercent = 0
    # query from 'goals' table old goals info
    old_goals = db.execute("SELECT amount, description, amount_left, current_progress, remaining_progress, completed_goal, id FROM goals WHERE user_id = ?", session["user_id"])
    for goal in old_goals:
        # calculate how far user is away from achieving goal
        target = float(goal['amount'])
        remaining = float(goal['amount_left'])
        current_worth = budget + savings
        current_progress_percent = round(((current_worth) / (target + remaining) * 100), 2)
        # for goals not achieved
        if current_progress_percent < 100:
            remaining_progress_amount = round(float(target + remaining - current_worth), 2)
            db.execute("UPDATE goals SET current_progress = ?, remaining_progress = ?, completed_goal = NULL WHERE user_id = ? AND id = ?", current_progress_percent, remaining_progress_amount, session["user_id"], goal['id'])
        # for goals achieved
        else:
            db.execute("UPDATE goals SET current_progress = '100', remaining_progress = '0', completed_goal = 'Goal achieved' WHERE user_id = ? AND id = ?", session["user_id"], goal['id'])
    # query from 'goals' table updated goals info
    goals = db.execute("SELECT id, amount, description, amount_left, current_progress, remaining_progress, completed_goal,date FROM goals WHERE user_id = ? ORDER BY date DESC", session["user_id"])
    # return "index.html"
    return render_template("index.html", user_info=user_info, goals=goals, history=history, savingspercent=savingspercent, investmentspercent=investmentspercent, budgetpercent=budgetpercent)

# set budgeting goals
@app.route("/setgoal", methods=["POST","GET"])
@login_required
def set_goals():
    # when user submit budget goals
    if request.method == "POST":
        # access form info
        amount = request.form.get("amount")
        description = request.form.get("description")
        amount_left = request.form.get("amount_left")
        # check for blank input of description, amount, amount_left inputs
        if not description or not amount or not amount_left:
            # return error function
            return error("Please provide more information about your goal!")
        amount = round(float(amount), 2)
        amount_left = round(float(amount_left), 2)
        # add to 'goals' table
        db.execute("INSERT INTO goals (user_id, amount, description, amount_left) VALUES (?, ?, ?, ?)", session["user_id"], amount, description, amount_left)
        # return "/" route
        return redirect("/")
    # when user click on "Set Goals" (GET req)
    else:
        # return "setgoals.html
        return render_template("setgoal.html")

# delete or achieved goal
@app.route("/deletegoal", methods=["GET"])
@login_required
def delete_goal():
    # access goal info
    goal_id = request.args.get("id")
    # delete from 'goals' table
    db.execute("DELETE FROM goals WHERE id = ?", goal_id)
    # return "/" route
    return redirect("/")

# edit goal
@app.route("/editgoal", methods=["POST","GET"])
@login_required
def edit_goal():
    # when user submit updated info
    if request.method == "POST":
        update_id = request.form.get("id")
        update_amount = request.form.get("amount")
        update_amount_left = request.form.get("amount_left")
        update_description = request.form.get("description")
        if not update_amount or not update_amount_left:
            return error("Please provide more information about your goal!")
        db.execute("UPDATE goals SET amount = ?, amount_left = ?, description = ? WHERE id = ?", update_amount, update_amount_left, update_description, update_id )
        return redirect("/")
    # when user press 'edit' button
    if request.method == "GET":
        goal_id = request.args.get("id")
        goal = db.execute("SELECT amount, description, amount_left, id FROM goals WHERE id = ?", goal_id)
        return render_template("editgoal.html", goal=goal)


# add net worth components
@app.route("/addincome", methods=["POST","GET"])
@login_required
def add_income():
    # add net worth form submitted
    if request.method == "POST":
        # access form info
        source = request.form.get("source")
        destination = request.form.get("destination")
        description = request.form.get("description")
        amount = request.form.get("amount")
        transaction_type = 'Income'
        # check for blank source, destination, description, amount inputs
        if not source or not destination or not description or not amount:
            return error("Please input more information about the transaction!")
        # destination is savings
        if destination == 'Savings':
            # query 'users' table for original savings and net worth
            user_info1 = db.execute("SELECT savings, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new savings and net worth
            new_savings = round(float(user_info1[0]['savings']) + float(amount), 2)
            new_net_worth1 = round(float(user_info1[0]['net_worth']) + float(amount), 2)
            # update 'users' table new savings and net worth
            db.execute("UPDATE users SET savings = ?, net_worth = ? WHERE id = ?", new_savings, new_net_worth1, session["user_id"])
        # destination is budget
        elif destination == 'Budget':
            # query 'users' table for original budget and net worth
            user_info2 = db.execute("SELECT budget, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and net worth
            new_budget = round(float(user_info2[0]['budget']) + float(amount), 2)
            new_net_worth2 = round(float(user_info2[0]['net_worth']) + float(amount), 2)
            # update 'users' table new budget and net worth
            db.execute("UPDATE users SET budget = ?, net_worth = ? WHERE id = ?", new_budget, new_net_worth2, session["user_id"])
        # destination is investments
        elif destination == 'Investments':
            # query 'users' table for original investments and net worth
            user_info3 = db.execute("SELECT investments, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new investments and net worth
            new_investments = round(float(user_info3[0]['investments']) + float(amount), 2)
            new_net_worth3 = round(float(user_info3[0]['net_worth']) + float(amount), 2)
            # update 'users' table new investments and net worth
            db.execute("UPDATE users SET investments = ?, net_worth = ? WHERE id = ?", new_investments, new_net_worth3, session["user_id"])
        # insert into 'history' table
        amount = round(float(amount), 2)
        db.execute("INSERT INTO history(user_id, source, destination, description, amount, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], source, destination, description, amount, transaction_type)
        # return "/" route
        return redirect("/")
    # when user click on "Add Net Worth"
    else:
        # return "addnetworth.html"
        return render_template("addincome.html")

# transfer between net worth components
@app.route("/addtransfer", methods=["POST", "GET"])
@login_required
def add_transfer():
    # transfer within net worth form submitted
    if request.method == "POST":
        # access form info
        source = request.form.get("source")
        destination = request.form.get("destination")
        description = request.form.get("description")
        amount = request.form.get("amount")
        transaction_type = 'Transfer'
        # check for blank source, destination, description, amount inputs
        if not source or not destination or not description or not amount:
            return error("Please input more information about the transaction!")
        # source is budget
        if source == 'source_Budget':
            # destination is budget
            if destination == 'Budget':
                return error("Source and destination should be different!")
            # destination is savings
            elif destination == 'Savings':
                # query 'users' table for current budget and savings
                old_user_info1 = db.execute("SELECT budget, savings FROM users WHERE id = ?", session["user_id"])
                # calculate new budget and savings
                new_budget1 = round(float(old_user_info1[0]["budget"]) - float(amount), 2)
                new_savings1 = round(float(old_user_info1[0]["savings"]) + float(amount), 2)
                # update 'users' table new budget and savings
                db.execute("UPDATE users SET budget = ?, savings = ? WHERE id = ?", new_budget1, new_savings1, session["user_id"])
            # destination is investments
            elif destination == 'Investments':
                # query 'users' table for current budget and investments
                old_user_info2 = db.execute("SELECT budget, investments FROM users WHERE id = ?", session["user_id"])
                # calculate new budget and savings
                new_budget2 = round(float(old_user_info2[0]["budget"]) - float(amount), 2)
                new_investments2 = round(float(old_user_info2[0]["investments"]) + float(amount), 2)
                # update 'users' table new budget and savings
                db.execute("UPDATE users SET budget = ?, investments = ? WHERE id = ?", new_budget2, new_investments2, session["user_id"])
            transaction_source = "Budget"
            # insert history table
            amount = round(float(amount), 2)
            db.execute("INSERT INTO history(user_id, source, destination, description, amount, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], transaction_source, destination, description, amount, transaction_type)
        # source is savings
        elif source == 'source_Savings':
            # destination is savings
            if destination == 'Savings':
                return error("Source and destination should be different!")
            # destination is budget
            elif destination == 'Budget':
                # query 'users' table for current savings and budget
                old_user_info3 = db.execute("SELECT budget, savings FROM users WHERE id = ?", session["user_id"])
                # calculate new savings and budget
                new_budget3 = round(float(old_user_info3[0]["budget"]) + float(amount), 2)
                new_savings3 = round(float(old_user_info3[0]["savings"]) - float(amount), 2)
                # update 'users' table new savings and budget
                db.execute("UPDATE users SET budget = ?, savings = ? WHERE id = ?", new_budget3, new_savings3, session["user_id"])
            # destination is investments
            elif destination == 'Investments':
                # query 'users' table for current savings and investments
                old_user_info4 = db.execute("SELECT savings, investments FROM users WHERE id = ?", session["user_id"])
                # calculate new budget and savings
                new_savings4 = round(float(old_user_info4[0]["savings"]) - float(amount), 2)
                new_investments4 = round(float(old_user_info4[0]["investments"]) + float(amount), 2)
                # update 'users' table new budget and savings
                db.execute("UPDATE users SET savings = ?, investments = ? WHERE id = ?", new_savings4, new_investments4, session["user_id"])
            transaction_source = "Savings"
            # insert history table
            amount = round(float(amount), 2)
            db.execute("INSERT INTO history(user_id, source, destination, description, amount, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], transaction_source, destination, description, amount, transaction_type)
        # source is investments
        elif source == 'source_Investments':
            # destination is investments
            if destination == 'Investments':
                return error("Source and destination should be different!")
            # destination is budget
            elif destination == 'Budget':
                # query 'users' table for current investments and budget
                old_user_info5 = db.execute("SELECT budget, investments FROM users WHERE id = ?", session["user_id"])
                # calculate new investments and budget
                new_budget5 = round(float(old_user_info5[0]["budget"]) + float(amount), 2)
                new_investments5 = round(float(old_user_info5[0]["investments"]) - float(amount), 2)
                # update 'users' table new investments and budget
                db.execute("UPDATE users SET budget = ?, investments = ? WHERE id = ?", new_budget5, new_investments5, session["user_id"])
            # destination is savings
            elif destination == 'Savings':
                # query 'users' table for current savings and investments
                old_user_info6 = db.execute("SELECT savings, investments FROM users WHERE id = ?", session["user_id"])
                # calculate new budget and savings
                new_savings6 = round(float(old_user_info6[0]["savings"]) + float(amount), 2)
                new_investments6 = round(float(old_user_info6[0]["investments"]) - float(amount), 2)
                # update 'users' table new budget and savings
                db.execute("UPDATE users SET savings = ?, investments = ? WHERE id = ?", new_savings6, new_investments6, session["user_id"])
            transaction_source = "Savings"
            # insert history table
            amount = round(float(amount), 2)
            db.execute("INSERT INTO history(user_id, source, destination, description, amount, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], transaction_source, destination, description, amount, transaction_type)
        # return ("/") route
        return redirect("/")
    # user click on 'Transfer Within Net Worth'
    else:
        # return "transferwithinnetworth.html"
        return render_template("addtransfer.html")

# add expenses
@app.route("/addexpense", methods=["POST","GET"])
@login_required
def add_expense():
    # when user submit expenses
    if request.method == "POST":
        # access form info
        source = request.form.get("source")
        destination = request.form.get("destination")
        description = request.form.get("description")
        amount = request.form.get("amount")
        transaction_type = 'Expense'
        # check for blank source, description, amount inputs
        if not source or not description or not amount or not destination:
            return error("Please input more information about the transaction!")
        # source is savings
        if source == 'Savings':
            # query 'users' table for original savings
            user_info1 = db.execute("SELECT savings, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new savings and net worth
            new_savings1 = round(float(user_info1[0]['savings']) - float(amount), 2)
            new_net_worth1 = round(float(user_info1[0]['net_worth']) - float(amount), 2)
            # update 'users' table new savings and net worth
            db.execute("UPDATE users SET savings = ?, net_worth = ? WHERE id = ?", new_savings1, new_net_worth1, session["user_id"])
        # source is budget
        elif source == 'Budget':
            # query 'users' table for original budget and net worth
            user_info2 = db.execute("SELECT budget, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new budget
            new_budget2 = round(float(user_info2[0]['budget']) - float(amount), 2)
            new_net_worth2 = round(float(user_info2[0]['net_worth']) - float(amount), 2)
            # update 'users' table new budget and net worth
            db.execute("UPDATE users SET budget = ?, net_worth = ? WHERE id = ?", new_budget2, new_net_worth2, session["user_id"])
        # insert into 'history' table
        amount = round(float(amount), 2)
        db.execute("INSERT INTO history(user_id, source, destination, description, amount, type) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], source, destination, description, amount, transaction_type)
        # return "/" route
        return redirect("/")
    # when user click on 'Add Expense"
    else:
        # return "addexpenses.html"
        return render_template("addexpense.html")

# check history of cash added, expenses, savings, investments
@app.route("/history", methods=["GET"])
@login_required
def history():
    # query 'history' table
    history = db.execute("SELECT id, source, destination, description, amount, date, type FROM history WHERE user_id = ? ORDER BY date DESC LIMIT 12", session["user_id"])
    # return "history.html"
    return render_template("history.html", history=history)

# delete any history added before
@app.route("/deletehistory", methods=["POST"])
@login_required
def delete_history():
    # access form info
    transaction_id = request.form.get("id")
    transaction_source = request.form.get("source")
    transaction_destination = request.form.get("destination")
    transaction_description = request.form.get("description")
    transaction_amount = float(request.form.get("amount"))
    # sources are salary, investments dividends, others (revert /addnetworth)
    if transaction_source == 'Salary' or transaction_source == 'Dividends' or transaction_source == 'Others' or transaction_source == "Interest":
        # destination is budget
        if transaction_destination == 'Budget':
            # query 'users' table for original budget and net worth
            user_info1 = db.execute("SELECT budget, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and net worth
            new_budget1 = round(float(user_info1[0]['budget']) - transaction_amount, 2)
            new_net_worth1 = round(float(user_info1[0]['net_worth']) - transaction_amount, 2)
            # update 'users' table new budget and net worth
            db.execute("UPDATE users SET budget = ?, net_worth = ? WHERE id = ?", new_budget1, new_net_worth1, session["user_id"])
        # destination is savings
        elif transaction_destination == 'Savings':
            # query 'users' table for original savings and net worth
            user_info2 = db.execute("SELECT savings, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new savings and net worth
            new_savings2 = round(float(user_info2[0]['savings']) - transaction_amount, 2)
            new_net_worth2 = round(float(user_info2[0]['net_worth']) - transaction_amount, 2)
            # update 'users' table new savings and net worth
            db.execute("UPDATE users SET savings = ?, net_worth = ? WHERE id = ?", new_savings2, new_net_worth2, session["user_id"])
        # destination is investments
        elif transaction_destination == 'Investments':
            # query 'users' table for original investments and net worth
            user_info3 = db.execute("SELECT investments, net_worth FROM users WHERE id = ?", session["user_id"])
            # calculate new investments and net worth
            new_investments3 = round(float(user_info3[0]['investments']) - transaction_amount, 2)
            new_net_worth3 = round(float(user_info3[0]['net_worth']) - transaction_amount, 2)
            # update 'users' table new investments and net worth
            db.execute("UPDATE users SET investments = ?, net_worth = ? WHERE id = ?", new_investments3, new_net_worth3, session["user_id"])
    # source is budget (revert /transferwithinnetworth or /addexpense)
    elif transaction_source == 'Budget':
        # destination is savings
        if transaction_destination == 'Savings':
            # query 'users' table for original budget and savings
            user_info4 = db.execute("SELECT budget, savings FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and savings
            new_budget4 = round(float(user_info4[0]['budget']) + transaction_amount, 2)
            new_savings4 = round(float(user_info4[0]['savings']) - transaction_amount, 2)
            # update 'users' table new budget and savings
            db.execute("UPDATE users SET budget = ?, savings = ? WHERE id = ?", new_budget4, new_savings4, session["user_id"])
        # destination is investments
        elif transaction_destination == 'Investments':
            # query 'users' table for original budget and investments
            user_info5 = db.execute("SELECT budget, investments FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and investments
            new_budget5 = round(float(user_info5[0]['budget']) + transaction_amount, 2)
            new_investments5 = round(float(user_info5[0]['investments']) - transaction_amount, 2)
            # update 'users' table new budget and investments
            db.execute("UPDATE users SET budget = ?, investments = ? WHERE id = ?", new_budget5, new_investments5, session["user_id"])
        # destination is expense
        elif transaction_destination == 'Expense':
            # query 'users' table for original budget
            user_info6 = db.execute("SELECT budget FROM users WHERE id = ?", session["user_id"])
            # calculate new budget
            new_budget6 = round(float(user_info6[0]['budget']) + transaction_amount, 2)
            # update 'users' table new budget
            db.execute("UPDATE users SET budget = ? WHERE id = ?", new_budget6, session["user_id"])
    # source is savings (revert /transferwithinnetworth or /addexpense)
    elif transaction_source == 'Savings':
        # destination is budget
        if transaction_destination == 'Budget':
            # query 'users' table for original budget and savings
            user_info7 = db.execute("SELECT budget, savings FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and savings
            new_budget7 = round(float(user_info7[0]['budget']) - transaction_amount, 2)
            new_savings7 = round(float(user_info7[0]['savings']) + transaction_amount, 2)
            # update 'users' table new budget and savings
            db.execute("UPDATE users SET budget = ?, savings = ? WHERE id = ?", new_budget7, new_savings7, session["user_id"])
        # destination is investments
        elif transaction_destination == 'Investments':
            # query 'users' table for original savings and investments
            user_info8 = db.execute("SELECT savings, investments FROM users WHERE id = ?", session["user_id"])
            # calculate new savings and investments
            new_savings8 = round(float(user_info8[0]['savings']) + transaction_amount, 2)
            new_investments8 = round(float(user_info8[0]['investments']) - transaction_amount, 2)
            # update 'users' table new savings and investments
            db.execute("UPDATE users SET savings = ?, investments = ? WHERE id = ?", new_savings8, new_investments8, session["user_id"])
        # destination is expense
        elif transaction_destination == 'Expense':
            # query 'users' table for original savings
            user_info9 = db.execute("SELECT savings FROM users WHERE id = ?", session["user_id"])
            # calculate new savings
            new_savings9 = round(float(user_info9[0]['savings']) + transaction_amount, 2)
            # update 'users' table new savings
            db.execute("UPDATE users SET savings = ? WHERE id = ?", new_savings9, session["user_id"])
    # source is investments (revert /transferwithinnetworth)
    elif transaction_source == 'Investments':
        # destination is budget
        if transaction_destination == 'Budget':
            # query 'users' table for original budget and investments
            user_info10 = db.execute("SELECT budget, investments FROM users WHERE id = ?", session["user_id"])
            # calculate new budget and investments
            new_budget10 = round(float(user_info10[0]['budget']) - transaction_amount, 2)
            new_investments10 = round(float(user_info10[0]['investments']) + transaction_amount, 2)
            # update 'users' table new budget and investments
            db.execute("UPDATE users SET budget = ?, investments = ? WHERE id = ?", new_budget10, new_investments10, session["user_id"])
        # destination is savings
        elif transaction_destination == 'Savings':
            # query 'users' table for original savings and investments
            user_info11 = db.execute("SELECT savings, investments FROM users WHERE id = ?", session["user_id"])
            # calculate new savings and investments
            new_savings11 = round(float(user_info11[0]['savings']) - transaction_amount, 2)
            new_investments11 = round(float(user_info11[0]['investments']) + transaction_amount, 2)
            # update 'users' table new savings and investments
            db.execute("UPDATE users SET savings = ?, investments = ? WHERE id = ?", new_savings11, new_investments11, session["user_id"])
    # delete from 'history' table
    db.execute("DELETE FROM history WHERE id = ?", transaction_id)
    # return "/history" route
    return redirect("/history")

# edit profile
@app.route("/editprofile", methods=["POST", "GET"])
@login_required
def edit_profile():
    if request.method == "POST":
        # access form info
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # check for blank password, confirmation input
        if not password or not confirmation:
            # return error function
            return error("Passwords should not be empty")
        # check that password and confirmation are the same
        if password != confirmation:
            # return error function
            return error("Passwords do not match")
        # check for valid password and confirmation
        if not validate_password(password):
            # return error function
            return error("Password should contain at least one capital letter, one number, one symbol and be at least 8 characters long")
        # query from 'users' table for current password
        current_password = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        # add to 'oldpasswords' table
        db.execute("INSERT INTO oldpasswords(old_password, user_id) VALUES(?, ?)", current_password[0]['hash'], session["user_id"])
        # query all passwords used before from 'oldpasswords' table
        used_passwords = db.execute("SELECT old_password FROM oldpasswords WHERE user_id = ?", session["user_id"])
        # check for matching passwords
        for used_password in used_passwords:
            if check_password_hash(used_password['old_password'], password):
                # return error function
                return error("Cannot use previous passwords")
        # hash new password
        new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # update "users" table
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_password, session["user_id"])
        # query from 'users' table email
        email = db.execute("SELECT email FROM users WHERE id = ?", session["user_id"])
        # send email to users informing them about changing password
        message = Message("Important Information About Profile", sender="zybudgettracker@gmail.com", recipients=[email[0]['email']])
        message.body = "Your password has been changed recently. Please ensure that you are the one who changed the password. If not, please contact us as soon as possible through this email!"
        mail.send(message)
        return redirect("/")
        # user click on 'Edit Profile'
    else:
        # return 'editprofile.html'
        return render_template("editprofile.html")

# find out more
@app.route("/moreinfo", methods=["GET"])
def moreinfo():
    return render_template("moreinfo.html")

# log out of web app
@app.route("/logout", methods=["GET"])
def logout():
    # forget any user id
    session.clear()
    # return "login.html"
    return redirect("/")