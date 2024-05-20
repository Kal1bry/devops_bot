import logging
import re
import paramiko
import shlex
import psycopg2
import os
import subprocess
from dotenv import load_dotenv, find_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

load_dotenv(find_dotenv(), override=True, verbose=True)

# Token connecting
TOKEN = os.getenv('TOKEN')


#Enabling logging
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


#Creating bot class for linux monitoring
class LinuxMonitorBot:
    def __init__(self, hostname, port, username, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname, port, username, password)

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode()

    def get_release(self):
        return self.execute_command('lsb_release -a')

    def get_uname(self):
        return self.execute_command('uname -a')

    def get_uptime(self):
        return self.execute_command('uptime')

    def get_df(self):
        return self.execute_command('df -h')

    def get_free(self):
        return self.execute_command('free -h')

    def get_mpstat(self):
        return self.execute_command('mpstat | head -n 5')

    def get_w(self):
        return self.execute_command('w')

    def get_auths(self):
        return self.execute_command('last -n 10')

    def get_critical(self):
        return self.execute_command('journalctl -p 2 -n 5')

    def get_ps(self):
        return self.execute_command('ps aux | head -n 5')

    def get_ss(self):
        return self.execute_command('ss -tulwn')
    
    def get_apt_list(self, package):
        if package:
            safe_package = shlex.quote(package)
            return self.execute_command(f'apt list {safe_package}')
        else:
            output = self.execute_command('apt list --installed | head -n 10')
            return output

    def get_services(self):
        return self.execute_command('systemctl list-units --type=service | head -n 5')

    


hostname = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_username = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_database = os.getenv('DB_DATABASE')
# Creating class example
bot = LinuxMonitorBot(hostname, port, username, password)


# Functions to call class functions and others
def start(update: Update, context):
    global user
    user = update.effective_user
    update.message.reply_text(f'Hello {user.full_name}!')
    logger.info(f'User {user.full_name} started bot')


def helpCommand(update: Update, context):
    update.message.reply_text('All commands: \n1) /find_phone_number - find numbers in text; \n2) /find_email - find email addresses in text;\n 3) /verify_password - check password complexity;\n4) /get_release - get system release information;\n5) /get_uname - get system uname information;\n6) /get_uptime - get system uptime;\n7) /get_df - get file system information;\n8) /get_free - get free memory information;\n9) /get_mpstat - get system performance;\n10) /get_w - get information about system users;\n11) /get_auths - get last 10 system auths/\n12) /get_critical - get last 5 critical events;\n13) /get_ps - get running processes;\n14) /get_ss - get used ports;\n15) /get_apt_list - get installed packages (if you need get information about a specific package, just write the package after command);\n16) /get_services - get running services;\n17) /get_emails - get written emails;\n18) /get_phone_numbers - get written numbers;\n19) /get_repl_logs - get replication logs.')

def get_release(update: Update, context):
    logger.info(f"/get_release command executed by {user.full_name}")
    update.message.reply_text(bot.get_release())

def get_uname(update: Update, context):
    logger.info(f"/get_uname command executed by {user.full_name}")
    update.message.reply_text(bot.get_uname())

def get_uptime(update: Update, context):
    logger.info(f"/get_uptime command executed by {user.full_name}")
    update.message.reply_text(bot.get_uptime())

def get_df(update: Update, context):
    logger.info(f"/get_df command executed by {user.full_name}")
    update.message.reply_text(bot.get_df())

def get_free(update: Update, context):
    logger.info(f"/get_free command executed by {user.full_name}")
    update.message.reply_text(bot.get_free())

def get_mpstat(update: Update, context):
    logger.info(f"/get_mpstat command executed by {user.full_name}")
    update.message.reply_text(bot.get_mpstat())

def get_w(update: Update, context):
    logger.info(f"/get_w command executed by {user.full_name}")
    update.message.reply_text(bot.get_w())

def get_auths(update: Update, context):
    logger.info(f"/get_auths command executed by {user.full_name}")
    update.message.reply_text(bot.get_auths())

def get_critical(update: Update, context):
    logger.info(f"/get_critical command executed by {user.full_name}")
    update.message.reply_text(bot.get_critical())

def get_ps(update: Update, context):
    logger.info(f"/get_ps command executed by {user.full_name}")
    update.message.reply_text(bot.get_ps())

def get_ss(update: Update, context):
    logger.info(f"/get_ss command executed by {user.full_name}")
    update.message.reply_text(bot.get_ss())

def get_apt_list(update: Update, context: CallbackContext):
    logger.info(f"/get_apt_list command executed by {user.full_name}")
    if context.args:
        package = ' '.join(context.args)
    else:
        package = None

    packages = bot.get_apt_list(package).strip()

    if packages:
        for pkg in packages.split('\n'):
            update.message.reply_text(pkg)
    else:
        update.message.reply_text("No packages found.")

def get_services(update: Update, context):
    logger.info(f"/get_services command executed by {user.full_name}")
    update.message.reply_text(bot.get_services())


