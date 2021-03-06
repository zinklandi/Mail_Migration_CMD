# Mail Migration CMD Project 
This command line tool supports your migration of old E-Mail account into the new account.
Therefore the tool uses only encrypted connections over TLS 1.2 to keep your data safe.

## How to use the tool
You need python (prefered python 3.5+) installed on your local machine. Download the python script `imap_account_migration.py` and run it with the following command:
```bash
python ./imap_account_migration.py
```
The Tool will ask you for the credentials of your old and new mail account as soon as it needs the credentials to authenticate before downloading or uploading the mails.
The credentials which will be needed are:
* Email-Address
* Password
* IMAP-Server Hostname
* IMAP-Server Port

## Questions / Erros
Please don't hesitate to contact me for any questions. If you find any error, please let me know or just create an issue or make a pull request.
Hopefully it will help you to move your old accounts to the new destination ;-)

## Thanks to
This tool is published because for security research issues. :)<br/>
Thanks to <a href="https://www.trinnovative.de">trinnovative GmbH</a> for the support! :)