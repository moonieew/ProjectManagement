from flask import Flask
import smtplib

app=Flask(__name__)

@app.route('/')
def index():
    mes="hello"
    sever = smtplib.SMTP("smtp.gmail.com",587)
    sever.starttls()
    sever.login("sdkansdkan1234@gmail.com","mkmkmk12")
    sever.sendmail("sdkansdkan1234@gmail.com","sdkansdkan123@gmail.com",mes)
    return "Sent"

if __name__=="__main__":
    app.run()