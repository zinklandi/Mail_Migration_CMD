# ==============================
# This module is able to load all
# mailboxes from an existing
# mail account.
#
# developed by
# Andreas Zinkl (B.Sc.)
# Mail: zinkl.andreas@googlemail.com
# ==============================
import imaplib
import time
import getpass

# =======================
# The MailAccount class connects to the IMAP Server via SSL (TLS 1.2)
# and provides a load and store function
# =======================
class MailAccount:
    def __init__(self):
        # first we need some user input
        self.email = input("Please Enter your Email Address: ")
        self.passwd = getpass.getpass(prompt="Enter your Password: ")
        self.ssl_address = input("Please enter your IMAP Configuration (e.g.: imap.web.de): ")
        self.ssl_port = input("Which Port does the IMAP Config use? ")
        self.login_successful = False
        self.mail_data = []
        self.mailboxes = []

        # now we are able to login
        self.imap = imaplib.IMAP4_SSL(self.ssl_address)
        try:
            print("Login in to {}..".format(self.email))
            self.imap.login(self.email, self.passwd)
            print("... successfully logged in!")
            self.login_successful = True
        except imaplib.IMAP4.error as err:
            print("Login failed! We got the following error! {}".format(err))
            self.imap = None

    # check if the response we got from the imap server is OK or not
    @staticmethod
    def __is_response_OK__(rv):
        if rv == 'OK':
            return True
        else:
            return False

    # list all mailboxes which are stored in your account
    def __list_all_mailboxes__(self):
        # first check if we got a connection
        if not self.is_login_successful():
            print("Could not load Mailboxes, because Login was not successful!")
            return

        # now get the mail boxes
        rv, mailboxes = self.imap.list()
        if self.__is_response_OK__(rv):
            self.mailboxes = mailboxes

    # returns the mailboxes with the corresponding data
    # attention! the data needs to be load before! use the load_mails function therefore!
    def get_mailboxes(self):
        print("Length of mailboxes is {}".format(str(len(self.mail_data))))
        return self.mail_data

    # logout the user and close the imap session
    def logout(self):
        print(" >>> We're logging out from the mail {}!".format(self.email))
        self.imap.logout()

    # returns the result if the login was successful
    def is_login_successful(self):
        return self.login_successful

    # load all mails of your imap mail server
    def load_mails(self):
        print(" >>> Start loading data from {}".format(self.email))

        # first we need to load all folders
        self.__list_all_mailboxes__()

        # now we are able to load the mails
        for m_box in self.mailboxes:
            mailbox = m_box.decode().split(' "/" ')[1]
            mailbox_data = []
            if mailbox:
                print(" #### Start loading mailbox {}".format(mailbox))

                # select the mailbox first, where we want to search for mails
                rv, data = self.imap.select(mailbox)
                if self.__is_response_OK__(rv):

                    # now search for all mails
                    rv, data = self.imap.search(None, "ALL")
                    if not self.__is_response_OK__(rv):
                        print(" #### Found no messages in here!")
                        return

                    for num in data[0].split():
                        # fetch the mail data
                        rv, data = self.imap.fetch(num, '(FLAGS RFC822 INTERNALDATE)')
                        if not self.__is_response_OK__(rv):
                            print(" #### !! Error !! Got the message from {}".format(num))
                            continue

                        # decode the given data into message, flags and date
                        # those information are needed for the mail upload into the new account
                        message = data[0][1]
                        flags = imaplib.ParseFlags(data[0][0])
                        flags_str = []
                        for flag in flags:
                            flags_str.append("{}".format(flag.decode('ascii')))
                        flag_str = " ".join(flags_str)
                        date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(data[0][0]))

                        # temporarily safe all messages
                        mailbox_data.append({"message": message, "flag": flag_str, "date": date})

            # only if we got a mail, then we save the mailbox
            # we can ignore a mailbox, if there's no mail in it
            if len(mailbox_data) > 0:
                self.mail_data.append({"box_name": mailbox, "data": mailbox_data})

    # store given mail data into the account
    # the mailbox_data structure is the result structure of the load_mails function
    # the structure looks like this:
    # [{
    #       box_name: "TEST",
    #       data: [{
    #           message: "This is a text",
    #           flag: "SEEN",
    #           date: "2019-02-02..."
    #       }]
    # }]
    def store_mails(self, mailbox_data):
        print(" >>> Start uploading data to {}".format(self.email))

        # loop over all folders
        for box in mailbox_data:
            box_name = box['box_name']

            # sometimes there are folders which have spaces in their name
            # we need to remove the colons as well as the spaces from the name
            # and replace those with an underscore
            box_name = box_name.replace('"', "")
            box_name = box_name.replace(' ', "_")

            # now start loop over the mails within the
            print("Upload mailbox {}".format(box_name))
            for data in box['data']:
                # always create a new folder, this folder should never exist, because
                # we append the "_migration" text to the folder name
                self.imap.create(box_name+"_migration")

                # now we're going to try to upload the mail
                # SSL and imaplib specially sometimes closes the connection without any reason, which produces
                # the self.imap.abort error. Therefore we try to upload the mail 10 times. If the mail could not
                # be uploaded, then we skip this mail and try the next one
                # each time we get an error, the connection will be renewed, to get a new valid session
                upload_counter = 0
                upload_result = ['NO']
                while upload_counter < 10 or upload_result[0] != "OK":
                    try:
                        upload_result = self.imap.append(box_name+"_migration", data['flag'], data['date'], data['message'])
                        break
                    except self.imap.abort:
                        print("..connection problem ..try again to upload!")
                        upload_counter += 1
                        time.sleep(5)
                        self.imap = imaplib.IMAP4_SSL(self.ssl_address)
                        self.imap.login(self.email, self.passwd)

                if upload_result[0] != "OK":
                    print(" #### !! Error !! while copying: {}\n{}".format(box_name, upload_result[0]))


# This is the mneu part, which is basically the program flow
# and also requests the user inputs.
if __name__ == "__main__":
    # start the migration
    print(" >>> Welcome! You want to migrate your E-Mail Account? Let's start!")
    print(" >>> First we need your old E-Mail configuration! Please enter it below!")
    from_mail = MailAccount()

    if not from_mail.is_login_successful():
        print(" >>> Login failed, so we're closing the Application.. Please run the Application again!")
        exit()

    # now start loading all the mails
    from_mail.load_mails()

    print(" >>> Great! So what is your new Account?")
    to_mail = MailAccount()

    if not from_mail.is_login_successful():
        print(" >>> Login failed, so we're closing the Application.. Please run the Application again!")
        from_mail.logout()
        exit()

    # ok so we got the two accounts, let's move everything to the new account!
    to_mail.store_mails(from_mail.get_mailboxes())

    # great close the app and logout the accounts
    print(" >>> Great! We copied the whole data to the new Account! Please verify this manually to be sure!")
    print(" >>> We do not guarantee a secure migration! Errors could occur which may lead to data loss! "
          "So verify the migration by yourself!")
    from_mail.logout()
    to_mail.logout()
    print(" >>> Application is shutting down..")
