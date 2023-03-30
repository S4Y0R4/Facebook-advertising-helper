from tkinter import filedialog as fd
from tkinter import messagebox as mb
import poster as p
import customtkinter

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green


def file_dialog_wrapper(on_open_file):
    file_path = fd.askopenfilename(filetypes=[('text files or image', ('.png', '.jpg', '.txt'))])
    on_open_file(file_path)


class AutoPosterGUI:
    def __init__(self, poster: p.Poster):
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

    def run(self) -> None:
        self.win = customtkinter.CTk()
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.login_entry = customtkinter.CTkEntry(master=self.win, placeholder_text="Your login or number", width=200)
        self.auth_btn = customtkinter.CTkButton(master=self.win, text="Authentication", width=100,
                                                command=lambda: self.poster.handle_login(self.login_entry.get(),
                                                                                         self.password_entry.get()))

        self.help_btn = customtkinter.CTkButton(master=self.win, text="Help me!", width=100,
                                                command=self.how_to_use)
        self.password_entry = customtkinter.CTkEntry(master=self.win, placeholder_text="Your password", width=200,
                                                     show="*")
        self.stop_posting_btn = customtkinter.CTkButton(master=self.win, text="Stop posting!", width=100,
                                                        command=self.poster.stop_execution)

        self.posting_btn = customtkinter.CTkButton(master=self.win, text="Start posting!", width=100,
                                                   command=lambda: self.start_posting())

        self.open_btn = customtkinter.CTkButton(master=self.win, text="Open txt file", width=100,
                                                command=lambda: file_dialog_wrapper(
                                                    on_open_file=self.poster.handle_open_file))

        self.pic_btn = customtkinter.CTkButton(master=self.win, text="Open picture", width=100,
                                               command=lambda: file_dialog_wrapper(
                                                   on_open_file=self.poster.handle_open_pic))

        self.label_group = customtkinter.CTkLabel(master=self.win, text="The link for the processed group will be here")
        self.text_txt = customtkinter.CTkTextbox(master=self.win, width=310)
        self.setup_gui()

    def start_posting(self):
        self.poster.is_posting = True
        message = self.text_txt.get("0.0", "end")
        self.poster.handle_posting(message)

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
        self.pic_btn.grid(row=4, column=0, sticky="nw", padx=5, pady=5)

    def create_login_component(self):
        self.login_entry.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        self.password_entry.grid(row=1, column=0, padx=5, pady=5, sticky="nw")

    def handle_auth_btn(self):
        self.auth_btn.grid(row=0, column=1, padx=5, pady=5, rowspan=2, sticky="ns")

    @staticmethod
    def how_to_use():
        info = """EN:
To use the script correctly, please don't try to break it, make sure you have a .txt file with the correct group links.\
Сarefully, for the script to work correctly, the language of your Facebook account must be either Russian, or English, \
or Polish. If you need another language, then write to me about it.
Don't worry about the data, the script code is free and you can view it if needed.

RU:
Для правильного использования скрипта, пожалуйста, не пытайтесь его сломать, убедитесь, что у вас создан .txt файл с ну\
жными ссылками на группы.
Будьте внимательны, для корреткной работы скрипта, язык вашего Facebook аккаунта должен быть либо русским, либо английс\
ким, либо польским. Если вам будет необходим другой язык, то напишите об этом мне.
Не беспокойтесь за ваши данные, код скрипта свободный и при необходимости вы можете его проанализировать.

*****************************
 https://github.com/S4Y0R4
*****************************
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

    def status_switch_auth_btn_off(self):
        self.auth_btn.configure(state="disabled")

    def status_switch_auth_btn_on(self):
        self.auth_btn.configure(state="normal")

    def status_switch_open_btn(self):
        if self.poster.is_posting:
            self.open_btn.configure(state="disabled")
        else:
            self.open_btn.configure(state="normal")

    def status_switch_pic_btn(self):
        if self.poster.is_posting:
            self.pic_btn.configure(state="disabled")
        else:
            self.pic_btn.configure(state="normal")

    def on_closing(self):
        if mb.askokcancel("Quit", "Do you want to quit?"):
            if self.poster.is_driver_online:
                self.poster.current_driver.quit()
            self.win.destroy()
