import smtplib
from email.mime.text import MIMEText


def send_email(user_email, subject, message, message_type='plain'):

    # i18n.load_path.append('../i18n')
    # i18n.set('filename_format', locale + '.json')
    # i18n.set('skip_locale_root_data', True)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login("no.reply.glucodoc@gmail.com", "glucodoc2016")

        msg = MIMEText(message, message_type)
        msg['Subject'] = subject
        msg['From'] = "no-reply@glucodoc.com"
        msg['To'] = user_email

        smtp.sendmail("no.reply.glucodoc@gmail.com", [user_email], msg.as_string())
        smtp.quit()
