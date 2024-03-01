from flask import *
import relink
import sqlite3
import hashlib
import re
from sendEmail import EmailSender
from db import Database
from flaskly import URLShortener

### In-App functions

def validate_username(username):
     return re.match("^(?=.*\d)[A-Za-z\d@$!%*?&]{6,}$", username)

def validate_password(password):
    return re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$", password)

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

def update_stats():
    global userCount, linkCount
    userCount, linkCount = get_db_connection()

def get_db_connection():
    conn = sqlite3.connect('relink.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM USERS")
    userCount = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM SAVED_SHORTLINKS")
    linkCount = cursor.fetchall()
    conn.close()
    return (userCount[0][0], linkCount[0][0])


app = Flask(__name__)

### Global Variables
emailSender = EmailSender()
user = None
userLinks = None

## For Link Saving
long_url = None
short_url = None

## For Members
shortener = None

## Database Related
userCount = None
linkCount = None 

@app.route('/algorithm',methods=['GET'])
def algorithmInfo():
    global user
    update_stats()
    return render_template('algorithm.html',user=user,userCount=userCount,linkCount=linkCount)

@app.route('/renewpass',methods=['GET','POST'])
def renewPassword():
    update_stats()
    match request.method:
        case 'GET': return render_template('update/forgotPassword.html',userCount=userCount,linkCount=linkCount)
        case 'POST':
            user = Database.returnUser(request.form['username'])
            if user:
                email = user[2]
                password = user[3]
                emailSender.remindPassword(email)

                return "An e-mail was sent you containing your password."

@app.route('/delete/link/<link_id>',methods=['POST'])
def deleteLink(link_id):
    global user
    update_stats()
    connection = sqlite3.connect('relink.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM SAVED_SHORTLINKS WHERE id = ?',(link_id,))
    connection.commit()
    connection.close()

    return redirect('/profile')

@app.route('/delete/account',methods=['GET','POST'])
def deleteAccount():
    global user
    update_stats()
    match(request.method):
        case 'GET': return render_template('update/deleteAccount.html',user=user,userCount=userCount,linkCount=linkCount)
        case 'POST':
            password = request.form['password']
            confirmPassword = request.form['confirm-password']
            if not hash_password(password) == user[3]:
                return 'Wrong credentials!'
            else:
                if not confirmPassword == password:
                    return 'Wrong credentials!'
                else:
                    connection = sqlite3.connect('relink.db')
                    cursor = connection.cursor()
                    cursor.execute('DELETE FROM USERS WHERE username = ?',(user[1],))
                    connection.commit()
                    cursor.execute('DELETE FROM SAVED_SHORTLINKS WHERE user_id = ?',(user[0],))
                    connection.commit()
                    connection.close()

                    return 'Your account has been successfully deleted!'

@app.route('/update/password',methods=['GET','POST'])
def updatePassword():
    global user
    update_stats()
    match request.method:
        case 'GET': return render_template('update/updatePassword.html')
        case 'POST':
            oldPassword = request.form['old-password']
            newPassword = request.form['new-password']
            confirmPassword = request.form['confirm-password']
            if not hash_password(oldPassword) == user[3]:
                return 'Wrong credentials!'
            else:
                if not newPassword == confirmPassword:
                    return 'Wrong credentials!'
                else:
                    connection = sqlite3.connect('relink.db')
                    cursor = connection.cursor()
                    cursor.execute('UPDATE USERS SET password = ? WHERE username = ?',(hash_password(newPassword),user[1]))
                    connection.commit()
                    connection.close()

                    return 'Your Password has been successfully updated!'

@app.route('/update/email',methods=['GET','POST'])
def updateEmail():
    global user
    update_stats()
    match request.method:
        case 'GET': return render_template('update/updateEmail.html',user=user,userCount=userCount,linkCount=linkCount)
        case 'POST':
            email = request.form['email']
            newEmail = request.form['new-email']
            password = request.form['password']
            confirm = request.form['confirm-password']
            if email == newEmail:
                return 'Same E-Mail!'
            else:
                if not password == confirm:
                    return 'Wrong credentials!'
                else:
                    connection = sqlite3.connect('relink.db')
                    cursor = connection.cursor()
                    cursor.execute('UPDATE USERS SET email = ? WHERE username = ?',(newEmail,user[1]))
                    connection.commit()
                    connection.close()

                    emailSender.newEmail(email,newEmail)
                    email = None
                    return 'Your E-Mail has been successfully updated! Check your last e-mail on your old e-mail'


@app.route('/<shortened_url>')
def redirect_to_original_url(shortened_url):
    global shortener, long_url
    if shortener is not None:
        long_url = shortener.expand_url(f'http://localhost:5000/{shortened_url}')
    else:
        long_url = Database.returnLongURL(shortened_url)
    if long_url != "URL not found":
        return redirect(long_url, code=301)
    else:
        return "URL not found", 404

@app.route('/help',methods=['GET'])
def help():
    update_stats()
    global user, userLinks
    if not user == None:
        return render_template('help.html',user=user,userLinks=userLinks,userCount=userCount,linkCount=linkCount)
    else:
        return render_template('help.html',userCount=userCount,linkCount=linkCount)
    

@app.route('/top10',methods=['GET'])
def topten():
    update_stats()
    global user, userLinks
    topTen = Database.returnTopTen()
    return render_template('topten.html',topTen=topTen,user=user,userLinks=userLinks,userCount=userCount,linkCount=linkCount)

@app.route('/profile',methods=['GET'])
def profile():
    update_stats()
    global user, userLinks
    userLinks = Database.returnUserLinks(user[0])
    return render_template('userpanel.html',user=user,userLinks=userLinks,userCount=userCount,linkCount=linkCount)

@app.route('/save',methods=['POST'])
def saveLink():
    update_stats()
    try:
        global long_url, short_url, user, userLinks
        doesExist = Database.checkLinkExists(user[0],short_url)
        if doesExist:
            return "You've already saved this link!"
        else:
            userLinks = Database.returnUserLinks(user[0])
            if len(userLinks) > 10: #Potential paid feature to increase this limit
                return "You've saved too many links!"
            else:
                conn = sqlite3.connect('relink.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO SAVED_SHORTLINKS VALUES(NULL,?,?,?)",(user[0],long_url,short_url))
                conn.commit()
                conn.close()
                return "Link saved successfully!"
    except Exception as e:
        print(e)
        return "Something went wrong!"


@app.route('/logout',methods=['GET'])
def logout():
    global user, userLinks
    update_stats()
    user = None
    userLinks = None
    return redirect('/')

@app.route('/signup',methods=['POST'])
def signup():
    update_stats()
    if not Database.checkUserExists(request.form['username-signup']):
        global emailSender
        username = request.form['username-signup']
        email = request.form['email']
        password = request.form['password-signup']
        confirmPassword = request.form['confirm-password-signup']

        if not validate_username(username):
            return "Invalid username"
        elif not validate_password(password):
            return "Invalid password"
        
        if not password == confirmPassword:
            return "Passwords do not match"

        hashed_password = hash_password(password)
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USERS VALUES(NULL,?,?,?)",(username,email,hashed_password))
        conn.commit()
        conn.close()

        emailSender.signup(email)

        return "User signed up successfully! Check your e-mail for verification"
    else:
        return "User exists!"

@app.route('/login',methods=['GET','POST'])
def login():
    global user, userLinks, shortener
    update_stats()
    match request.method:
        case 'GET': return render_template("login.html",userCount=userCount,linkCount=linkCount)
        case 'POST':
            username = request.form['username-login']
            password = request.form['password-login']
            hashed_password = hash_password(password)
            if Database.checkUserExists(username):
                if Database.checkCreds(username, hashed_password):
                    user = Database.returnUser(username)
                    userLinks = Database.returnUserLinks(user[0])
                    shortener = URLShortener()
                    return redirect('/')
                else:
                    return "Invalid credentials!"
            else:
                return "User doesn't exist! Please create a new account!"

@app.route('/',methods=['GET','POST'])
def index():
    global user,userLinks
    global long_url,short_url
    global shortener
    update_stats()
    match request.method:
        case 'GET':
            if not user == None:
                return render_template('index.html',userCount=userCount,linkCount=linkCount,user=user,userLinks=userLinks)
            else:
                return render_template('index.html',userCount=userCount,linkCount=linkCount)
        case 'POST':
            long_url = request.form['url']
            url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
            if not url_pattern.match(long_url):
                return "Invalid URL format."
            else:
                sanitized_url = re.sub(r'<script>', '', long_url)
                if user == None:
                    short_url = relink.shorten_url(long_url)
                else:
                    short_url = shortener.shorten_url(long_url)
                if not user == None:
                    return render_template('index.html',short_url=short_url,userCount=userCount,linkCount=linkCount,user=user,userLinks=userLinks)
                else:
                    return render_template('index.html',short_url=short_url,userCount=userCount,linkCount=linkCount)

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)