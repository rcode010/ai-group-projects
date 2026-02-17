import smtplib
import ssl
from email.message import EmailMessage
import time

class EmailAgent:
    def __init__(self, sender_email, email_password):
        self.sender_email = sender_email
        self.email_password = email_password
        self.smtp_server = "smtp.gmail.com"
        self.port = 465  

    def send_email(self, receiver_email, subject, body):
        
        """
        Sends an email alert to the specified receiver.
        """
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg.set_content(body)

      
        context = ssl.create_default_context()

        try:
            print(f"📧 Agent attempting to send email to {receiver_email}...")
            
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.sender_email, self.email_password)
                server.send_message(msg)
                
            print("✅ Email sent successfully!")
            return True 
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
        

if __name__ == "__main__":
    MY_EMAIL = "randk5991@gmail.com"
    MY_APP_PASSWORD = "aehg ztma zipl abwf" 
    ADMIN_EMAIL = "randzana1920@gmail.com" 

  
    agent = EmailAgent(MY_EMAIL, MY_APP_PASSWORD)

   
    print("... Email Agent is running and waiting for triggers ...")
    
    incoming_alert_subject = "CRITICAL WARNING: RAM Usage High"
    incoming_alert_body = "Alert from System: RAM usage has exceeded 90%. Please check the server immediately."
     
    agent.send_email(ADMIN_EMAIL, incoming_alert_subject, incoming_alert_body)