import evadb
import time
from itertools import chain
import email
import imaplib
from datetime import datetime, timedelta
import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from gpt4all import GPT4All
print("""Hello! I'm a bot that wants to help you to administrate your gmail account.\nThe main goal is to make you easier your experience on gmail.\n
I am going to classify your new eamils in emails for works or personal emails and a lot more of fascinating things.\n
The bot has two modes:\n 
      1. The first mode is for getting administration of new emails authomatically, classifying them, answering them, etc.\n 
      2. The second mode is for you to ask me about all the emails from a concrete date gap i.e. emails from (01-26-2020) (optional you can specify the sender)\n\n\n""")

mode = input("What mode do you want me to use? (Write 1 for mode 1 and 2 for mode 2)\n")


def achieve_emails(fd, sender):
    "Function to get all the emails from one date "
    # Gets the date with the correct format for imaplib
    if fd != "no":
        date_in = datetime(int(fd[6:]), int(fd[:2]), int(fd[3:5]))
        date_in = date_in.strftime('%d-%b-%Y')
    # If there is a sender the name of the new folder with the mails and the query will be different than if only provided the date
    if sender != "no" and fd != "no":
        mail.create(str(date_in) + "-" + str(sender))
        query = f'(SENTON {date_in} FROM "{sender}")'
    elif fd != "no":
        mail.create(str(date_in))
        query = f'(SENTON {date_in})'
    else:
        mail.create(str(sender))
        query = f'(FROM "{sender}")'
    
    result, data = mail.uid('search', None, query)

    # Process the results
    if result == 'OK':
        ids = data[0].split()
        for email_id in ids:
            if sender != "no" and fd != "no":
                mail.uid('copy', email_id, str(date_in) + "-" + str(sender))
            elif sender != "no":
                mail.uid('copy', email_id, str(sender))
            else:
                mail.uid('copy', email_id, str(date_in))
            

    else:
        print("Error in the search.")


# Different variables need for the script
#Mail account
mail = imaplib.IMAP4_SSL("imap.gmail.com")
# Var to check if you have been able to connect to a user
connected = False
# Variable for getting the information of the emails
criteria = {}
# Get the number of message read
uid_max = 0
# Special key to connect to OpenAI
openai.api_key = "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"
# Variable for not checking the first time the mail
new_message = 0
#llm = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

def get_completion(prompt, model="gpt-3.5-turbo"):
    ''' Function that sends to chatGPT a message received as argument and return it answer
    I am using gpt-3.5-turbo which is the best free avaible tool'''
    # Prepare the message
    messages = [{"role": "user", "content": prompt}]
    # Sends the message to chatgpt
    response = openai.ChatCompletion.create(

    model=model,

    messages=messages,

    temperature=0,

    )
    # Return the answer
    return response.choices[0].message["content"]

def take_name(name):
    aux = ""
    for i in name:
        if i == '@':
            return aux
        aux += i

def search_string(uid_max, criteria):
    ''' Function that helps getting all the mails in the 'inbox' email account '''
    # Map the criteria dictionary to a list of tuples, where each tuple contains the key and its quoted value
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    # Join the list of tuples into a space-separated string within parentheses
    return '(%s)' % ' '.join(chain(*c))

while not connected:
    '''Loop to connect to the account. Until you don't connect to an account the loop wouldn't end'''

    #For a normal performance we should use this commented lines 

    #username = input("First of all I need you to give me your gmail address: ")
    #password = input("And finally your password: ")
    #status = input("Please tell me why couldn't you be able to answer right now the mail for the authomatic answer")

    # For showing how does it works I use a static value for this variables
    username = "evadbp1@gmail.com"
    password = "prvv agfw bgbc fvdm"
    status = "Working"
    try:
        # Tries to log in
        mail.login(username, password)
        # In case it can log in, selects the 'inbox' and create new folders for the classification of emails
        mail.select('inbox')
        mail.create("Work")
        mail.create("Personal")
        mail.create("Urgent")
        mail.create("SummaryUrgent")
        mail.create("SummaryWork")
        connected = True
    except:
        print("One or more invalid arguments\n")
