import time

import customtkinter
from customtkinter import *
import threading


customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme('dark-blue')


# ==============GUI design ===============
class Graphical_window(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Automatic bets")
        self.geometry("300x400")
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(pady=10, padx=10, fill="both", expand="True")

        # ====== Variables ======
        self.running = False

        def stop():
            self.running = False
            print("stop pressed")

        def start():
            self.running = True
            from functii import SiteA
            F = SiteA()
            print("Start")
            # F.extract_predictions()
            while self.running:
                F.main_loop(self.entry_username.get(), self.entry_password.get(), self.entry_min.get(), self.entry_max.get())

        def button_starter():
            print("startstart\n\n")
            t = threading.Thread(target=start)
            print("=================Incep Programul=============\n\n")
            t.start()

        # ====== Credentials area ========
        self.label_credentials = customtkinter.CTkLabel(self.frame, text="Enter your credentials:", text_color="green")
        self.label_credentials.grid(row=0, sticky=W, padx=10, columnspan=8)
        self.entry_username = customtkinter.CTkEntry(self.frame, width=250, placeholder_text="Enter username")
        self.entry_username.grid(row=1, column=0, padx=10, columnspan=8)
        self.entry_password = customtkinter.CTkEntry(self.frame, width=250, placeholder_text="Enter password", show="*")
        self.entry_password.grid(row=2, column=0, padx=10, columnspan=8)
        self.empty_row = customtkinter.CTkLabel(self.frame, text="")
        self.empty_row.grid(row=3,columnspan=8)
        self.label_percentage = customtkinter.CTkLabel(self.frame, text="Enter min and max percents to bet:", text_color="green")
        self.label_percentage.grid(row=4,sticky=W, padx=10, columnspan=8)
        self.label_min = customtkinter.CTkLabel(self.frame, text="Min", text_color="green")
        self.label_min.grid(row=5, column=0, padx=10)
        self.entry_min = customtkinter.CTkEntry(self.frame, width=50, placeholder_text="25")
        self.entry_min.grid(row=5, column=1, sticky=W)
        self.label_max = customtkinter.CTkLabel(self.frame, text="Max", text_color="green")
        self.label_max.grid(row=6, column=0, padx=10)
        self.entry_max = customtkinter.CTkEntry(self.frame, width=50, placeholder_text="35")
        self.entry_max.grid(row=6, column=1, sticky=W)
        self.empty_row = customtkinter.CTkLabel(self.frame, text="")
        self.empty_row.grid(row=7, columnspan=8)
        self.label_max_balance = customtkinter.CTkLabel(self.frame, text="Enter max balance used for extraction:", text_color="green")
        self.label_max_balance.grid(row=8, sticky=W, padx=10, columnspan=8)
        self.entry_max_withdraw = customtkinter.CTkEntry(self.frame, width=100, placeholder_text="1500")
        self.entry_max_withdraw.grid(row=9, column=1, sticky=W)
        self.empty_row = customtkinter.CTkLabel(self.frame, text="")
        self.empty_row.grid(row=10, columnspan=8)
        self.button_start = customtkinter.CTkButton(self.frame, text="Start Betting", width=60, command=button_starter)
        self.button_start.grid(row=11, column=0, padx=10)
        self.button_start = customtkinter.CTkButton(self.frame, text="Stop Betting", width=60, command=stop)
        self.button_start.grid(row=11, column=1, padx=10)



if __name__ == "__main__":
    app = Graphical_window()
    app.mainloop()
