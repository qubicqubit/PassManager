import customtkinter as ctk
from auth import is_master_set
from ui.login import FirstTimeSetupScreen, LoginScreen
from vault import initialize_database


# Configure the global appearance (dark mode and blue theme)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Initialize the main application window
app = ctk.CTk()
app.geometry("500x600")
app.title("Local Password Manager")

initialize_database()

# Launch correct screen
if is_master_set():
    LoginScreen(app)
else:
    FirstTimeSetupScreen(app)

# Start the main application event loop
app.mainloop()
