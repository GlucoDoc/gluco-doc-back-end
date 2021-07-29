import requests
import smtplib
from email.mime.text import MIMEText

ALEXA_URI = "https://api.amazonalexa.com/v2/accounts/~current/settings/Profile.email"


def get_user_email(access_token):

    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json"
    }

    response = requests.get(ALEXA_URI, headers=headers, allow_redirects=True)

    return str(response.json())


def send_email_alert(user_email, predicted_state):
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login("no.reply.glucodoc@gmail.com", "glucodoc2016")
        # Create a text/plain message
        msg = MIMEText("We have predicted your glucose might be in a {} state!\n Please verify your glucose level.".format(predicted_state))

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = "Gluco Doc Alert"
        msg['From'] = "no-reply@glucodoc.com"
        msg['To'] = user_email

        # Send the message via our own SMTP server, but don't include the
        # envelope header.

        smtp.sendmail("no.reply.glucodoc@gmail.com", [user_email], msg.as_string())
        smtp.quit()
