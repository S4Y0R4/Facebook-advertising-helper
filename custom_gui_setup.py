from tkinter import filedialog as fd
from tkinter import messagebox as mb
import threading
import poster as p
import customtkinter

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green


def file_dialog_wrapper(on_open_file):
    file_path = fd.askopenfilename(filetypes=[("Text files", ".txt")])
    on_open_file(file_path)


class AutoPosterGUI(threading.Thread):
    def __init__(self, poster: p.Poster):
        threading.Thread.__init__(self)
        self.posting_btn = None
        self.stop_posting_btn = None
        self.open_btn = None
        self.auth_btn = None
        self.password_entry = None
        self.text_txt = None
        self.login_entry = None
        self.win = None
        self.poster = poster
        self.help_btn = None
        self.label_group = None
        self.start()

    def run(self) -> None:
        self.win = customtkinter.CTk()
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.login_entry = customtkinter.CTkEntry(master=self.win, placeholder_text="Your login or number", width=200)
        self.auth_btn = customtkinter.CTkButton(master=self.win, text="Authentication", width=100,
                                                command=lambda: threading.Thread(
                                                    target=self.poster.handle_login(self.login_entry.get(),
                                                                                    self.password_entry.get())).start())

        self.help_btn = customtkinter.CTkButton(master=self.win, text="Help me!", width=100, command=self.how_to_use)
        self.password_entry = customtkinter.CTkEntry(master=self.win, placeholder_text="Your password", width=200,
                                                     show="*")
        self.stop_posting_btn = customtkinter.CTkButton(master=self.win, text="Stop posting!", width=100,
                                                        command=self.stop_execution)

        self.posting_btn = customtkinter.CTkButton(master=self.win, text="Start posting!", width=100,
                                                   command=lambda: threading.Thread(target=self.start_posting,
                                                                                    daemon=True).start())

        self.open_btn = customtkinter.CTkButton(master=self.win, text="Open file", width=100,
                                                command=lambda: file_dialog_wrapper(
                                                    on_open_file=self.poster.handle_open_file))
        self.label_group = customtkinter.CTkLabel(master=self.win, text="The link for the processed group will be here")
        self.text_txt = customtkinter.CTkTextbox(master=self.win, width=310)
        self.setup_gui()

    def stop_execution(self):
        if self.poster.is_posting:
            self.poster.stop_execution()

    def start_posting(self):
        if not self.poster.is_posting:
            self.poster.stop_execution()
        message = self.text_txt.get("0.0", "end")
        self.poster.start_posting(message)

    def setup_gui(self):
        self.win.title("FB poster")
        self.win.geometry("430x362")
        self.win.resizable(False, False)
        self.create_login_component()
        self.create_body()
        self.win.mainloop()

    def create_body(self):
        self.text_txt.grid(row=2, column=0, sticky="nw", padx=5, pady=5, columnspan=2)
        self.open_btn.grid(row=2, column=2, sticky="nw", padx=5, pady=5)
        self.label_group.grid(row=3, column=0, sticky="nw", padx=5, pady=5, columnspan=3)
        self.help_btn.grid(row=4, column=2, padx=5, pady=5)

    def create_login_component(self):
        self.login_entry.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        self.password_entry.grid(row=1, column=0, padx=5, pady=5, sticky="nw")

    def handle_posting_started(self):
        print('posting started', self)

    def handle_auth_btn(self):
        self.auth_btn.grid(row=0, column=1, padx=5, pady=5, rowspan=2, sticky="ns")

    @staticmethod
    def how_to_use() -> str:
        info = """EN:
To use the script correctly, please don't try to break it, make sure you have a .txt file with the correct group links \
. If you need to make two identical posts in a row, just duplicate the link in your file. Do not worry about your data,\
 the script code is free and you can analyze it if necessary.So far, the ability to post emoji has not been implemented\
 (with the exception of those characters that Meta itself interpretst into emoticons, like ':)' and so on... I hope to \
do that later.)
Be careful, for the script to work correctly, the language of your Facebook account must be either Russian, or English,\
 or Polish. If you need another language, then write about it to my mail or github.
Do not worry about your data, the script code is open-source and you can analyze it if necessary.
RU:
Для правильного использования скрипта, пожалуйста, не пытайтесь его сломать, убедитесь, что у вас создан .txt файл с ну\
жными ссылками на группы. Если вам необходимо сделать два одинаковых поста подряд, просто продублируйте ссылку в вашем \
файле. Пока что не реализована возможность постить эмоджи (за исключением тех символов, которые интерпритирует сам Face\
book, например ':)' и тд... Надеюсь, сделаю это позже.)
Будьте внимательны, для корреткной работы скрипта, язык вашего Facebook аккаунта должен быть либо русским, либо английс\
ким, либо польским. Если вам будет необходим другой язык, то напишите об этом мне на почту или в гитхаб.
Не беспокойтесь за ваши данные, код скрипта свободный и при необходимости вы можете его проанализировать.

***************************
 https://github.com/S4Y0R4
***************************
"""
        return mb.showinfo("Information", info)

    def handle_link_changed(self, group: str):
        self.label_group.configure(text=group[12:])

    def handle_logged_in(self):
        self.posting_btn.grid(row=0, column=2, padx=5, pady=5)
        self.stop_posting_btn.grid(row=1, column=2, padx=5, pady=5)

    def status_switch_posting_btn(self):
        if self.poster.is_posting:
            self.posting_btn.configure(state="disabled")
        else:
            self.posting_btn.configure(state="normal")

    def status_switch_text_field(self):
        if self.poster.is_posting:
            self.text_txt.configure(state="disabled")
        else:
            self.text_txt.configure(state="normal")

    def status_switch_stop_posting_btn(self):
        if self.poster.is_posting:
            self.stop_posting_btn.configure(state="normal")
        else:
            self.stop_posting_btn.configure(state="disabled")

    def status_switch_auth_btn(self):
        self.auth_btn.configure(state="disabled")

    def status_switch_open_btn(self):
        if self.poster.is_posting:
            self.open_btn.configure(state="disabled")
        else:
            self.open_btn.configure(state="normal")

    def on_closing(self):
        if mb.askokcancel("Quit", "Do you want to quit?"):
            self.poster.current_driver.quit()
            self.win.destroy()
