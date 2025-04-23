import npyscreen
import os
import json
import uuid
from models import Account, BillItem, Transaction
import openai
import textwrap
from dotenv import load_dotenv

# === Data files ===
BASE_DIR          = os.path.dirname(__file__)
DATA_DIR          = os.path.join(BASE_DIR, 'data')
USERS_FILE        = os.path.join(DATA_DIR, 'users.json')
PLAID_USERS_FILE  = os.path.join(DATA_DIR, 'plaid_users.json')
ACCOUNTS_FILE     = os.path.join(DATA_DIR, 'accounts.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
BILLS_FILE        = os.path.join(DATA_DIR, 'bills.json')

class MedisaveApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # ensure data directory & files exist
        os.makedirs(DATA_DIR, exist_ok=True)
        for path, default in [
            (USERS_FILE,    []),
            (ACCOUNTS_FILE, []),
            (BILLS_FILE,    []),
        ]:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(default, f, indent=2)

        # shared state
        self.user_id  = None
        self.linked_acc_ids = []
        self.linked_txs_ids = []
        self.accounts = []
        self.transactions = []
        self.bills    = []
        self.ai = ""

        # register screens
        self.addForm('MAIN',     MainMenuForm)
        self.addForm('SIGNUP',   SignupForm)
        self.addForm('LOGIN',    LoginForm)
        self.addForm('ITEMIZED', ItemizedForm)
        self.addForm('PLAID',    PlaidForm)
        self.addForm('BANKINFO', BankInfoForm)
        self.addForm('AI', AIForm)

        # go
        self.setNextForm('MAIN')

    def load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

# === Screens =========================================================

class MainMenuForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Welcome to Medisave", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.add(npyscreen.ButtonPress, name="Login",   when_pressed_function=self.go_login)
        self.add(npyscreen.ButtonPress, name="Sign Up", when_pressed_function=self.go_signup)
        self.add(npyscreen.ButtonPress, name="Exit", when_pressed_function=self.go_exit)

    def go_login(self):
        self.parentApp.setNextForm('LOGIN');  self.editing=False
    def go_signup(self):
        self.parentApp.setNextForm('SIGNUP'); self.editing=False
    def go_exit(self):
        self.parentApp.setNextForm(None); self.editing=False

class SignupForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Medisave - Create Account", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.email = self.add(npyscreen.TitleText,     name="Email:")
        self.password = self.add(npyscreen.TitlePassword, name="Password:")

        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress, name="Sign Up",   when_pressed_function=self.go_signup)
        self.add(npyscreen.ButtonPress, name="Back", when_pressed_function=self.go_back)

    def go_signup(self):
        users = self.parentApp.load_json(USERS_FILE)
        if any(u['email']==self.email.value for u in users):
            npyscreen.notify_confirm("That email is taken.", title="Error")
        else:
            users.append({
                'id':       str(uuid.uuid4()),
                'email': self.email.value,
                'password': self.password.value,
                'linkedAccountIDs': [],
                'linkedTransactionIDs': []
            })
            self.parentApp.save_json(USERS_FILE, users)
            npyscreen.notify_confirm("Account created! Please log in.", title="Success")
            self.parentApp.setNextForm('LOGIN')
        self.editing=False

    def go_back(self):
        self.parentApp.setNextForm('MAIN'); self.editing=False

class LoginForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Medisave - Log In", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.email = self.add(npyscreen.TitleText,        name="Email   :", begin_entry_at=12)
        self.password = self.add(npyscreen.TitlePassword, name="Password:", begin_entry_at=12)

        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress, name="Login",   when_pressed_function=self.go_login)
        self.add(npyscreen.ButtonPress, name="Back", when_pressed_function=self.go_back)

    def go_login(self):
        users = self.parentApp.load_json(USERS_FILE)
        match = next((u for u in users
                      if u['email']==self.email.value
                      and u['password']==self.password.value), None)
        if not match:
            npyscreen.notify_confirm("Invalid credentials.", title="Error")
        else:
            self.parentApp.user_id = match['id']
            self.parentApp.linked_acc_ids = match['linkedAccountIDs']
            self.parentApp.linked_txs_ids = match['linkedTransactionIDs']
            # load any saved hospital bills
            all_bills = self.parentApp.load_json(BILLS_FILE)
            self.parentApp.bills = [
                BillItem(b['service'], b['cost']) for b in all_bills
                if b.get('user_id') == self.parentApp.user_id
            ]
            # load accounts data from JSON
            all_acc = self.parentApp.load_json(ACCOUNTS_FILE)
            usr_acc = [a for a in all_acc if a.get('account_id') in self.parentApp.linked_acc_ids]
            self.parentApp.accounts = [
                Account(a['name'], a['mask'], a['balance']) for a in usr_acc
            ]
            # load transactions data from JSON
            all_txs = self.parentApp.load_json(TRANSACTIONS_FILE)
            usr_txs = [t for t in all_txs if t.get('transaction_id') in self.parentApp.linked_txs_ids]
            self.parentApp.transactions = [
                Transaction(t['transaction_id'], t['account_id'], t['date'], t['amount'],
                            t['merchant_name'], t['category'], t['running_balance'],
                            t['pending'], t['description']) for t in usr_txs
            ]
            self.parentApp.setNextForm('ITEMIZED')
        self.editing=False

    def go_back(self):
        self.parentApp.setNextForm('MAIN'); self.editing=False

