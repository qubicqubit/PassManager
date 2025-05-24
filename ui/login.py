import customtkinter as ctk
#import os
from auth import is_master_set, set_master_password, verify_master_password
from ui.dashboard import DashboardScreen

class FirstTimeSetupScreen(ctk.CTk):
    """
    GUI screen for first-time setup to create a master password.
    """

    def __init__(self, app):
        self.app = app

        # Clear any existing widgets from the app windows
        for widget in self.app.winfo_children():
            widget.destroy()

        # Title label
        self.title_label = ctk.CTkLabel(self.app, text="Create Master Password", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Master password entry
        self.password_entry = ctk.CTkEntry(self.app, placeholder_text="Master Password", show="*")
        self.password_entry.pack(pady=10)

        # Confirm password entry
        self.confirm_entry = ctk.CTkEntry(self.app, placeholder_text="Confirm Password", show="*")
        self.confirm_entry.pack(pady=10)

        # Status label (for errors/success messages)
        self.status_label = ctk.CTkLabel(self.app, text="")
        self.status_label.pack(pady=5)

        # Save button
        self.save_button = ctk.CTkButton(self.app, text="Save Master Password", command=self.save_master_password)
        self.save_button.pack(pady=20)

    def save_master_password(self):
        """
        Validate and save the new master password.
        """
        pw = self.password_entry.get()
        confirm_pw = self.confirm_entry.get()

        if pw != confirm_pw:
            self.status_label.configure(text="Passwords do not match.", text_color="red")
        elif len(pw) < 6:
            self.status_label.configure(text="Password too short (min 6 chars).", text_color="orange")
        else:
            set_master_password(pw)
            self.status_label.configure(text="Master Password Set Successfully.", text_color="green")
            self.app.after(1000, lambda: LoginScreen(self.app))

class LoginScreen:
    """
    GUI screen for user login using existing master password.
    """
    def __init__(self, app):
        self.app = app

        # Clear any existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()
        
        # Title label
        self.title_label = ctk.CTkLabel(self.app, text="Enter Master Password", font=("Arial", 18))
        self.title_label.pack(pady=20)

        # Password entry
        self.password_entry = ctk.CTkEntry(self.app, placeholder_text="Master Password", show="*")
        self.password_entry.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self.app, text="")
        self.status_label.pack(pady=5)

        # Login button
        self.login_button = ctk.CTkButton(self.app, text="Login", command=self.attempt_login)
        self.login_button.pack(pady=20)

    def attempt_login(self):
        """
        Verify the entered master password.
        """
        pw = self.password_entry.get()

        if verify_master_password(pw):
            self.status_label.configure(text="Login Successful.", text_color="green")
            self.app.after(1000, lambda: DashboardScreen(self.app, pw))
        else:
            self.status_label.configure(text="Incorrect password.", text_color="red")