import unittest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

class TestEmailSending(unittest.TestCase):
    def setUp(self):
        self.sender_email = "evadbtests@gmail.com"
        self.sender_password = "pgfj odgg uemz jqvc"
        self.recipient_email = "evadbp1@gmail.com"
        
        # Connect to the SMTP server (Gmail in this example)
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(self.sender_email, self.sender_password)

    def tearDown(self):
        # Quit the server
        self.server.quit()

    def send_test_email(self, subject, body):
        # Create the message
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            # Send the email
            self.server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            print(f"Test email sent successfully! Subject: {subject}")
        except Exception as e:
            self.fail(f"Failed to send test email. Error: {e}")
        time.sleep(60)

    def test_send_email_1(self):
        subject = "Test Email 1: Personal email"
        body = "Hello, I am Emilio would you like to eat Pizza on the new restaurant tomorrow?"
        self.send_test_email(subject, body)

    def test_send_email_2(self):
        subject = "Test Email 2: Work email"
        body = "Hello, I need you to make a bot that controls my gmail account. This would be your new task on the work. \nKindest regards"
        self.send_test_email(subject, body)

    def test_send_email_3(self):
        subject = "Test Email 3: Urgent email"
        body = "Hello, I'm in a big trouble, please help me."
        self.send_test_email(subject, body)

    def test_send_email_4(self):
        subject = "Test Email 4: NotRelevant email"
        body = "Hi"
        self.send_test_email(subject, body)

if __name__ == "__main__":
    unittest.main()