import npyscreen
from db import Database
from api_client import PlaidClient
from models import Account, BillItem

class LoginForm(npyscreen.ActionForm):
    def create(self):
        self.email = self.add(npyscreen.TitleText, name="Email:")
        self.password = self.add(npyscreen.TitlePassword, name="Password:")
        self.db = self.parentApp.db
    
    def on_ok(self):
        user_id = self.db.authenticate(self.email.value, self.password.value)
        if user_id:
            self.parentApp.user_id = user_id
            self.parentApp.setNextForm('PLAID')
        else:
            npyscreen.notify_confirm("Invalid credentials", title="Error")
    
    def on_cancel(self):
        self.parentApp.setNextForm(None)

class SignupForm(npyscreen.ActionForm):
    def create(self):
        self.email = self.add(npyscreen.TitleText, name="New Email:")
        self.password = self.add(npyscreen.TitlePassword, name="New Password:")
        self.db = self.parentApp.db
    
    def on_ok(self):
        try:
            self.db.create_user(self.email.value, self.password.value)
            npyscreen.notify_confirm("User created! Please log in.", title="Success")
            self.parentApp.setNextForm('LOGIN')
        except Exception as e:
            npyscreen.notify_confirm(str(e), title="Error")
    
    def on_cancel(self):
        self.parentApp.setNextForm('LOGIN')

class PlaidForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.FixedText, value="Connect to your bank via Fake Plaid:")
        self.client = PlaidClient()
    
    def on_ok(self):
        token = self.client.authenticate(self.parentApp.user_id)
        accounts = self.client.get_accounts()
        self.parentApp.accounts = [Account(**a) for a in accounts]
        self.parentApp.plaid_client = self.client
        self.parentApp.setNextForm('BILLS')

    def on_cancel(self):
        self.parentApp.setNextForm(None)

class BillsForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Your Accounts:")
        for i, acc in enumerate(self.parentApp.accounts):
            self.add(npyscreen.FixedText, value=f"{acc.name} ({acc.mask}): ${acc.balance}")
        self.add(npyscreen.ButtonPress, name="Sync Hospital Bills", when_pressed_function=self.sync_bills)

    def sync_bills(self):
        bills = self.parentApp.plaid_client.sync_hospital_bills()
        self.parentApp.bills = [BillItem(**b) for b in bills]
        self.parentApp.setNextForm('ITEMIZED')
        self.editing = False

class ItemizedForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.FixedText, value="Itemized Hospital Bills:")
        for b in self.parentApp.bills:
            self.add(npyscreen.FixedText, value=f"{b.service}: ${b.cost}")
        self.add(npyscreen.ButtonPress, name="Quit", when_pressed_function=self.exit)

    def exit(self):
        self.parentApp.setNextForm(None)
        self.editing = False

class MainMenuForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.FixedText, value="Welcome to the Medisave")
        self.login_btn = self.add(npyscreen.ButtonPress, name="Login", when_pressed_function=self.go_login)
        self.signup_btn = self.add(npyscreen.ButtonPress, name="Sign Up", when_pressed_function=self.go_signup)

    def go_login(self):
        self.parentApp.setNextForm('LOGIN')
        self.editing = False

    def go_signup(self):
        self.parentApp.setNextForm('SIGNUP')
        self.editing = False

class MedisaveApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.db = Database()
        self.db.connect()

        # Explicitly define all shared app variables here
        self.user_id = None
        self.accounts = []
        self.bills = []
        self.plaid_client = None

        # Register all forms
        self.addForm('LOGIN', LoginForm)
        self.addForm('SIGNUP', SignupForm)
        self.addForm('PLAID', PlaidForm)
        self.addForm('BILLS', BillsForm)
        self.addForm('ITEMIZED', ItemizedForm)

        # Initial menu (login/signup)
        self.addForm('MAIN', MainMenuForm)
        self.setNextForm('MAIN')

if __name__ == '__main__':
    MedisaveApp().run()
