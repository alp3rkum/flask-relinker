import os
import smtplib
from email.message import EmailMessage
from db import Database

current_directory = os.path.dirname(os.path.abspath(__name__))
html_file_paths = [os.path.join(current_directory, 'templates', 'email', 'signup.html'),os.path.join(current_directory,'templates','email','updateEmail.html'),os.path.join(current_directory,'templates','email','passchange.html'),os.path.join(current_directory,'templates','email','remindPassword.html')]

class EmailSender:
    msg_content = None
    msg_content_template = None
    def signup(self,email):
        with open(html_file_paths[0], 'r') as f:
            self.msg_content = f.read()
        msg = EmailMessage()
        msg.set_content(self.msg_content, subtype='html')
        msg['Subject'] = 'Welcome to Flask Relinker!'
        msg['From'] = "Flask Relinker"
        msg['To'] = email

        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
            smtp.login("flaskrelinker@gmail.com", "tezd qznz golp fhmb")
            smtp.send_message(msg)
            print("Email sent successfully")
        except Exception as e:
            print(e)
    
    def newEmail(self,email,newEmail):
        with open(html_file_paths[1],'r') as f:
            self.msg_content_template = f.read()
            self.msg_content = self.msg_content_template.replace('{{newEmail}}',newEmail)

        msg = EmailMessage()
        msg.set_content(self.msg_content, subtype='html')
        msg['Subject'] = 'Flask Relinker E-Mail Update'
        msg['From'] = "Flask Relinker"
        msg['To'] = email

        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
            smtp.login("flaskrelinker@gmail.com", "tezd qznz golp fhmb")
            smtp.send_message(msg)
            print("Email sent successfully")
        except Exception as e:
            print(e)
    
    def newPassword(self,email):
        with open(html_file_paths[2],'r') as f:
            self.msg_content = f.read()
        msg = EmailMessage()
        msg.set_content(self.msg_content, subtype='html')
        msg['Subject'] = 'Flask Relinker Password Update'
        msg['From'] = "Flask Relinker"
        msg['To'] = email

        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
            smtp.login("flaskrelinker@gmail.com", "tezd qznz golp fhmb")
            smtp.send_message(msg)
            print("Email sent successfully")
        except Exception as e:
            print(e)
    
    def remindPassword(self,email):
        password = Database.createNewPassword(email)
        with open(html_file_paths[3],'r') as f:
            self.msg_content_template = f.read()
            self.msg_content = self.msg_content_template.replace('{{password}}',password)
        msg = EmailMessage()
        msg.set_content(self.msg_content, subtype='html')
        msg['Subject'] = 'Flask Relinker Password Remind'
        msg['From'] = "Flask Relinker"
        msg['To'] = email

        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com',465)
            smtp.login("flaskrelinker@gmail.com", "tezd qznz golp fhmb")
            smtp.send_message(msg)
            print("Email sent successfully")
        except Exception as e:
            print(e)