#Function to find phone numbers
def findPhoneNumbersCommand(update: Update, context):
    logger.info(f"/find_phone_numbers command executed by {user.full_name}")
    update.message.reply_text('Enter text to find numbers: ')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phoneNumRegex = re.compile(r"\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|\+?7[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}|8[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}")
    global phoneNumberList  # Declare phoneNumberList as global
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Numbers are not found in the promoted text.')
        return ConversationHandler.END  # End the conversation if no numbers are found

    phoneNumbers = ''
    for i, phone_tuple in enumerate(phoneNumberList):
        phone = ''.join(phone_tuple)
        phoneNumbers += f'{i+1}. {phone}\n'
        logger.info(f'New phone number {phone} found in text')

    update.message.reply_text(phoneNumbers)

    update.message.reply_text('Do you want to save found phone numbers in the database? (Yes/No)')
    return 'savePhoneNumbers'

#Function to save phone numbers
def savePhoneNumbers(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'yes':
        conn = psycopg2.connect(
            dbname=db_database,
            user=db_username,
            password=db_password,
            host=db_host
        )
        cur = conn.cursor()
        for phone_tuple in phoneNumberList:
            phone = ''.join(phone_tuple)
            cur.execute(f"insert into phone_numbers (value) values ('{phone}');")
            logger.info(f'New phone number {phone} was written to database')
        cur.close()
        conn.commit()  # Commit the transaction
        conn.close()

        update.message.reply_text('Phone numbers successfully saved!')
    elif user_input == 'no':
        update.message.reply_text('Nothing will be saved.')
    else:
        update.message.reply_text('Please answer "Yes" or "No".')

    return ConversationHandler.END  # End the conversation

#Functions to find email addresses
def findEmailsCommand(update: Update, context):
    logger.info(f'/find_email command executed by {user.full_name}')
    update.message.reply_text('Enter text to find email-addresses: ')
    return 'findEmails'


def findEmails(update: Update, context):
    user_input = update.message.text

    emailRegex = r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+)*' \
                 r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    global emailList
    emailList = re.findall(emailRegex, user_input)

    if not emailList:
        update.message.reply_text('Email-addresses are not found in the promoted text.')
        return

    emails = '\n'.join(emailList)
    update.message.reply_text(emails)
    update.message.reply_text('Do you want to save found email addresses in the database? (Yes/No)')
    return 'saveEmails'

#Function to save email addresses
def saveEmails(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'yes':
        conn = psycopg2.connect(
            dbname=db_database,
            user=db_username,
            password=db_password,
            host=db_host
        )
        cur = conn.cursor()
        for email_tuple in emailList:
            email = ' '.join(email_tuple).replace(" ","")
            cur.execute(f"insert into emails (email) values ('{email}');")
            logger.info(f'New email addres {email} was inserted to database')
        cur.close()
        conn.commit()  # Commit the transaction
        conn.close()

        update.message.reply_text('Email addresses successfully saved!')
    elif user_input == 'no':
        update.message.reply_text('Nothing will be saved.')
    else:
        update.message.reply_text('Please answer "Yes" or "No".')

    return ConversationHandler.END  # End the conversation


def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Enter the password for checking complexity: ')
    return 'verifyPassword'


def verifyPassword(update: Update, context):
    user_input = update.message.text
    logger.info(f'Password verification command was execured by {user.full_name} with password {user_input}')
    # Regex for numbers
    passwordRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}$')

    if passwordRegex.match(user_input):
        update.message.reply_text('Password is difficult')
    else:
        update.message.reply_text('Password is simple')

    return ConversationHandler.END


def get_logs(update: Update, context):
    logger.info(f"/get_repl_logs was executed by {user.full_name}")
    command = "cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode() != "":
        update.message.reply_text("Can not open log file!")
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))
    
#Functions to get info from db
def get_emails(update: Update, context):
    logger.info(f"/get_emails was executed by {user.full_name}")
    conn = psycopg2.connect(
        dbname=db_database,
        user=db_username,
        password=db_password,
        host=db_host
    )
    cur = conn.cursor()
    cur.execute("SELECT email FROM emails")
    emails = cur.fetchall()
    for email in emails:
        update.message.reply_text(email[0])
    cur.close()
    conn.close()

def get_phone_numbers(update: Update, context):
    logger.info(f"/get_phone_numbers was executed by {user.full_name}")
    conn = psycopg2.connect(
        dbname=db_database,
        user=db_username,
        password=db_password,
        host=db_host
    )
    cur = conn.cursor()
    cur.execute("SELECT value FROM phone_numbers")
    emails = cur.fetchall()
    for email in emails:
        update.message.reply_text(email[0])
    cur.close()
    conn.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


#Main function to handle conversations.
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'savePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, savePhoneNumbers)]
            },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'saveEmails': [MessageHandler(Filters.text & ~Filters.command, saveEmails)]
            },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],},
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list, pass_args=True))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
