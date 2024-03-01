import sqlite3
import random
import string
import hashlib

class Database:
    def checkUserExists(username):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def checkCreds(username, password):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username = ? AND pass_hash = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def returnUser(username):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USERS WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def returnUserLinks(userid):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SAVED_SHORTLINKS WHERE user_id = ?", (userid,))
        result = cursor.fetchall()
        conn.close()
        return result
    
    def returnTopTen():
        sqlString = """
        SELECT long_url, short_url, COUNT(*) AS occurrence_count
        FROM SAVED_SHORTLINKS
        GROUP BY long_url, short_url
        ORDER BY occurrence_count DESC
        LIMIT 10;
        """
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute(sqlString)
        result = cursor.fetchall()
        conn.close()
        return result
    
    def checkLinkExists(userid, shortlink):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SAVED_SHORTLINKS WHERE user_id = ? AND short_url = ?", (userid,shortlink,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def returnLongURL(shortlink):
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SAVED_SHORTLINKS WHERE short_url = ?", (shortlink,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def createNewPassword(email):
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randrange(8,15)))
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        hashed_password = sha256.hexdigest()
        conn = sqlite3.connect('relink.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE USERS SET pass_hash = ? WHERE email = ?", (hashed_password, email))
        conn.commit()
        conn.close()
        return password