import flet as ft
import json
from datetime import datetime


def load_users():
    with open('users.json', 'r') as file:
        data = json.load(file)
    return data.get('users', [])

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)

def load_verifications():
    with open('verif.json', 'r') as file:
        data = json.load(file)
    if isinstance(data, dict) and 'verifications' in data:
        return data['verifications']
    return []

def save_verification(user):
    verifications = load_verifications()
    verifications.append(user)
    with open('verif.json', 'w') as file:
        json.dump({"verifications": verifications}, file, indent=4)

def delete_verification(username):
    verifications = load_verifications()
    verifications = [v for v in verifications if v['username'] != username]
    with open('verif.json', 'w') as file:
        json.dump({"verifications": verifications}, file, indent=4)

def load_history():
    with open('riwayat.json', 'r') as file:
        data = json.load(file)
    return data.get('history', [])

def save_history(entry):
    history = load_history()
    history.append(entry)
    with open('riwayat.json', 'w') as file:
        json.dump({"history": history}, file, indent=4)

def login(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def transfer(sender, receiver_username, amount):
    users = load_users()
    sender_user = next((user for user in users if user['username'] == sender['username']), None)
    receiver_user = next((user for user in users if user['username'] == receiver_username), None)
    if receiver_user and sender_user and sender_user['balance'] >= amount:
        sender_user['balance'] -= amount
        receiver_user['balance'] += amount
        save_users(users)
        save_history({
            "sender": sender['username'],
            "receiver": receiver_username,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True
    return False

def add_balance(username, amount):
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    if user:
        user['balance'] += amount
        save_users(users)
        return True
    return False

def main(page: ft.Page):
    page.title = "Login"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.update()

    username_entry = ft.TextField(label="Username", width=300)
    password_entry = ft.TextField(label="Password", password=True, width=300)
    login_button = ft.ElevatedButton(text="Login", on_click=lambda e: check_login(page, username_entry, password_entry))
    register_button = ft.ElevatedButton(text="Register", on_click=lambda e: open_register_window(page))

    page.controls.clear()
    page.add(username_entry, password_entry, login_button, register_button)
    page.update()

def check_login(page, username_entry, password_entry):
    user = login(username_entry.value, password_entry.value)
    if user:
        if not user.get("verified", False):
            show_error_dialog(page, "Login gagal", "Akun Anda belum diverifikasi oleh admin.")
        elif user["role"] == "admin":
            page.controls.clear()
            page.update()
            open_admin_dashboard(page, user)
        else:
            page.controls.clear()
            page.update()
            open_transfer_window(page, user)
    else:
        show_error_dialog(page, "Login gagal", "Username atau password salah.")

def open_transfer_window(page, user):
    page.title = "Transfer"
    balance_label = ft.Text(f"Saldo kamu: {user['balance']}", size=20, key="balance_label")
    receiver_entry = ft.TextField(label="Username Penerima", width=300)
    amount_entry = ft.TextField(label="Jumlah Transfer", width=300)
    transfer_button = ft.ElevatedButton(text="Transfer", on_click=lambda e: make_transfer(page, user, receiver_entry, amount_entry))
    logout_button = ft.ElevatedButton(text="Logout", on_click=lambda e: logout(page))

    page.controls.clear()
    page.add(balance_label, receiver_entry, amount_entry, transfer_button, logout_button)
    page.update()

def make_transfer(page, user, receiver_entry, amount_entry):
    if transfer(user, receiver_entry.value, int(amount_entry.value)):
        show_success_dialog(page, "Transfer berhasil", "Transfer berhasil dilakukan!", lambda e: open_transfer_window(page, user))
        receiver_entry.value = ""
        amount_entry.value = ""
        balance_label = page.controls[0]  # Assuming balance_label is the first control
        balance_label.value = f"Saldo kamu: {user['balance']}"
        page.update()
    else:
        show_error_dialog(page, "Transfer gagal", "Username penerima tidak ditemukan atau saldo tidak cukup.")

def logout(page):
    main(page)
    page.update()

def open_register_window(page):
    page.title = "Register"
    username_entry = ft.TextField(label="Username", width=300)
    password_entry = ft.TextField(label="Password", password=True, width=300)
    confirm_password_entry = ft.TextField(label="Confirm Password", password=True, width=300)
    register_button = ft.ElevatedButton(text="Register", on_click=lambda e: register_user(page, username_entry, password_entry, confirm_password_entry))

    page.controls.clear()
    page.add(username_entry, password_entry, confirm_password_entry, register_button)
    page.update()

def register_user(page, username_entry, password_entry, confirm_password_entry):
    if password_entry.value != confirm_password_entry.value:
        show_error_dialog(page, "Registration gagal", "Password dan konfirmasi password tidak cocok.")
        return

    users = load_users()
    if any(user['username'] == username_entry.value for user in users):
        show_error_dialog(page, "Registration gagal", "Username sudah terdaftar.")
        return

    new_user = {
        "username": username_entry.value,
        "password": password_entry.value,
        "balance": 0,
        "role": "user",
        "verified": False
    }

    save_verification(new_user)
    show_success_dialog(page, "Registration berhasil", "Registrasi berhasil. Tunggu verifikasi oleh admin.", lambda e: main(page))

def open_admin_dashboard(page, admin_user):
    page.title = "Admin Dashboard"
    verifications = load_verifications()
    verification_list = [ft.Text(f"Username: {user['username']}, Verifikasi: {'Ya' if user['verified'] else 'Tidak'}") for user in verifications]
    approve_buttons = [ft.ElevatedButton(text="Approve", on_click=lambda e, user=user: approve_user(page, user)) for user in verifications if not user['verified']]
    add_balance_button = ft.ElevatedButton(text="Tambah Saldo", on_click=lambda e: open_add_balance_window(page))
    logout_button = ft.ElevatedButton(text="Logout", on_click=lambda e: logout(page))

    page.controls.clear()
    page.add(*verification_list, *approve_buttons, add_balance_button, logout_button)
    page.update()

def open_add_balance_window(page):
    page.title = "Tambah Saldo"
    username_entry = ft.TextField(label="Username", width=300)
    amount_entry = ft.TextField(label="Jumlah Saldo", width=300)
    add_balance_button = ft.ElevatedButton(text="Tambah", on_click=lambda e: add_balance_action(page, username_entry, amount_entry))
    back_button = ft.ElevatedButton(text="Kembali", on_click=lambda e: open_admin_dashboard(page, None))

    page.controls.clear()
    page.add(username_entry, amount_entry, add_balance_button, back_button)
    page.update()

def add_balance_action(page, username_entry, amount_entry):
    if add_balance(username_entry.value, int(amount_entry.value)):
        show_success_dialog(page, "Berhasil", "Saldo berhasil ditambahkan.", lambda e: open_admin_dashboard(page, None))
    else:
        show_error_dialog(page, "Gagal", "Username tidak ditemukan.")

def approve_user(page, user):
    users = load_users()
    users.append(user)
    save_users(users)
    delete_verification(user['username'])
    show_success_dialog(page, "User disetujui", f"User {user['username']} telah disetujui.", lambda e: open_admin_dashboard(page, None))

def show_error_dialog(page, title, content):
    def close_dialog(e):
        page.overlay.remove(error_dialog)
        page.update()
    
    error_dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[ft.ElevatedButton(text="Ok", on_click=close_dialog)],
    )
    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()

def show_success_dialog(page, title, content, on_close=None):
    def close_dialog(e):
        page.overlay.remove(success_dialog)
        page.update()
        if on_close:
            on_close(e)
    
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
