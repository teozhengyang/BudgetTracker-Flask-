# Budget Tracker
### Video Demo:
https://youtu.be/X6B2zrtEBzg
### Project Description:

**Project Idea**

As the project title implies, I decided to create a budget tracker web application to help users track their income and expenses hence net worth. The reason behind creating a web application for my final project is because I wish to create something functional that I myself can use. I decided to create a budget tracker. I tried out various budget trackers in the past but stopped using after a while as it was becoming a hassle. Some reasons behind this are that some trackers have complicated UIs while some have functions that come at a premium.

Therefore, with the knowledge I learnt from CS50x, I decided to create a budget tracker web application using Python, HTML, CSS and JavaScript. Also, since I did not have prior programming experience, I chose to adapt my project based on Week 9 Problem Set: Finance which explains the similarities between both applications. Moreover, since I did not collaborate with anyone on the project, it would be rather simple with a few functions. However, it is still effective.

**How does the project works**

I would now explain how does the budget tracker works. When the user accesses the tracker, he/she will be directed to the login page. If the user is here for the first time, he/she will need to register a new account with his/her email and a password of their choice under the 'Register' tab at the navigation bar. To enhance security, the password is required to contain at least one uppercase letter, one number, one special character and be at least 8 characters long. Upon successful registration, the user will be redirected back to the login page where he/she will log in with his/her new credentials. An email will be sent to the user to confirm his/her successful registration as well.

After logging in, the user will reach the homepage of the web application which will contain the user's net worth and goals information. Both sections will be empty initially and the user will have to add in relevant information to start using the tracker.

To add information, the user can access the relevant tabs in the navigation bar at the top of the page. The 'Add Transfer' will be the more confusing tab out of all of tabs in my opinion. This is added to allow users to transfer money between the various components of his/her net worth (budget, savings, investments) which may be useful for different users. At these pages, the users can have certain level of freedom in customising the information they wish to input into the tracker. For example, a 'description' input field was added if the user wishes to add more information about the transactions.

 After setting goals, the user has the ability to edit any part of their goals at the homepage which may be useful if the target amount is higher than expected after a while. To see his/her recent transactions, the users can access the 'History' tab. Here, the user can delete any transactions that were wrong or accidentally created and add the correct one in the relevant tabs if neccessary.

 For more information about how the tracker works, a simple 'More Information' page was created as well. The user can edit his/her password if hr/she wants to change it for security purposes. Here, the user will not be allowed to use any passwords he/she had used before. Upon a successful change, the user will receive an email confirming the change.

**Folders and Files**

In this project, the Flask framework was used to create the web application. Hence, common folders like static, templates and flask_session and files like app.py, helpers.py, project.db and requirements.txt are used in creating the budget tracker.

The 'static' folder contains a icon file which is downloaded from a royalty-free website which suits my application and also a CSS file which I used to customise all the various components of my application like the navigation bar, tables and input forms. I also created a logo for the budget tracker in the CSS file. The logo can be seen at the top left corner of all the pages in the application.

In the 'templates' folder, it contains all the HTML pages of the application like 'index.html' which represents the homepage and 'error.html' which notifies the user of any mistake that he/she has made while using the tracker eg inputting in wrong/missing information while submitting the form to add a transaction. A 'layout.html' was used to ensure the pages are consistent and contains the same necessary navigation bar and footer.

The flask_session contains the session information of a user every time he/she registers a new account and logs in. This allows the user to not log in every time he/she accesses the tracker which makes it more convenient for the user to use the tracker.

The app.py file contains the routes when user uses any function in the tracker. Few examples are the '/register', '/addincome', '/editgoals' and '/moreinfo/ routes. As what the name implies, the routes handle any requests sent to them. Apart from the '/register', '/moreinfo' and '/login' route, all the routes have the 'login_required' decorator which only allows users to access these routes once they are logged in. The helpers.py file contains all the functions that are used by the routes in app.py. For example the function that 'login_required' decorator used in app.py file can be found in helpers.py. Also, the functions to check whether the email and password used are validated can be found in this file. This file allows the app.py to be less messy in a sense that helpers.py will contain the functions used while app.py will contain the routes of the application.

The project.db database contains all the tables that are used in the tracker namely, 'oldpasswords', 'users', 'goals' and 'history'. All these tables contain relevant information of each user who use the tracker. For example the 'oldpasswords' table stores hashed versions of all the passwords each user had used before while 'users' stores each user's net worth and components. These tables will be queried for the relevant information when neccessary eg the 'users' table is accessed to display the user's net worth in the homepage. The requirements.txt contain the various libraries that are used in the application eg Flask-Mail and Flask-Sessionn.

**Design Choices**

I have many ideas of how the budget tracker should work and wish it will a be comprehensive yet easy to use tracker. However, I realised as soon as I started that it would be difficult and I need to remove functions that are not as important. One example will be the function of editing any transactions. This will mean that I need to display all the transactions in my application. However as the user uses it for hours, days and months, the number of transactions will increase to a point that it will take quite a while for the 'History' page to load. Hence, I decided to only show 12 of the most recent transactions and only allow the user to delete if he/she makes a mistake. Since a user is most likely to update information at the end of the day or week, this may be a better choice as well since the user will be less likely to make a mistake while inputting information.

Secondly, I ponder over showing more information like recent transactions together with the net worth and goals tables in the homepage. However, I found out that it would make the homepage contains too much information hence making it messy. Therefore, I chose to only display the user's net worth and goals in the homepage to make the page 'cleaner'.

Thirdly, I was in a dilemma whether a 'FAQ' page would be necessary for the application because the functions of the application are rather simple to understand and use. In the end, I decided to add a 'More Information' page that acts like a 'FAQ' page to guide the user if there are any issues and questions while the user is using the application. This would also hopefully be a good idea if I choose to continue to improve the tracker and add more functions.

Lastly, the 'Add Transfer' was added to cater to different users. I believe most users will allocate a portion of their income to savings and investments before moving all of it to their budget. However, I also note that there may be users who may only allocate what is left from their budget after a period of time eg a month to their savings or investments. This function is created to cater to such users.

**Future Improvements**

This is my first coding project and there is definitely rooms for improvements. I have already look at ways at improving the tracker and its functions after I submit this version of the tracker. I wish to build on this tracker until one day when I achieve the goal of creating a comprehensive budget tracker that is simple to use at the same time. Right now, I wish to add an investment tracker to the budget tracker which will display live changes to the user's investment portfolio and hence net worth. Also, a calculator app can be built into the tracker to allow simple calculations for the user. Therefore, I am considering all these changes if I choose to continue improving this project in the future.

**Conclusion**

I wish to express my appreciation to the teaching team here in this conclusion section. I chanced upon a recommendation on Reddit to enrol in CS50x online course before I start my university Computer Science course. As someone with no experience in programming, I feel that it would be beneficial if I have exposure to CS before my course officially starts and took the chance to enrol in the course. This is definitely one of the best choices I ever made as Professor David made various concepts easy to understand. I am finding computer science and coding more interesting thanks to the CS50 team and I am looking forward to starting my university CS course. All right, thanks to the CS50 team for guiding me to build my first web application! This is just a start and I want to continue to develop more web applications and softwares in the future!