class ItemizedForm(npyscreen.FormBaseNew):
    def create(self):
        pass

    def beforeEditing(self):
        # Clear existing widgets
        self._widgets__[:] = []
        self._clear_all_widgets()

        self.add(npyscreen.FixedText, value="Medisave - Itemized Bill", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.add(npyscreen.FixedText, value="Your Hospital Bills:", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)
        if self.parentApp.bills:
            max_len = max(len(b.service) for b in self.parentApp.bills)
            for b in self.parentApp.bills:
                self.add(npyscreen.FixedText,
                         value=f"{b.service:<{max_len}}: ${b.cost:.2f}", editable=False)
        else:
            self.add(npyscreen.FixedText, value="(none found)", editable=False)

        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress,
                 name="My Bank Info",
                 when_pressed_function=self.bank_info)
        self.add(npyscreen.ButtonPress,
                 name="Sync Bank Accounts",
                 when_pressed_function=self.sync_accounts)
        self.add(npyscreen.MiniButtonPress,
                 name="Send Bill Adjustment Request with Personal Bank Info",
                 when_pressed_function=self.ai)
        self.add(npyscreen.ButtonPress,
                 name="Quit",
                 when_pressed_function=self.exit_app)

    def ai(self):
        self.parentApp.setNextForm('AI')
        self.editing=False

    def bank_info(self):
        self.parentApp.setNextForm('BANKINFO')
        self.editing=False

    def sync_accounts(self):
        self.parentApp.setNextForm('PLAID')
        self.editing=False

    def exit_app(self):
        self.parentApp.setNextForm(None)
        self.editing=False

class PlaidForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Medisave - Link Bank Info with Plaid", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.username = self.add(npyscreen.TitleText,     name="Bank Username:", begin_entry_at=18)
        self.password = self.add(npyscreen.TitlePassword, name="Bank Password:", begin_entry_at=18)

        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress, name="Submit",   when_pressed_function=self.go_submit)
        self.add(npyscreen.ButtonPress, name="Back", when_pressed_function=self.go_back)

    def go_submit(self):
        users = self.parentApp.load_json(PLAID_USERS_FILE)
        match = next((u for u in users
                      if u['username']==self.username.value
                      and u['password']==self.password.value), None)
        if not match:
            npyscreen.notify_confirm("Account not found.", title="Error")
        else:
            # load accounts data from JSON
            all_acc = self.parentApp.load_json(ACCOUNTS_FILE)
            usr_acc = [a for a in all_acc if (a.get('user_id') == self.parentApp.user_id and a.get('account_id') not in self.parentApp.linked_acc_ids)]
            # instantiate Account(name, mask, balance)
            self.parentApp.accounts.extend([
                Account(a['name'], a['mask'], a['balance']) for a in usr_acc
            ])
            self.parentApp.linked_acc_ids.extend([a['account_id'] for a in usr_acc])

            # load transactions data from JSON
            all_txs = self.parentApp.load_json(TRANSACTIONS_FILE)
            usr_txs = [t for t in all_txs if (t.get('user_id') == self.parentApp.user_id and t.get('transaction_id') not in self.parentApp.linked_txs_ids)]
            # instantiate Transaction(transaction_id, account_id, date, amount, 
            #                           merchant_name, category, running_balance,
            #                           pending, description)
            self.parentApp.transactions.extend([
                Transaction(t['transaction_id'], t['account_id'], t['date'], t['amount'],
                            t['merchant_name'], t['category'], t['running_balance'],
                            t['pending'], t['description']) for t in usr_txs
            ])
            self.parentApp.linked_txs_ids.extend([t['transaction_id'] for t in usr_txs])
            # TODO: Update the users.json file with any new linked account or transaction IDs

            self.parentApp.setNextForm('BANKINFO')
        self.editing=False

    def go_back(self):
        self.parentApp.setNextForm('ITEMIZED'); self.editing=False

