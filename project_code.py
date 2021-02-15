#souce code
#authors : aprao,farook,dhavalma

import sqlite3
from datetime import date
import getpass
import collections
import sys

c = None
conn = None
uid = None

#to check if user is privileged or not
def isprev():
    c.execute('''select * from privileged where uid = ?''',(uid,))
    rows = c.fetchone()
    if rows:
        return True
    else:
        return False
      
#helper function for q2 to select a post to work on
def pidchoice(flist):
    if flist:
        while True:
            try:
                while True:
                    choice = int(input("Select Post No. (1/2/3...): "))
                    if choice > (len(flist)-1) or choice < 1:
                        print("Selected post not in range.")
                        continue
                    elif flist[-1] == 'n' and choice > 5:
                        print("Selected post not in range.")
                        continue
                    break
                break
            except:
                pass
            print("please enter an integer")
        pid = flist[choice-1][0]#*
    return pid
  
#counting number of posts already there
def pidcount():
    c.execute('''select count(pid) from posts''')
    countt = (c.fetchone())
    pidcnt = int(countt[0])
    return pidcnt

#to generate a new uniquepid
def newpid(pidcnt):
    c.execute("select * from posts where pid = ?",(pidcnt,))
    p = c.fetchall()
    if p:
        pidcnt = pidcnt + 1
        pidcnt = newpid(pidcnt) #recursion
        return pidcnt
    return pidcnt

#post action: give a badge to user
def givebadge(pid):
    give = input("Would you like to give a badge to the poster? y/n: ")
    give.lower()
    if give == 'y':
        c.execute("select * from badges")
        
        names = c.fetchall()
        for i in range(0,len(names)):
            print(names[i][0])
        
        valid = 'n'
        while valid == 'n':
            name = input("Please enter a badge name from above: ")
            c.execute('''select bname from badges where bname = ?''',(name,))
            badge = c.fetchone()
            if badge == None:
                print("badge name is not valid")
            else:
                print("badge name is valid")
                valid = 'y'
        c.execute('''select poster from posts where pid = ?''',(pid,))
        poster = list(c.fetchone())[0]
        today = date.today()
        c.execute("select * from ubadges where uid  = ? and bdate = ?",(poster,today))
        r = c.fetchall()
        if r:
            print("You cannot give a badge to the same user on the same day.")
            return
        ubadge = [(poster,today,name)]
        c.executemany('''insert into ubadges values(?,?,?)''',ubadge)
        conn.commit()
        printLine()
        print("Badge inserted")

#post action: mark as accepted answer
def markans(pid):
    #pid=the post id
    #Qid=the question the post is answering
    #theaid = previous accepted answer
    
    # check if pid in ans
        c. execute('''select pid from answers where pid = ?''',(pid,))
        rows = c.fetchone()
        
        if rows:
            markp = input("Would you like to mark this post as the accepted answer? y/n: ")
            markp.lower()
            if markp == 'y':
                c.execute('''select qid from answers where pid = ?''',(pid,))
                Qid = list(c.fetchone())[0]
                
                c.execute('''select theaid from questions where pid = ?''',(Qid,))
                theaid = list(c.fetchone())[0]
                
                if theaid: #see if it already has an accepted ans
                    change = input("Question already has an accepted answer, would you like to change the accepted answer? y/n: ")
                    change.lower()
                    if change == 'y':
                        c.execute('''update questions set theaid = ? where pid = ?''',(pid,Qid))
                        printLine()
                        print("Answer has been updated")
                else:
                    c.execute('''update questions set theaid = ? where pid = ?''',(pid,Qid))
                    printLine()
                    print("Answer has been marked.")
        else:
            print("This is not an answer post, it can't be marked.")
        conn.commit()

#post action: post an answer
def postans(pid,pidcnt):
    
    c.execute('''select pid from questions where pid = ?''',(pid,)) #accesing the picked post
   
    qselect = c.fetchall()
   
    
    if qselect: #checks if list is not empty/checks if post is a question
        choice = input("Would you like to answer this question y/n : ")
        choice.lower()
        if choice == 'y':
            title = input("Enter Title: ")
            body = input("Enter Answer: ")
            today = date.today()
            pidcnt+=1
            ansid = newpid(pidcnt)
            theans=[(ansid,today,title,body,uid)]
            c.executemany("insert into posts values(?,?,?,?,?);",theans)
            printTable("posts")
            theans = [(ansid,pid)]
            c.executemany("insert into answers values(?,?);",theans)
            
    else:
        print("You can't answer this post because selected post is already an answer. ")
    conn.commit()

#helper function to check if user input is exit or logout
def check_exit_login(inp):
    if(inp.lower() == "exit"):
        conn.commit()
        print("Exiting..")
        exit()
    if(inp.lower() == "logout"):
        return "login_again"

