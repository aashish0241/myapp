import os
import os.path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from service import register_sms_receiver  # Import the service function
from kivy.utils import platform

# Conditionally import Android permissions module.
if platform == 'android':
    from android.permissions import request_permissions, Permission
else:
    # Dummy function and Permission class for non-Android platforms.
    def request_permissions(perms):
        print("Not on Android: Skipping permission request.")

    class Permission:
        RECEIVE_SMS = "RECEIVE_SMS"
        READ_SMS = "READ_SMS"
        INTERNET = "INTERNET"
        READ_PHONE_STATE = "READ_PHONE_STATE"


def get_user_data_dir():
    """
    Returns the app's private directory on Android.
    If not on Android, returns the current directory.
    """
    return os.environ.get("ANDROID_PRIVATE", ".")


class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super(MainUI, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [20, 20, 20, 20]
        self.spacing = 20

        # Header label
        header = Label(
            text="SMS OTP Reader Setup",
            font_size="24sp",
            bold=True,
            size_hint=(1, 0.1)
        )
        self.add_widget(header)

        # Create a grid layout for form fields
        form = GridLayout(
            cols=1,
            spacing=10,
            row_force_default=True,
            row_default_height=40,
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        # Phone Number field
        form.add_widget(Label(text="Phone Number:", size_hint_x=0.4))
        self.phone_input = TextInput(
            hint_text="Enter phone number",
            multiline=False,
            size_hint_x=0.6
        )
        form.add_widget(self.phone_input)

        # Email field
        form.add_widget(Label(text="Email:", size_hint_x=0.4))
        self.email_input = TextInput(
            hint_text="Enter email",
            multiline=False,
            size_hint_x=0.6
        )
        form.add_widget(self.email_input)

        # App Password field
        form.add_widget(Label(text="App Password:", size_hint_x=0.4))
        self.pass_input = TextInput(
            hint_text="Enter app password",
            multiline=False,
            password=True,
            size_hint_x=0.6
        )
        form.add_widget(self.pass_input)

        self.add_widget(form)

        # Status Label
        self.status_label = Label(
            text="Status: Waiting for input",
            size_hint=(1, 0.1)
        )
        self.add_widget(self.status_label)

        # Start Button
        self.start_button = Button(
            text="Start SMS Monitoring",
            size_hint=(1, 0.1)
        )
        self.start_button.bind(on_press=self.start_service)
        self.add_widget(self.start_button)

    def start_service(self, instance):
        # Validate that all required fields are filled
        phone = self.phone_input.text.strip()
        email = self.email_input.text.strip()
        password = self.pass_input.text.strip()

        if not phone or not email or not password:
            self.status_label.text = "Error: All fields are required."
            return

        # Save credentials to the app's private directory
        data_dir = get_user_data_dir()
        cred_file = os.path.join(data_dir, "credentials.txt")
        try:
            with open(cred_file, "w") as f:
                f.write(f"{phone}\n{email}\n{password}\n")
            self.status_label.text = "Credentials saved. Starting service..."
        except Exception as e:
            self.status_label.text = f"Error saving credentials: {e}"
            return

        # Request runtime permissions (RECEIVE_SMS, READ_SMS, INTERNET, READ_PHONE_STATE)
        try:
            perms = [
                Permission.RECEIVE_SMS,
                Permission.READ_SMS,
                Permission.INTERNET,
                Permission.READ_PHONE_STATE
            ]
            request_permissions(perms)
            print("Permissions requested:", perms)
        except Exception as e:
            print("Error requesting permissions:", e)

        # Start the background service that monitors SMS
        try:
            register_sms_receiver()  # Call the function from service.py
            self.status_label.text = "Background Service Started! App is working in the background."
        except Exception as e:
            self.status_label.text = f"Error starting service: {e}"


class SMSApp(App):
    def build(self):
        return MainUI()


if __name__ == "__main__":
    SMSApp().run()
