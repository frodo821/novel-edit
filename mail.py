#-*-coding: utf-8;-*-
"""noveleditor.mail
投稿機能をサポート
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from threading import Thread
from warnings import warn

def create_message(subj, msg, from_, to):
    mes = MIMEText(msg, _subtype='html', _charset='utf-8')
    mes["Subject"] = subj
    mes["From"] = from_
    mes["To"] = to
    mes["Date"] = formatdate(localtime=True)
    return mes

def send(sbj, body, config, callback=lambda: None):
    if not sbj:
        raise ValueError("小説タイトルは必ず設定する必要があります")
    def __post():
        from_ = config["user"]["mailaddr"]
        passwd = config["user"]["password"]
        to = config["post-to"]
        msg = create_message(sbj, body, from_, to)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.ehlo()
        try:
            s.login(from_, passwd)
        except BaseException as e:
            callback(f"投稿に失敗しました: {str(e)}")
            return
        s.sendmail(from_, to, msg.as_string())
        s.quit()
        try:
            callback()
        except TypeError:
            warn("Non-callable callback")
    pt = Thread(target=__post)
    pt.start()
