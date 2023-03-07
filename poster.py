import collections
import time
from selenium.common.exceptions import NoSuchElementException
from tkinter import messagebox as mb
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

COOKIE_BUTTON_PATH = "/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]"

LOGIN_BUTTON_PATH = "/html/body/div[1]/div[1]/div[1]/div/div[2]/div[2]/form/div/div[3]/button"

HOME_BUTTON_PATH = "/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div[1]/div/div[1]/div/div/div[1]/div/div/div[" \
                   "1]/span/div/a/i"

PICTURE_BUTTON_PATH = "/html/body/div[1]/div/div[1]/div/div[6]/div/div/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div[2]/div[2]/div[1]/span[1]/i"

ANOTHER_PICTURE_BUTTON_PATH = "/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div/div[2]/div[2]/div[1]/span[1]/i"

WRITE_SOMETHING_PATH = ["//*[contains(text(), 'Napisz coś...')]", "//*[contains(text(), 'Write something...')]",
                        "//*[contains(text(), 'Напишите что-нибудь...')]"]

PEOPLE_BUTTON_PATH = "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/form/" \
                     "div/div[1]/div/div/div[1]/div/div[3]/div[1]/div" \
                     "[2]/div[4]/div/span/div/div/div[1]/div/div/div[1]/i"

ADD_TO_POST = "/html/body/div[1]/div/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div/div/div/div[1]/form/div/div[1]/div/div/div[1]/div/div[3]/div[1]/div[1]/div"

ANOTHER_PEOPLE_BUTTON_PATH = "/html/body/div[1]/div/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div/div/div/div[" \
                             "1]/form/div/div[1]/div/div/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/span/div/div/div" \
                             "[1]/div/div/div[1]/i"

LOADING_POST = ["//span[text()='Publikowanie']", "//span[text()='Posting']", "//span[text()='Публикация']"]

STREAM_BUTTON = ["//span[text()='Transmisja wideo na żywo']", "//span[text()='Live video']",
                 "//span[text()='Прямой эфир']"]

BLOCK_WARNING = ["//span[text()='powiadom nas o tym']", "//span[text()='let us know']",
                 "//span[text()='дайте нам знать']"]

CAN_NOT_POSTING_ALERT = "/html/body/div[4]/div[1]/div/div[2]/div/div/div/div/div[3]/div/div[1]/div"

STREAM_BUTTON_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div/div[2]/div[1]"


