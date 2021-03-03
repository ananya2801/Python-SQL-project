
## General Overview:
* Our program uses the functionality of SQL in python to build a user friendly system for obtaining and recording data
appropriately in required databases.
* Essentially, the system allows registered users to work on “posts” and perform several tasks on them through a
simple command line interface.
* The system’s initial page contains a login screen where existing users are able to sign in securely by providing their
username and password(which is non-visible at the time of typing). The system also effectively prevents any SQL
injection attacks. Non-existing users may register into the system where their user information is properly recorded.
* Users can perform tasks such as (1) asking a question , (2) searching for posts with certain keywords. On selected
posts they can further perform tasks such as voting on a post, answering a post.
* Certain users are considered to be privileged and have options to perform additional tasks such as adding a tag,
editing a post etc.
* After performing every task, the user is brought back to the options menu and has the opportunity to go back to the
login screen or exit the program all together.

## To test program
* Create a database in the same directory as the downloaded project.
* Create the appropriate tables in your SQL database by using "< prj-tables.sql"
* Populate the database by doing "< mini_proj_data.sql". This Data was prepared by Vincent Wainman, vwainman@ualberta.ca, published on 2020-09-28 and revised on 2020-10-06
* When you run the python program "project_code.py", provide the name of the database as the first and only command line argument.

## User Guide:
1. How to login to the database?
(i) If you are already a registered user, just type in “y” on the login screen and enter your user id and password securely.
(ii) If you are a new user, type in “n” on the login screen and enter a user id of your choice consisting of 4 characters followed by a password.

2. How do I post a new question?
Enter “1” when the options menu is displayed.

3. How do I search up posts with particular keywords?
Enter “2” when the options menu is displayed.

4. What can I do on a selected post?
You could either post an answer if the selected post is a question by entering “3” or vote on the post by entering “4” if you haven't already voted on the
same post earlier.

5. How do I exit the database?
Whenever given the option to, simply type “exit”.

6. How do I logout of the system?
Whenever given the option to, simply type “logout”.

7. How do I go back to the previous menu?
Whenever given the option to, simply type “back”.

Privileged User:
1. How do I mark an answer post as accepted?
Enter “5” when the options menu is displayed.

2. How do I give a badge to the user?
Enter “6” when the options menu is displayed. Keep in mind that you may only give badge names that already exist in the system.

3. How do I add a tag to the post? 
Enter “7” when the options menu is displayed. Keep in mind that you may only add a tag provided the post doesn’t have that tag already.

4. How do I edit the title/body of a post?
Enter “8” when the options menu is displayed. If you are not changing the title or body, press enter when prompted to type out the change.

## Detailed software design
LOGIN (implemented using login(), login_implementation() )
* Depending on whether the user is already registered in the database or not, they can either directly
sign in or sign up. If a user does not exist in the database or does not enter appropriate details
during registration, they are brought back to the login screen to attempt again or exit. New
registered user’s information is properly recorded in the database.

Q1) Posting questions: (implemented using question function)
* In this function we get the user to input a question title and a question body which we then insert
into the posts table and record the qid in the questions table.

Q2) Searching for Keywords: (implemented using q _search)
* The keywords entered are stored in a list. The program iterates through this list and stores the pid
of posts that have at least one keyword either in title, body, or tag fields.
* These pids are stored in a list which is then passed into the Counter function that orders by the
number of times each post occurs in the list. It then retrieves the AnsCnt and VoteCnt for each pid
along with the other rows in the posts table and outputs it.

Q3) Posting an Answer:(implemented using postans)
* Checks if the selected post is a question. If yes, it asks the user to input a title and body. Updates
posts and answer tables.

Q4) Voting on posts(implemented using vote function)
* Allows a user to vote on a post if the same user has not already voted on the same post, and
inserts it into the votes table.

Q5) Mark as accepted(implemented using markans(pid))
* This is a privileged user task which allows the user to mark an answer post as an accepted answer.
The program checks if the question post already has an accepted answer. If it does, it asks the
user if they would like to change the accepted answer. The questions table is then updated with
the accepted answer.

Q6) Give a Badge(implemented using givebadge(pid))
* This is a privileged user task which allows the user to give a badge to the poster by providing a
badge name, provided this badge name is in the badges table. The badge is then recorded in
Ubadges table.

Q7) Add a Tag (implemented using add_tag(pid) )
* This is a privileged user task which allows the user to add multiple tags to the selected post in Q2
provided that post does not already have the entered tag . If it does, the user is prompted to enter a
tag again. The tags are recorded in the tags table of the database.

Q8) Edit a Post (implemented using edit_post(pid) )
* This is a privileged user task which allows the user to edit the title or body of the selected post in
Q2 .
* Whatever they enter is properly updated in the posts table of the database. If they do not wish to
make changes, they must only press enter as indicated

**Flow of the program** : Login Screen leads to menu 1 with user tasks #1,#2. If task #2 is executed and a
post is selected only then menu 2 with tasks #3,#4 will be displayed. If the user is privileged, an
additional menu 3 with privileged user tasks will be shown. You can go back to previous screens.
