import sqlite3
import random
import re

# Database Setup
conn = sqlite3.connect('bank_ginal.db')
cursor = conn.cursor()

# Create Tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    dob TEXT NOT NULL,
    city TEXT NOT NULL,
    password TEXT NOT NULL,
    balance REAL DEFAULT 2000,
    contact_number TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS login (
    account_number TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS "transaction" (
    id INTEGER PRIMARY KEY,
    account_number TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    balance_after REAL NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# Validation Functions
def validate_name(name):
    return len(name) > 0


def validate_account_number(account_number):
    return len(account_number) == 10 and account_number.isdigit()


def validate_password(password):
    return len(password) >= 8 and re.search(r'[A-Za-z]', password) and re.search(r'\d', password)


def validate_contact_number(contact_number):
    return len(contact_number) == 10 and contact_number.isdigit()


def validate_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)


def validate_initial_balance(balance):
    return balance >= 2000


def generate_account_number():
    return str(random.randint(1000000000, 9999999999))


# Function to add a user
def add_user():
    name = input("Enter your name: ")
    if not validate_name(name):
        print("Invalid name.")
        return

    account_number = generate_account_number()

    dob = input("Enter your date of birth (YYYY-MM-DD): ")
    city = input("Enter your city: ")
    password = input("Enter your password: ")
    if not validate_password(password):
        print("Invalid password. Must be at least 8 characters long, with letters and numbers.")
        return

    balance = float(input("Enter initial balance: "))
    if not validate_initial_balance(balance):
        print("Initial balance must be at least 2000.")
        return

    contact_number = input("Enter your contact number: ")
    if not validate_contact_number(contact_number):
        print("Invalid contact number.")
        return

    email = input("Enter your email: ")
    if not validate_email(email):
        print("Invalid email format.")
        return

    address = input("Enter your address: ")

    # Insert user into database
    cursor.execute('''
    INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, account_number, dob, city, password, balance, contact_number, email, address))
    conn.commit()

    # Insert login details
    cursor.execute('''
    INSERT INTO login (account_number, password)
    VALUES (?, ?)
    ''', (account_number, password))
    conn.commit()

    print(f"User added successfully with account number: {account_number}")


# Function to show user details
def show_user():
    account_number = input("Enter your account number: ")

    cursor.execute('''
    SELECT * FROM users WHERE account_number = ?
    ''', (account_number,))
    user = cursor.fetchone()

    if user:
        print(f"Name: {user[1]}")
        print(f"Account Number: {user[2]}")
        print(f"DOB: {user[3]}")
        print(f"City: {user[4]}")
        print(f"Balance: {user[6]}")
        print(f"Contact Number: {user[7]}")
        print(f"Email: {user[8]}")
        print(f"Address: {user[9]}")
    else:
        print("User not found.")


# Login functionality
def login():
    account_number = input("Enter account number: ")
    password = input("Enter password: ")

    cursor.execute('''
    SELECT * FROM login WHERE account_number = ? AND password = ?
    ''', (account_number, password))

    user = cursor.fetchone()

    if user:
        print("Login successful.")
        while True:
            print("\n1. Show Balance")
            print("2. Show Transaction")
            print("3. Credit Amount")
            print("4. Debit Amount")
            print("5. Transfer Amount")
            print("6. Active/Deactive Account")
            print("7. Change Password")
            print("8. Update Profile")
            print("9. Logout")
            choice = input("Enter your choice: ")

            if choice == '1':
                show_balance(account_number)
            elif choice == '2':
                show_transaction(account_number)
            elif choice == '3':
                credit_amount(account_number)
            elif choice == '4':
                debit_amount(account_number)
            elif choice == '5':
                transfer_amount(account_number)
            elif choice == '6':
                active_deactive_account(account_number)
            elif choice == '7':
                change_password(account_number)
            elif choice == '8':
                update_profile(account_number)
            elif choice == '9':
                print("Logging out.")
                break
            else:
                print("Invalid choice.")
    else:
        print("Invalid credentials.")


# Function to show balance
def show_balance(account_number):
    cursor.execute('''
    SELECT balance FROM users WHERE account_number = ?
    ''', (account_number,))
    balance = cursor.fetchone()
    print(f"Your balance is: {balance[0]}")


# Function to show transactions
def show_transaction(account_number):
    cursor.execute('''
    SELECT * FROM transaction WHERE account_number = ?
    ''', (account_number,))
    transactions = cursor.fetchall()

    if transactions:
        for transaction in transactions:
            print(f"{transaction[1]} - {transaction[2]} of {transaction[3]} on {transaction[4]}")
    else:
        print("No transactions found.")


# Function to credit amount
def credit_amount(account_number):
    amount = float(input("Enter amount to credit: "))
    cursor.execute('''
    SELECT balance FROM users WHERE account_number = ?
    ''', (account_number,))
    current_balance = cursor.fetchone()[0]

    new_balance = current_balance + amount
    cursor.execute('''
    UPDATE users SET balance = ? WHERE account_number = ?
    ''', (new_balance, account_number))
    cursor.execute('''
    INSERT INTO transaction (account_number, transaction_type, amount, balance_after)
    VALUES (?, ?, ?, ?)
    ''', (account_number, 'credit', amount, new_balance))
    conn.commit()

    print(f"Amount credited. New balance: {new_balance}")


# Function to debit amount
def debit_amount(account_number):
    amount = float(input("Enter amount to debit: "))
    cursor.execute('''
    SELECT balance FROM users WHERE account_number = ?
    ''', (account_number,))
    current_balance = cursor.fetchone()[0]

    if current_balance >= amount:
        new_balance = current_balance - amount
        cursor.execute('''
        UPDATE users SET balance = ? WHERE account_number = ?
        ''', (new_balance, account_number))
        cursor.execute('''
        INSERT INTO transaction (account_number, transaction_type, amount, balance_after)
        VALUES (?, ?, ?, ?)
        ''', (account_number, 'debit', amount, new_balance))
        conn.commit()

        print(f"Amount debited. New balance: {new_balance}")
    else:
        print("Insufficient balance.")


# Function to transfer amount
def transfer_amount(account_number):
    recipient_account = input("Enter recipient account number: ")
    amount = float(input("Enter amount to transfer: "))

    cursor.execute('''
    SELECT balance FROM users WHERE account_number = ?
    ''', (account_number,))
    sender_balance = cursor.fetchone()[0]

    if sender_balance >= amount:
        cursor.execute('''
        SELECT balance FROM users WHERE account_number = ?
        ''', (recipient_account,))
        recipient_balance = cursor.fetchone()[0]

        if recipient_balance is not None:
            new_sender_balance = sender_balance - amount
            new_recipient_balance = recipient_balance + amount

            cursor.execute('''
            UPDATE users SET balance = ? WHERE account_number = ?
            ''', (new_sender_balance, account_number))
            cursor.execute('''
            UPDATE users SET balance = ? WHERE account_number = ?
            ''', (new_recipient_balance, recipient_account))
            cursor.execute('''
            INSERT INTO transaction (account_number, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
            ''', (account_number, 'transfer', amount, new_sender_balance))
            cursor.execute('''
            INSERT INTO transaction (account_number, transaction_type, amount, balance_after)
            VALUES (?, ?, ?, ?)
            ''', (recipient_account, 'transfer', amount, new_recipient_balance))
            conn.commit()

            print(f"Amount transferred. New balance: {new_sender_balance}")
        else:
            print("Recipient account not found.")
    else:
        print("Insufficient balance.")


# Function to activate or deactivate account
# Function to deactivate an account
def active_deactive_account(account_number):
    cursor.execute('''SELECT balance FROM users WHERE account_number = ?''', (account_number,))
    user = cursor.fetchone()

    if user:
        cursor.execute('''UPDATE users SET status = 'deactivated' WHERE account_number = ?''', (account_number,))
        conn.commit()
        print("Account deactivated.")
    else:
        print("Account not found.")



# Function to change password
def change_password(account_number):
    new_password = input("Enter new password: ")
    if not validate_password(new_password):
        print("Invalid password. It must be at least 8 characters long, with letters and numbers.")
        return

    cursor.execute('''
    UPDATE login SET password = ? WHERE account_number = ?
    ''', (new_password, account_number))
    conn.commit()
    print("Password changed successfully.")


# Function to update profile
def update_profile(account_number):
    name = input("Enter new name: ")
    city = input("Enter new city: ")
    address = input("Enter new address: ")

    cursor.execute('''
    UPDATE users SET name = ?, city = ?, address = ? WHERE account_number = ?
    ''', (name, city, address, account_number))
    conn.commit()
    print("Profile updated successfully.")


# Main Menu
def main():
    while True:
        print("\n1. Add User")
        print("2. Show User")
        print("3. Login")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_user()
        elif choice == '2':
            show_user()
        elif choice == '3':
            login()
        elif choice == '4':
            print("Exiting.")
            break
        else:
            print("Invalid choice.")


if __name__ == "_main_":
    main()

# Close the connection
conn.close()