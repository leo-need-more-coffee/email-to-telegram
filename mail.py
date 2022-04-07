import imaplib
import aiogram.utils.markdown as md
from bs4 import BeautifulSoup as bs
import mailparser as p
import socket


def get_last_mail(imap, username, password, last_email, pathname="temp"):
    try:
        socket.setdefaulttimeout(5)
        mail = imaplib.IMAP4_SSL(imap)
        mail.login(username, password)
        mail.select(readonly=True)  # refresh inbox

        status, message_ids = mail.search(None, "ALL")  # get all emails
        message_id = message_ids[0].split()[-1]
        status, message_data = mail.fetch(message_id, '(RFC822)')
        actual_message = p.parse_from_bytes(message_data[0][-1])
        headers = actual_message.headers
        current_msg = ""
        attr = ["From", "To", "Date", "Subject"]
        for el in attr:
            current_msg += "%s: %s" % (md.bold(el), headers[el]) + "\n"
        soup = bs(str(actual_message.text_html), features="lxml")
        #breadcrum = [item.strip().replace("\\n", " ").replace("\\r", "").replace("\\t", "") + "\n" for item in soup.strings if str(item)][1:-1]
        current_msg += md.bold("Текст письма") + ":\n" + (soup.get_text()[2:-2].replace("\\n", "").replace("\\r", "").replace("\\t", "")).strip() #"".join(breadcrum)
        msg_id = headers["Message-ID"]
        if msg_id != last_email:
            actual_message.write_attachments(pathname)
            return (current_msg, len(actual_message.attachments) > 0, msg_id)
        return (current_msg, False, msg_id)
    except Exception as e:
        print(e)
        return ("Ошибка. Проверьте правильность написания. Ошибка:\n" + str(e), False, None)
