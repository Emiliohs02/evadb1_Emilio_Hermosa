#import evadb
import time
from itertools import chain
import email
import imaplib
import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#cursor = evadb.connect().cursor()

print("""Hello! I'm a bot that wants to help you to administrate your gmail account.\nThe main goal is to make you easier your experience on gmail.\n
       I am going to classify your new eamils in emails for works or personal emails and a lot more of fascinating things.\n""")
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

def get_completion(prompt, model="gpt-3.5-turbo"):
    ''' Function that sends to chatGPT a message received as argument and return it answer
    I am using gpt-3.5-turbo which is the best free avaible tool'''
    # Prepare the message
    messages = [{"role": "user", "content": prompt}]
    # Sends the message
    response = openai.ChatCompletion.create(

    model=model,

    messages=messages,

    temperature=0,

    )
    # Return the answer
    return response.choices[0].message["content"]

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

    # Fow showing how does it works I use a static value for this variables
    username = "evadbp1@gmail.com"
    password = "jjpd lakl vzwm ragu"
    status = "Holidays"
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

while 1:
    # For each iteration it must try to connect to the mail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select('inbox')
    # Gets all the messages
    result, data = mail.uid('search', None, search_string(uid_max, criteria))
    # It divides all the messages that are on the gmail
    uids = [int(s) for s in data[0].split()]
    # It goes through the whole list of mails
    for uid in uids:
        # If it is a new mail it makes all the operations
        if uid > uid_max:
            # Prepating to get the mail message
            result, message_data = mail.uid('fetch', str(uid), '(RFC822)')
            for response_part in message_data:
                # Checks if it is the first iteration
                if new_message != 0:
                    # Check if the response_part is a tuple (email message)
                    if isinstance(response_part, tuple):
                        # Gets the message
                        raw_email = response_part[1]
                        msg = email.message_from_bytes(raw_email)

                        # Extract subject and body from the email message
                        subject = msg["Subject"]
                        body = ""
                        # Gets the body of the message depending if it is multipart or not
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                # Process non-attachment parts
                                if "attachment" not in content_disposition:
                                    payload = part.get_payload(decode=True)
                                    if payload is not None:
                                        body += payload.decode("utf-8", "ignore")
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload is not None:
                                body = payload.decode("utf-8", "ignore")

                        # Create a prompt for OpenAI based on the email content
                        string = "Classify this mail into: 'Work', 'Personal', 'Urgent' or 'NotRelevant'. Please respond exclusively with one of the provided words. The mail is:\n"
                        sub = "Subject: " + subject + "\n"
                        obj = "Body: " + body + "\n"
                        string += sub + obj
                        response = get_completion(string)
                        # Auxiliar print for watching in terminal how it is classifying the mail
                        print(response)

                        # Handle the response and take appropriate actions
                        if response == 'NotRelevant':
                            # If not relevant the mail is deleted
                            mail.uid('store', str(uid).encode('utf-8'), '+FLAGS', '(\Deleted)')
                            mail.expunge()

                        else:
                            # Copy the email to a new folder
                            result_copy, data_copy = mail.uid('copy', str(uid).encode('utf-8'), response)
                            # Mark the original email as seen
                            resultado, data = mail.uid('store', str(uid).encode('utf-8'), '+FLAGS', '(\Seen)')

                            # Create a summary of the email and append it to a new folder
                            string = 'Please make a summary of this mail in 2 or 3 lines maximum. The mail is: ' + body
                            response2 = sub + "\n"
                            response2 += get_completion(string)
                            mail.append('Summary' + response, None, None, response2.encode('utf-8'))

                            # Create a response message
                            string = '''Please correct the following message: Hello, at this moment I am not able to read the email because I am on''' + status + '''. I will answer you as soon as possible.\nKindest regards'''
                            response2 = get_completion(string)

                            # Configure the Gmail SMTP server
                            smtp_answer = "smtp.gmail.com"
                            answer_port = 587

                            # Start connection with SMTP server
                            # Create the message object
                            message = MIMEMultipart()
                            message["From"] = username
                            message["Subject"] = subject

                            # Attach the body of the message
                            message.attach(MIMEText(response2, "plain"))
                            server_answer = smtplib.SMTP(smtp_answer, answer_port)
                            server_answer.starttls()
                            server_answer.login(username, password)

                            # Extract sender email address
                            raw_email = response_part[1]
                            msg = email.message_from_bytes(raw_email)
                            message["To"] = msg.get("From")

                            # Send the response message
                            server_answer.send_message(message)

            uid_max = uid
    new_message = 1

# Logout and wait for a while before repeating the process
mail.logout()
time