class BankInfoForm(npyscreen.FormBaseNew):
    def create(self):
        pass

    def beforeEditing(self):
        # Clear existing widgets
        self._widgets__[:] = []
        self._clear_all_widgets()

        self.add(npyscreen.FixedText, value="Medisave - My Bank Info", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.add(npyscreen.FixedText, value="Your Linked Accounts:", editable=False)
        if self.parentApp.accounts:
            max_len = max(len(f"{acc.name} ({acc.mask})") for acc in self.parentApp.accounts)
            for acc in self.parentApp.accounts:
                header=f"{acc.name} ({acc.mask})"
                self.add(npyscreen.FixedText,
                         value=f"{header:<{max_len}}: ${acc.balance:.2f}", editable=False)
        else:
            self.add(npyscreen.FixedText, value="(no accounts linked)", editable=False)

        self.add(npyscreen.FixedText, value="", editable=False)

        self.add(npyscreen.FixedText, value="Your Recent Transactions:", editable=False)
        if self.parentApp.transactions:
            max_len = max(len(f"{tx.merchant_name} ({tx.date})") for tx in self.parentApp.transactions)
            for tx in self.parentApp.transactions:
                header=f"{tx.merchant_name} ({tx.date})"
                self.add(npyscreen.FixedText,
                         value=f"{header:<{max_len}}: ${tx.amount:.2f}", editable=False)
        else:
            self.add(npyscreen.FixedText, value="(no transactions)", editable=False)

        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress,
                 name="Back to Bills",
                 when_pressed_function=self.back_to_itemized)

    def back_to_itemized(self):
        self.parentApp.setNextForm('ITEMIZED')
        self.editing=False

class AIForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Medisave - My Bank Info", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)

        self.add(npyscreen.FixedText, value="Email for Hospital:", editable=False)
        self.email_display = self.add(npyscreen.Pager,
                              value=self.parentApp.ai or [],
                              max_height=14,
                              rely=5,  # adjust as needed
                              scroll_exit=True,
                              color='STANDOUT')
        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.FixedText, value="", editable=False)
        self.add(npyscreen.ButtonPress,
                 name="Generate AI Email",
                 when_pressed_function=self.generate_ai_email)
        self.add(npyscreen.ButtonPress,
                 name="Back to Bills",
                 when_pressed_function=self.back_to_itemized)

    def generate_ai_email(self):
        load_dotenv("./.env")
        api_key = os.getenv("api-key")
        if not api_key:
            npyscreen.notify_confirm("API key not found in .env", title="Error")
            return

        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        prompt = f"""Act as a professional negotiator writing a formal email to the hospital billing
                    department to come to a settlement that is able to be handled by the user. The
                    goal is that the user is able to pay off their debt to the hospital, and isn't
                    left to debt collectors. I will give you data on the users bank accounts, their
                    recent transactions, and the bills from the hospital they face. 
                    Here is the account data:
                    {str(self.parentApp.accounts)}
                    Here is the transactions data:
                    {str(self.parentApp.transactions)}
                    Here is the hospital bills data:
                    {str(self.parentApp.bills)}
                    
                    RESPOND IN PLAIN TEXT, DO NOT RESPOND IN MARKDOWN. ONLY RESPOND WITH THE EMAIL.
                    """

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=512,
            )
            email = response.choices[0].message.content or ""
            with open("debug.log", 'w') as out:
                out.write(f"AI response: {email}")
            # after you receive `email = response.choices[0].message.content`
            # 1) wrap paragraphs to widget width:
            widget_w = self.email_display.width - 2
            wrapped = []
            for para in email.split("\n"):
                if not para.strip():
                    wrapped.append("")
                else:
                    wrapped.extend(textwrap.wrap(para, widget_w))

            # 2) update the Pager’s content and height (optional auto-resize):
            self.email_display.values = wrapped

            # 3) redraw
            self.email_display.display()
        except Exception as e:
            npyscreen.notify_confirm(f"Error generating email:\n{e}", title="Error")

    def back_to_itemized(self):
        self.parentApp.setNextForm('ITEMIZED')
        self.editing = False

# ─── Launch ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    MedisaveApp().run()
