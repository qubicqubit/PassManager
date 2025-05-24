import customtkinter as ctk
from vault import get_all_passwords

class DashboardScreen:
    """
    GUI screen for the main password vault dashboard after successful login.
    """

    def __init__(self, app, master_password):
        self.app = app
        self.master_password = master_password

        # Clear existing widgets
        for widget in self.app.winfo_children():
            widget.destroy()

        # Welcome label
        self.title_label = ctk.CTkLabel(self.app, text="Welcome to Your Password Vault", font=("Arial", 20))
        self.title_label.pack(pady=30)

        # Load all vault entries
        self.entries = get_all_passwords(self.master_password)

        # Scrollable frame to list vault entries
        self.entries_frame = ctk.CTkScrollableFrame(self.app, width=500, height=350)
        self.entries_frame.pack(pady=10)
        # Add Password button
        self.add_password_button = ctk.CTkButton(self.app, text="Add Password", command=self.open_add_password_popup)
        self.add_password_button.pack(pady=15)

        # Refresh vault entries properly
        self.refresh_entries()

        # Logout button
        self.logout_button = ctk.CTkButton(self.app, text="Logout", command=self.logout)
        self.logout_button.pack(pady=20)
    
    def logout(self):
        from ui.login import LoginScreen
        LoginScreen(self.app)
    
    def open_add_password_popup(self):
        """
        Open a popup window for adding a new password entry.
        """
        #print("Add Password button clicked.")
        popup = ctk.CTkToplevel(self.app)
        popup.title("Add New Password")
        popup.geometry("400x650")
        popup.after(100, popup.grab_set)

        # Website field
        website_label = ctk.CTkLabel(popup, text="Website:")
        website_label.pack(pady=(20, 5))
        website_entry = ctk.CTkEntry(popup)
        website_entry.pack(pady=5)
        website_entry.focus()

        # Username field
        username_label = ctk.CTkLabel(popup, text="Username:")
        username_label.pack(pady=(20, 5))
        username_entry = ctk.CTkEntry(popup)
        username_entry.pack(pady=5)

        # Password length field
        length_label = ctk.CTkLabel(popup, text="Password Length (Default 12):")
        length_label.pack(pady=(20, 5))
        length_entry = ctk.CTkEntry(popup)
        length_entry.pack(pady=5)

        # Password field
        password_label = ctk.CTkLabel(popup, text="Password:")
        password_label.pack(pady=(20,5))
        password_entry = ctk.CTkEntry(popup)
        password_entry.pack(pady=5)

        # Generate password button
        def fill_generated_password():
            from ui.generator import generate_password
            
            try:
                length = int(length_entry.get())
                if length < 6:
                    length = 6 # Enforce minimum length
            except ValueError:
                length = 12 # Default if user enters non-numeric or empty

            new_password = generate_password(length=length)
            password_entry.delete(0, 'end')
            password_entry.insert(0, new_password)
        
        generate_btn = ctk.CTkButton(popup, text="Generate Password", command=fill_generated_password)
        generate_btn.pack(pady=(5, 20))

        # Notes field
        notes_label = ctk.CTkLabel(popup, text="Notes (optional):")
        notes_label.pack(pady=(20,5))
        notes_entry = ctk.CTkEntry(popup)
        notes_entry.pack(pady=5)


        def save_password():
            """
            Validate inputs and save the new password entry into vault.
            """
            website = website_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            notes = notes_entry.get()

            if not website or not username or not password:
                status_label.configure(text="Website, Username and Password are required.", text_color="red")
                return
            
            from vault import add_password, entry_exists

            if entry_exists(website, username):
                status_label.configure(text="This entry already exists.", text_color="orange")
                return
            
            # Weak password detection
            weak_patterns = ['123','password','qwerty','asdf','zxcv','abc']
            if len(password) < 8 or any(p in password.lower() for p in weak_patterns):
                status_label.configure(text="Password is weak, Use a stronger one.", text_color="orange")
                return
            
            add_password(
                website=website,
                username=username,
                plain_password=password,
                notes=notes,
                master_password=self.master_password
            )

            # Show success message
            status_label.configure(text="Password saved successfully.", text_color="green")

            # Disable save button to prevent re-clicking
            save_button.configure(state="disabled")
            
            # Refresh dashboard list
            self.refresh_entries()

            # Close popup after short delay
            popup.after(1000, popup.destroy)
        
        # Status label
        status_label = ctk.CTkLabel(popup, text="", text_color="gray", wraplength=300, justify="center")
        status_label.pack(pady=(10, 0))

        # Save button
        save_button = ctk.CTkButton(popup, text="save", command=save_password)
        save_button.pack(pady=20)

    def open_edit_password_popup(self, entry_id):
        """
        Open a popup window to edit an existing password entry.
        """
        # Find the entry by ID
        entry_to_edit = next((e for e in self.entries if e['id'] == entry_id), None)
        if not entry_to_edit:
            print(f"Error: Entry with ID {entry_id} not found.")
            return
        
        popup = ctk.CTkToplevel(self.app)
        popup.title("Edit Password")
        popup.geometry("400x650")
        popup.after(100, popup.grab_set)

        # Pre-fill fields
        website_label = ctk.CTkLabel(popup, text="Website:")
        website_label.pack(pady=(20, 5))
        website_entry = ctk.CTkEntry(popup)
        website_entry.insert(0, entry_to_edit['website'])
        website_entry.pack(pady=5)

        username_label = ctk.CTkLabel(popup, text="Username:")
        username_label.pack(pady=(20, 5))
        username_entry = ctk.CTkEntry(popup)
        username_entry.insert(0, entry_to_edit['username'])
        username_entry.pack(pady=5)

        password_label = ctk.CTkLabel(popup, text="Password:")
        password_label.pack(pady=(20, 5))
        password_entry = ctk.CTkEntry(popup)
        password_entry.insert(0, entry_to_edit['password'])
        password_entry.pack(pady=5)

        notes_label = ctk.CTkLabel(popup, text="Notes (optional):")
        notes_label.pack(pady=(20, 5))
        notes_entry = ctk.CTkEntry(popup)
        notes_entry.insert(0, entry_to_edit['notes'])
        notes_entry.pack(pady=5)

        # Save Changes button
        def save_changes():
            from vault import update_password

            new_website = website_entry.get()
            new_username = username_entry.get()
            new_password = password_entry.get()
            new_notes = notes_entry.get()

            update_password(
                entry_id=entry_id,
                new_website=new_website,
                new_username=new_username,
                new_plain_password=new_password,
                new_notes=new_notes,
                master_password=self.master_password
            )

            self.refresh_entries()

            popup.destroy()

        save_button = ctk.CTkButton(popup, text="Save Changes", command=save_changes)
        save_button.pack(pady=20)
        
    def create_entry_frame(self, entry):
        """
        Create a single entry block in the UI from a vauilt record.
        """
        entry_frame = ctk.CTkFrame(self.entries_frame)
        entry_frame.pack(pady=5, padx=10, fill="x")
        
        separator = ctk.CTkLabel(self.entries_frame, text="─" * 100, text_color="gray")
        separator.pack(pady=2)

        website_label = ctk.CTkLabel(entry_frame, text=f"Website: {entry['website']}")
        website_label.pack(anchor="w", padx=10)

        username_label = ctk.CTkLabel(entry_frame, text=f"Username: {entry['username']}")
        username_label.pack(anchor="w", padx=10)

        # Frame to hold password and reveal button
        password_frame = ctk.CTkFrame(entry_frame)
        password_frame.pack(fill="x", padx=10, pady=5)

        # Initially masked password
        masked_password = "•" * len(entry['password'])

        is_visible = [False]

        password_label = ctk.CTkLabel(password_frame, text=f"Password: {masked_password}")
        password_label.pack(side="left", padx=(0, 10))

        # Status label for feedback messages
        status_label = ctk.CTkLabel(password_frame, text="", text_color="gray", font=("Arial", 12))
        status_label.pack(pady=2, anchor="w")

        # Copy button (initially disabled)
        copy_btn = ctk.CTkButton(password_frame, text="Copy", width=80, state="disabled")
        copy_btn.pack(side="right", padx=5)
        def toggle_visibility():
                if is_visible[0]:
                    password_label.configure(text=f"Password: {'•' * len(entry['password'])}")
                    reveal_btn.configure(text="Reveal")
                    copy_btn.configure(state="disabled")
                else:
                    password_label.configure(text=f"Password: {entry['password']}")
                    reveal_btn.configure(text="Hide")
                    copy_btn.configure(state="normal")
                is_visible[0] = not is_visible[0]

        reveal_btn = ctk.CTkButton(
                password_frame,
                text="Reveal",
                width=80,
                command=toggle_visibility
        )
        reveal_btn.pack(side="right")

        def copy_to_clipboard():
                self.app.clipboard_clear()
                self.app.clipboard_append(entry['password'])
                self.app.update()
                status_label.configure(text="Copied to clipboard.", text_color="green")
                status_label.after(1500, lambda: status_label.configure(text=""))

        copy_btn.configure(command=copy_to_clipboard)

        # Frame for action buttons (Edit + Delete)
        actions_frame = ctk.CTkFrame(entry_frame)
        actions_frame.pack(fill="x", padx=10, pady=5)

        # Edit button
        edit_btn = ctk.CTkButton(
                actions_frame,
                text="Edit",
                width=80,
                command=lambda: self.open_edit_password_popup(entry['id'])
            )
        edit_btn.pack(side="left", padx=5)

            # Delete Button
        delete_btn = ctk.CTkButton(
                actions_frame,
                text="Delete",
                width=80,
                command=lambda: self.delete_password(entry['id'])
            )
        delete_btn.pack(side="left", padx=5)

    def refresh_entries(self):
        """
        Refresh the vault entries displayed in the dashboard.
        Reload from the database and rebuild the scrollable frame.
        """
        # Clear all widgets inside the entries_frame
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        # Reload entries from database
        from vault import get_all_passwords
        self.entries = get_all_passwords(self.master_password)

        # Recreate all entry frames
        for entry in self.entries:
            self.create_entry_frame(entry)

        if not self.entries:
            empty_label = ctk.CTkLabel(self.entries_frame, text="No passwords saved yet.")
            empty_label.pack(pady=10)

    def delete_password(self, entry_id):
        """
        Delete a password entry by its ID and refresh the vault view.
        """
        from vault import delete_password

        delete_password(entry_id)

        self.refresh_entries()        