cursor = evadb.connect().cursor()
cursor.query("DROP TABLE IF EXISTS " + str(take_name(username)) + "_blocked").df()
# Create a table for storing the mails of blocked or potential blocked address
cursor.query(f"""
    CREATE TABLE {str(take_name(username))}_blocked (
        addr TEXT(20) UNIQUE,
        notrelevantmails INTEGER
    )
    """
).df()

if mode == "2":
    initial_date = input("What day do you want to get the emails from? (Format of date must be MM-DD-YYYY). If you don't want a specific date write 'no'\n")
    #final_date = input("Tell me the last day you want me to take the emails from. If is the same date as the last one, write it as again.\n")
    sender = input("write the email address of a specific sender if you want emails from only one person. If not write 'no'\n")
    achieve_emails(initial_date, sender)
else:
    possible_blocked = []
    while 1:
        try:
            with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
                # connects to the mail account for each iteration
                mail.login(username, password)
                mail.select('inbox')
                # Gets all the mails in the account and divided them and store them on a list
                result, data = mail.uid('search', None, search_string(uid_max, criteria))
                uids = [int(s) for s in data[0].split()]
                # Goes throw the whole list
                for uid in uids:
                    # If it is a new message is going to do the actions should do
                    if uid > uid_max:
                        # gets the whole message
                        result, message_data = mail.uid('fetch', str(uid), '(RFC822)')
                        for response_part in message_data:
                            blocked = 0
                            # If it is the first iteration it mustn't do anything. This way we don't clasiffy all the messages all the times it is executed the bot
                            if new_message != 0:
                                # Gets the important part of the message and store it in two variables, one called subject and the other called body
                                if isinstance(response_part, tuple):
                                    # Get the part of the email we are interested
                                    raw_email = response_part[1]
                                    msg = email.message_from_bytes(raw_email)

                                    subject = msg["Subject"] # Gets the subject
                                    body = ""
                                    # Checks if the message is multipart to take the body
                                    if msg.is_multipart():
                                        for part in msg.walk():
                                            content_type = part.get_content_type()
                                            content_disposition = str(part.get("Content-Disposition"))

                                            if "attachment" not in content_disposition:
                                                payload = part.get_payload(decode=True)
                                                if payload is not None:
                                                    body += payload.decode("utf-8", "ignore")
                                    # If it is not multipart it gets easily the body
                                    else:
                                        payload = msg.get_payload(decode=True)
                                        if payload is not None:
                                            body = payload.decode("utf-8", "ignore")
                                    #Asks chat-gpt-3.5-turbo for a clasification of the mail and returt the response
                                    string = "Classify this mail into: 'Work', 'Personal', 'Urgent' or 'NotRelevant'. Please respond exclusively with one of the provided words. Spam emails must be classified as NotRelevant as well. The mail is:\n"
                                    sub = "Subject: " + subject + "\n"
                                    obj = "Body: " + body + "\n"
                                    string += sub + obj
                                    sender = msg.get("From")
                                    if sender in possible_blocked:
                                        # Checks if the one who sent the email is blcked
                                        cursor.query(f"INSERT INTO {str(take_name(username))}_blocked (addr, notrelevantmails) VALUES ('{str(take_name(sender))}', 0)").df()                                       
                                        res = cursor.query(f"SELECT notrelevantmails FROM {str(take_name(username))}_blocked WHERE addr = '{str(take_name(sender))}'").df()
                                        for index, counter in res.iterrows() :
                                            # In case he is blocked the mail will be erased and the program will not process nothing about it
                                            if counter[take_name(username)+"_blocked.notrelevantmails"] > 5:
                                                mail.uid('store', str(uid).encode('utf-8'), '+FLAGS', '(\Deleted)')
                                                mail.expunge()
                                                blocked = 1
                                    if not blocked:
                                        # If he is not blocked he will make the regular things
                                        response = get_completion(string)
                                        print(response)
                                        # If it is not relevant the email is deleted
                                        if response == 'NotRelevant':
                                            mail.uid('store', str(uid).encode('utf-8'), '+FLAGS', '(\Deleted)')
                                            mail.expunge()
                                            if sender in possible_blocked:
                                                # Update the number of irrelevant emails that the sender has sent till now
                                                res = cursor.query(f"SELECT notrelevantmails FROM {str(take_name(username))}_blocked WHERE addr = '{str(take_name(sender))}'").df()
                                                for index, counter in res.iterrows():
                                                    val = counter[take_name(username)+"_blocked.notrelevantmails"]
                                                val = val + 1
                                                cursor.query(f"DELETE FROM {str(take_name(username))}_blocked WHERE addr = '{str(take_name(sender))}'").df()
                                                cursor.query(f"INSERT INTO {str(take_name(username))}_blocked ( addr, notrelevantmails ) VALUES ( '{str(take_name(sender))}', '{str(val+1)}');").df()
                                            else:
                                                # If is the first irrelevant email from the boy we will just create a new row for him
                                                print(str(take_name(sender)))
                                                cursor.query(f"INSERT INTO {str(take_name(username))}_blocked ( addr, notrelevantmails ) VALUES ( '{str(take_name(sender))}', 1);").df()
                                                possible_blocked.append(sender)
                                        # In case it is: work, urgent or personal email, it would be sent to a new fonder
                                        else:
                                            result_copy, data_copy = mail.uid('copy', str(uid).encode('utf-8'), response)
                                            # In case it is a work or urgent email it makes a summary of it and send it to a folder
                                            if response == 'Work' or response == 'Urgent':
                                                string = 'Please make a summary of this mail in 2 or 3 lines maximum. The mail is: ' + body
                                                response2 = sub + "\n"
                                                response2 += get_completion(string)
                                                mail.append('Summary' + response, None, None, response2.encode('utf-8'))
                                            # Asks chat-gpt for a response to the mail telling why you can't answer it right now
                                            string = '''Send a response to the mail I am going to show you right now specifying why it is not possible for me to read right now the mail because I am on a specific status.
                                                        A good example would be: Hello, I am sorry, I am not able to read right now the mail because I am on my holidays. Kindest regards.  A bad example would be: Hello [sender], I will not be able 
                                                        to answer you until [Date] because I am on holidays. This would be a bad example because you are using [sender], [date] or [Your name]. The mail MUST finish exactly like this: 'best regards.' IMPORTANT DONT WRITE NOTHING LIKE [sender], [date] or [Your name].
                                                        My status right now is ''' + status + '''and the email receive is  ''' + body
                                            response2 = get_completion(string)
                                            # Asks chatgpt for the answer
                                            # Prepare the script to send the message created from chatgpt and sends it
                                            smtp_answer = "smtp.gmail.com"
                                            answer_port = 587

                                            message = MIMEMultipart()
                                            message["From"] = username
                                            message["Subject"] = subject

                                            message.attach(MIMEText(response2, "plain"))
                                            server_answer = smtplib.SMTP(smtp_answer, answer_port)
                                            server_answer.starttls()
                                            server_answer.login(username, password)

                                            raw_email = response_part[1]
                                            msg = email.message_from_bytes(raw_email)
                                            message["To"] = sender

                                            server_answer.send_message(message) # Sends the message
                                            resultado, data = mail.uid('store', str(uid).encode('utf-8'), '-FLAGS', r'(\Seen)')

                        uid_max = uid

        except Exception as e:
            print(f'Error: {e}')

        new_message = 1
        time.sleep(1)  # Add a small delay before re-checking to avoid aggressive reconnection attempts


# Logout should be outside the loop
mail.logout()