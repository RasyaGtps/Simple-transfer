import flet as ft
import json
from datetime import datetime
import os

def load_users():
    with open('users.json', 'r') as file:
        data = json.load(file)
    return data['users']

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)

def login(username, password, users):
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def transfer(sender, receiver_username, amount, users):
    receiver = next((user for user in users if user['username'] == receiver_username), None)
    if receiver:
        sender['balance'] -= amount
        receiver['balance'] += amount
        return True
    return False

def log_transfer(sender_username, receiver_username, amount):
    transfer_record = {
        "sender": sender_username,
        "receiver": receiver_username,
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists('riwayat.json') and os.path.getsize('riwayat.json') > 0:
        try:
            with open('riwayat.json', 'r') as file:
                history = json.load(file)
        except json.JSONDecodeError:
            history = []
    else:
        history = []

    history.append(transfer_record)

    with open('riwayat.json', 'w') as file:
        json.dump(history, file, indent=4)

def main(page: ft.Page):
    page.title = "Login"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.update()

    users = load_users()

    username_entry = ft.TextField(label="Username", width=300)
    password_entry = ft.TextField(label="Password", password=True, width=300)
    login_button = ft.ElevatedButton(text="Login", on_click=lambda e: check_login(page, username_entry, password_entry, users))

    page.add(username_entry, password_entry, login_button)

def check_login(page, username_entry, password_entry, users):
    user = login(username_entry.value, password_entry.value, users)
    if user:
        page.controls.clear()
        page.update()
        open_transfer_window(page, user, users)
    else:
        show_error_dialog(page, "Login gagal", "Username atau password salah.")

def open_transfer_window(page, user, users):
    page.title = "Transfer"
    balance_label = ft.Text(f"Saldo kamu: {user['balance']}", size=20, key="balance_label")
    receiver_entry = ft.TextField(label="Username Penerima", width=300)
    amount_entry = ft.TextField(label="Jumlah Transfer", width=300)
    transfer_button = ft.ElevatedButton(text="Transfer", on_click=lambda e: make_transfer(page, user, receiver_entry, amount_entry, users))
    logout_button = ft.ElevatedButton(text="Logout", on_click=lambda e: logout(page))

    page.add(balance_label, receiver_entry, amount_entry, transfer_button, logout_button)
    page.update()

def make_transfer(page, user, receiver_entry, amount_entry, users):
    if transfer(user, receiver_entry.value, int(amount_entry.value), users):
        show_success_dialog(page, "Transfer berhasil", "Transfer berhasil dilakukan!")
        save_users(users)
        log_transfer(user['username'], receiver_entry.value, int(amount_entry.value))
        receiver_entry.value = ""
        amount_entry.value = ""
        balance_label = page.controls[0]  
        balance_label.value = f"Saldo kamu: {user['balance']}"
        page.update()
    else:
        show_error_dialog(page, "Transfer gagal", "Username penerima tidak ditemukan atau saldo tidak cukup.")

def logout(page):
    page.controls.clear()
    main(page)
    page.update()

def show_error_dialog(page, title, content):
    def close_dialog(e):
        if page.dialog:
            page.dialog.open = False
            page.update()
    
    error_dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[ft.ElevatedButton(text="Ok", on_click=close_dialog)],
    )
    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()

def show_success_dialog(page, title, content):
    def close_dialog(e):
        if page.dialog:
            page.dialog.open = False
            page.update()
            open_transfer_window(page, user, users)
            receiver_entry.value = ""
            amount_entry.value = ""
            receiver_entry.focus() 
    
    success_dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[ft.ElevatedButton(text="Ok", on_click=close_dialog)],
    )
    page.overlay.append(success_dialog)
    success_dialog.open = True
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