# search for a post by providing keywords
def qsearch():
    answer = ''
    while True:
        try: 
            n=int(input("How many Keywords would you like to enter? "))
            if n<1:
                print("Please enter a number greater than 0.")
                continue
            break
        except:
            pass
        print("Please enter an integer within the range.")
        
    keywords = []
    while n!=0:
        keywords.append(input("Enter Keyword: "))
        n = n-1
    biglist = []
    for key in keywords:
        c.execute('''select p.pid
                  from posts p
                  where p.title like ? COLLATE NOCASE
                  union
                  select p.pid
                  from posts p
                  where body like ? COLLATE NOCASE
                  union
                  select pid
                  from tags t
                  where tag like ? COLLATE NOCASE
                  ''',('%'+key+'%','%'+key+'%','%'+key+'%'))
        rows = c.fetchall()
        #only adds to biglist if the keyword returns results
        if rows:
            for row in rows:
                biglist.append(row[0])
        
    if not biglist:
        printLine()
        print("The search did not retrieve any matching posts, please try again")
        return 
    #number of time each post apprears in a list
    dict1 = collections.Counter(biglist)
    ordered_list = list(dict1.keys())
   
    rows1 = []  #contains final ordered list
    for pid in ordered_list:
        c.execute('''select id,date,title,body,user,vcnt,coalesce(ansCnt,0)
                from (
                (select pid as id,pdate as date,title as title,body as body,poster as user from posts where pid = ?) A
                left outer join
                (select qid as qnum,count(pid) as ansCnt from answers
                 group by qid) B
                 on A.id = B.qnum
                 left outer join 
                 (select v.pid as pid,count(v.vno) as vcnt from votes v
                  group by v.pid) C
                  on A.id = C.pid)''',(pid,))
        a = c.fetchone()
        rows1.append(a)
        
    #number of matches displayed
    i = 0
    while i<5 and i<len(rows1):
        print(str(i+1)+' - ',end='') 
        print(rows1[i])
        i=i+1
    answer = input("Would you like to see more matches? y/n ")
    answer.lower()
    if answer == 'y':
        i=0
        while i<len(rows1):
            print('('+str(i+1)+')',end='')
            print(rows1[i])
            i = i + 1
    
    
    rows1.append(answer)
    return rows1

#prints a line for readibility
def printLine():
    print('-'* 70)


#login implementation
def login_implementation():
    printLine()
    print('LOGIN')
    global uid
    

    registered = input('Are you a registered user? Y/N\n')
    if registered.lower() == 'y':
        printLine()
        uid = input("enter user id\n")
        password = getpass.getpass("enter password")
       
        c.execute("select uid from users where uid = ? COLLATE NOCASE and pwd = ?;",(uid,password))
        user = c.fetchone()
        
        
        
        if user == None:
            print("User does not exist.")
            choice = input('''Type "exit" to leave program, enter anything else to try again : ''')
            check_exit_login(choice)
            return "login_again"
        
        else:
            uid = user[0]
            printLine()
            print("Welcome!", uid)
            
        
    elif registered.lower() == 'n':
        printLine()
        print("REGISTRATION")
        
        valid = False

        while(not valid):
            uid = input("Enter a unique ID of 4 characters: ")
            c.execute("select uid from users where uid = ? COLLATE NOCASE;",(uid,))
            check_uid = c.fetchone()
            if uid.lower() == "exit":
                printLine()
                print("Exiting..")
                exit()
            elif not uid.isalnum():
                print("Username can only contain alphanumeric characters. Try again. ")
            elif uid.lower() == "login":
                return "login_again"
            elif len(uid) != 4 :
                print('''Sorry uid not valid, Enter again. OR Enter "exit" to exit program, "login" to go back to login screen.''') 
            elif (check_uid != None):
                print('''User ID already exists try again. Enter again. OR Enter "exit" to exit program, "login" to go back to login screen.''')
            else:
                valid = True
            
        
        name = input("Enter your name: ")
        city = input("Enter your city: ")
        password = getpass.getpass("Enter a password: ")
        if not password.isalnum():
            print("Password can only contain alphanumeric characters. Try again. ")
            return "login_again"
        today = date.today()
        insertion = [(uid,name,password,city,today)]
        c.executemany("insert into users values(?,?,?,?,?);",insertion)
        conn.commit()
        #conn.commit()
    else:
        print("Enter again")
        return "login_again"