class Poster:
    def __init__(self):
        self.is_posting = False
        self.is_driver_online = False
        self.gui = None
        self.links = set()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-notifications")
        self.options.headless = False
        self.current_driver = None
        self.language_id = 0  # if = 0 PL, 1 - ENG, 2 - RU

    def start_driver(self):
        self.current_driver = webdriver.Chrome(
            executable_path=r'/tmp/chrome/chromedriver.exe',
            options=self.options)
        self.is_driver_online = True
        self.current_driver.set_window_size(1920, 1080)
        self.home_page()

    def bind_gui(self, gui):
        self.gui = gui

    def handle_login(self, login: str, password: str):
        self.auth(login, password)

    def handle_open_file(self, file):
        self.set_groups_from_file(file)

    def handle_check_box(self):
        return self.gui.checkbox.get()

    def stop_execution(self):
        self.is_posting = False

    def what_is_language(self):
        for i in STREAM_BUTTON:
            try:
                WebDriverWait(self.current_driver, 2, 0.3).until(
                    ec.visibility_of_element_located((By.XPATH, i)))
                print(f'Current language id is {STREAM_BUTTON[self.language_id]}')
                return self.language_id
            except TimeoutException:
                self.language_id += 1
                if self.language_id > len(STREAM_BUTTON):
                    self.home_page()
                    mb.showerror("Your account language is not supported, switch it to PL, ENG or RUS")

    def auth(self, login, password) -> None:
        if self.is_cookie_button_exist():
            self.current_driver.find_element(By.XPATH, COOKIE_BUTTON_PATH).click()
        email_input = self.current_driver.find_element(By.ID, "email")
        email_input.clear()
        email_input.send_keys(login)
        password_input = self.current_driver.find_element(By.ID, "pass")
        password_input.clear()
        password_input.send_keys(password)
        self.current_driver.find_element(By.NAME, "login").click()

        if not self.is_logged_in():
            mb.showinfo("Warning!", "Your login or password is incorrect")
            self.home_page()
            return

        self.gui.handle_logged_in()
        self.gui.status_switch_auth_btn()
        self.gui.status_switch_stop_posting_btn()
        self.what_is_language()

    def is_stream_button_exist(self):
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, STREAM_BUTTON_XPATH)))
            return True
        except TimeoutException:
            return False

    def is_logged_in(self) -> bool:
        if self.is_stream_button_exist():
            return True
        elif self.is_home_button_exist():
            home_button = self.current_driver.find_element(By.XPATH, HOME_BUTTON_PATH)
            if home_button.get_attribute("data-visualcompletion") == "css-img":
                return True
        elif self.is_picture_button_exist():
            picture_button = self.current_driver.find_element(By.XPATH, PICTURE_BUTTON_PATH)
            if picture_button.get_attribute("data-visualcompletion") == "css-img":
                return True
        elif self.is_another_picture_button_exist():
            picture_button = self.current_driver.find_element(By.XPATH, ANOTHER_PICTURE_BUTTON_PATH)
            if picture_button.get_attribute("data-visualcompletion") == "css-img":
                return True
        else:
            return False

    def is_can_not_posting_alert_exist(self):
        try:
            WebDriverWait(self.current_driver, 1, 0.25).until(
                ec.visibility_of_element_located((By.XPATH, CAN_NOT_POSTING_ALERT)))
            return True
        except TimeoutException:
            return False

    def is_home_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, HOME_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def is_picture_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, PICTURE_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def is_another_picture_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, ANOTHER_PICTURE_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def is_add_to_post_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, ADD_TO_POST)))
            return True
        except TimeoutException:
            return False

    def is_cookie_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, COOKIE_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def is_text_field_in_group_exist(self) -> bool:
        if self.is_add_to_post_button_exist():
            return True
        else:
            return False

    def is_people_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, PEOPLE_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def is_another_people_button_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, ANOTHER_PEOPLE_BUTTON_PATH)))
            return True
        except TimeoutException:
            return False

    def home_page(self):
        self.current_driver.get("https://facebook.com")

    @staticmethod
    def is_file_path_not_empty(file_path) -> bool:
        return len(file_path) > 0

    def is_links_not_empty(self) -> bool:
        return len(self.links) > 0

    def set_groups_from_file(self, file_path: str):
        if self.is_file_path_not_empty(file_path):
            self.links = set()
            with open(file_path) as file:
                for link in file:
                    self.links.add(link)
                file.close()
        self.gui.handle_auth_btn()

    @staticmethod
    def count_lines(message: str):
        counter = collections.Counter(message)
        num_of_new_line = counter["\n"]
        return num_of_new_line

    @staticmethod
    def is_message_not_empty(message: str) -> bool:
        if len(message) == 0:
            return False

    def write_message(self, message: str):
        if self.is_message_not_empty:
            action_chain = ActionChains(self.current_driver)
            action_chain.send_keys(message)
            if self.count_lines(message) > 3:
                action_chain.send_keys(Keys.TAB * 8)
            else:
                action_chain.send_keys(Keys.TAB * 9)
            action_chain.perform()
            time.sleep(1)
            action_chain.send_keys(Keys.ENTER)
            action_chain.perform()

    @staticmethod
    def get_clickable_button(span: WebElement) -> WebElement:
        parent = span.find_element(By.XPATH, "..")
        return parent.find_element(By.XPATH, "..")

    def is_write_something_exist(self) -> bool:
        try:
            WebDriverWait(self.current_driver, 2, 0.3).until(
                ec.visibility_of_element_located((By.XPATH, WRITE_SOMETHING_PATH[self.language_id])))
            return True
        except TimeoutException:
            return False

    def start_posting(self, message_to_post):
        if self.is_links_not_empty():
            self.is_posting = True
            self.gui.status_switch_text_field()
            self.gui.status_switch_posting_btn()
            self.gui.status_switch_stop_posting_btn()
            self.gui.status_switch_open_btn()
            self.gui.handle_posting_started()
            for group in self.links:
                if self.is_posting:
                    self.current_driver.get(group)
                    self.gui.handle_link_changed(group)
                    if self.is_write_something_exist():
                        write_something = self.current_driver.find_element(By.XPATH,
                                                                           WRITE_SOMETHING_PATH[self.language_id])
                        button = self.get_clickable_button(write_something)
                        button.click()
                    if self.is_text_field_in_group_exist():
                        self.write_message(message_to_post)
                        if self.is_can_not_posting_alert_exist() or self.is_block_warning_exist():
                            self.home_page()
                            self.is_posting = False
                            self.gui.status_switch_posting_btn()
                            self.gui.status_switch_stop_posting_btn()
                            self.gui.status_switch_open_btn()
                            self.gui.status_switch_text_field()
                        else:
                            self.is_loading_post_pl_disappeared()
                    else:
                        continue
            self.home_page()
            self.is_posting = False
            self.gui.status_switch_posting_btn()
            self.gui.status_switch_stop_posting_btn()
            self.gui.status_switch_open_btn()
            self.gui.status_switch_text_field()
            return mb.showinfo("Posting is over", "Now you can choose another .txt file")
        else:
            return mb.showerror("Error", "Link to group can not be empty")

    def is_loading_post_pl_disappeared(self):
        while True:
            try:
                self.current_driver.find_element(By.XPATH, LOADING_POST[self.language_id])
            except NoSuchElementException:
                break

    def is_block_warning_exist(self):
        try:
            self.current_driver.find_element(By.XPATH, BLOCK_WARNING[self.language_id])
            mb.showwarning("BLOCK WARNING!",
                           """The account has been temporarily suspended, please restart the program as a different\
user. To avoid this, please use the program wisely!""")
            return True
        except NoSuchElementException:
            return False
