import getpass, imaplib, os
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup as bs
from config import user, pwd


def main():

    # save emails to textfile
    fdir = os.path.dirname(os.path.realpath(__file__))
    fname_base = os.path.join(fdir, "text-files")

    # directory where to save attachments (default: current)
    detach_dir = "."

    # get user info if not passed through a config file
    # user = input("Enter your GMail username:")
    # pwd = getpass.getpass("Enter your password: ")

    # connecting to the gmail imap server
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user, pwd)

    # use m.list() to get all the mailboxes
    m.select("Inbox")  # defaults to INBOX or pass string

    # get unread emails from Matt Levine
    res, items = m.search(None, "(UNSEEN)", '(FROM "Matt Levine")')

    # get all emails from Matt Levine
    # res, items = m.search(None, '(FROM "Matt Levine")')

    # scrape all of them
    items = items[0].split()  # getting the mails id

    for emailid in items:

        res, data = m.fetch(emailid, "(RFC822)")

        email_body = data[0][1]  # getting the mail content

        # Content Type Encoding is base64
        #
        # to check other parts of mail object
        # for ele in mail:
        #     print(ele)

        mail = BytesParser(policy=default).parsebytes(email_body)

        # get date from weird format
        datestr = mail["Date"]
        datelst = datestr.split(" ")[1:4]
        date = " ".join(datelst)

        # set textfile name to save as
        subject = mail["Subject"]

        # make specific name
        # name = subject + " (" + date + ").txt"
        name = "({d}) {s}.txt".format(d = date, s = subject)

        fname = os.path.join(fname_base, name)

        # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
        print("Scraping {}".format(subject))

        txt = ""
        for part in mail.walk():
            p = part.get_payload(decode=True)
            content_type = part.get_content_type().strip()
            if p != None and content_type == "text/plain":
                s = bs(p, "lxml")
                t = s.get_text()
                txt += t

        text = (
            txt.replace("\t", " ")
            .replace("\n", ". ")
            .replace("\r", "")
            .replace("\xa0", " ")
            .replace("]]>", "")
        )

        text = " ".join(
            [ele.strip() for ele in text.split(" ") if ele != " " and ele != ""]
        )

        with open(fname, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