#post action : voting on a post
def vote(pid):
    
    vno = 0
    c.execute('SELECT * FROM votes WHERE pid=? and uid=?', (pid, uid))
    a = c.fetchall()

    if not a:
        c.execute('SELECT count(*) FROM votes WHERE pid=? GROUP BY pid=?', (pid, pid))
       
        votecount = c.fetchone()
        if not votecount:
           vno = 1
           today = date.today()
           insertion = [(pid,vno,today,uid)]
           c.executemany("insert into votes values(?,?,?,?);",insertion)
        else:
           vno = int((votecount)[0]) + 1
           today = date.today()
           insertion = [(pid,vno,today,uid)]
           c.executemany("insert into votes values(?,?,?,?);",insertion)
		
        conn.commit()
        print("Your vote has been recorded.")
           
    else:
        print("You have already voted on this post.")

#getting logged in user to input question title and body
def question(pidcnt):
    q_title = input("Enter a question title: ")
    q_body = input("Enter the question body: ")
    today = date.today()
    #inserting question into posts table
    
    pidcnt= pidcnt + 1
    pid = newpid(pidcnt)
    insertion = [(pid,today,q_title,q_body,uid)]
    c.executemany("insert into posts values(?,?,?,?,?);",insertion)
    insertion2 = [(pid,None)]
    c.executemany("insert into questions values(?,?);",insertion2)
    conn.commit()
    printLine()
    print("Question recorded")

#post action : editing a post's body or title
def edit_post(pid):
    new_title = input("Enter new title of the post, Please press enter if you do not want to change it.: ")
    new_body = input("Enter new body of the post, Please press enter if you do not want to change it.: ")
    if (new_title != ""):
        c.execute("UPDATE posts set title = ? where pid = ?;",(new_title,pid))
    if (new_body != ""):
        c.execute("UPDATE posts set body = ? where pid = ?;",(new_body,pid))
    printLine()
    print("Any required edits have been made.")
    conn.commit()

#post action : adding a tag
def add_tag(pid):
    no_tags = int(input("How many tags would you like to add to this post? "))
    while(no_tags!= 0):
        tag = input("Enter tag ")
        c.execute("select pid,tag from tags where pid = ? and tag like ? COLLATE NOCASE;",(pid,tag))
        row = c.fetchone()
        #checking if post already has that tag
        if row != None:
            print("This post already has that tag, enter a new one.")
            continue

        c.execute("insert into tags values (?,?);",(pid,tag))
        printLine()
        print("Your tag has been entered.")
        no_tags = no_tags - 1
        conn.commit()

#login
def login():
    valid = login_implementation()
    while(valid == "login_again"):         
        valid = login_implementation()
    printLine()


def main():
    
    global conn,c,uid
    conn = sqlite3.connect(sys.argv[1])
    c = conn.cursor()
    
    continue_program = True

    #implementation of the menu which keeps getting displayed until the user exits program
    while continue_program:
        login()
        printLine()
        continue_program = False
        
        while True:
            print("User currently logged on to the system is", uid)
            printLine()
            print('''Choose from the following options (1/2) Type "exit" to leave program, "logout" to go back to login screen''')
            print("1. Post a Question.")
            print("2. Search for post by providing keyword(s) and select a post to work on.\n")
            printLine()
            choice = input()
            
            
            pidcnt = pidcount()

            if check_exit_login(choice) == "login_again":
                continue_program = True
                break
            elif choice == '1':
                question(pidcnt)
            elif choice == '2':
                flist = qsearch()
                if flist:
                    pid = pidchoice(flist)

                    while True:
                        printLine()
                        print("On the selected post you may :")
                        print("3. Post an answer if selected post is a question.")
                        print("4. Vote on the post, provided you have not already.")
                        isprevilged=isprev()
                        if isprevilged:
                            print("You are a privileged user and may do these extra tasks :")
                            print("5. Mark a post, provided it is an answer, as the accepted answer.")
                            print("6. Provide a badge to the poster of this post.")
                            print("7. Add a tag to the post.")
                            print("8. Edit the title or body of the post.")
                        
                        printLine()
                        choice_post = input('''Choose corresponding number, type "back" to go to previous menu, "logout" to go to login screen and "exit" to exit program: ''')
                        printLine()
                        if choice_post.lower() == "back":
                            break
                        if check_exit_login(choice_post) == "login_again":
                            continue_program = True
                            break
                        
                        if choice_post == "3":
                            postans(pid,pidcnt)
                        elif choice_post == "4":
                            vote(pid)
                        elif choice_post == "5" and isprevilged:
                            markans(pid)
                        elif choice_post == "6" and isprevilged: 
                            givebadge(pid)
                        elif choice_post == "7" and isprevilged:
                            add_tag(pid)
                        elif choice_post == "8" and isprevilged:
                            edit_post(pid)
                        else:
                            print("You did not select an appropriate option, try again")
            else:
                printLine()
                print("You did not select an appropriate option, try again")
            
            
            if continue_program:
                break
            printLine()




    conn.commit()
    conn.close()
    
    
if __name__ == "__main__":
  main()
        
    
    
