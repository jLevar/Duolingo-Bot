from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import platform
# To - Do
# Fill in the Blanks Questions
# Use the title of the question to know which question before looking for elements - theoretically removing need for those try blocks
# Figure out why sometimes (answer_box?) throws an ElementNotInteractableException and fix it

class Webdriver:
    def __init__(self):
        op_sys = platform.system()
        if op_sys == "Darwin":
            self.loginPath = "/Users/joshua.levar/Desktop/I'm Stuff/duoLogin.txt"
            driver = webdriver.Chrome(service=Service("/Users/joshua.levar/Desktop/chromedriver"))
        elif op_sys == "Windows":
            self.loginPath = "C:/Users/alanl/Desktop/duoLogin.txt"
            driver = webdriver.Chrome(service=Service("C:/Users/alanl/Downloads/chromedriver_win32/chromedriver.exe"))
            driver.set_window_position(2000, 0)
        else:
            raise "Error: OS Not Recognized"
        driver.maximize_window()
        self.use_keyboard_button_pressed = False
        self.driver = driver

    def login(self):
        driver = self.driver
        driver.implicitly_wait(20)
        driver.get('https://www.duolingo.com/learn')

        # 'I ALREADY HAVE AN ACCOUNT' button
        driver.find_element(By.CSS_SELECTOR, "button.WOZnx").click()

        # Retrieves username and password from file
        with open(self.loginPath, "r") as login_file:
            username = login_file.readline()
            password = login_file.readline()

        # Username box
        driver.find_element(By.CSS_SELECTOR,
                            'div._2a3s4:nth-child(1) > label:nth-child(1) > div:nth-child(1) > input:nth-child(1)'
                            ).send_keys(username)

        # Password box
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        'div._2a3s4:nth-child(2) > label:nth-child(1) > div:nth-child(1) > '
                                        'input:nth-child(1)'))
        ).send_keys(password)

        # Login button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._1rl91:nth-child(3)'))
        ).click()

        # Finds body of Duolingo home screen to ensure that the login was successful before finishing function
        driver.find_element(By.CLASS_NAME, '_3BJQ_')
        print("Login Successful")
        self.driver = driver

    def do_lesson(self, lesson_link):
        driver = self.driver
        driver.get(lesson_link)

        dictionary = self.load_dictionary_from_json()

        progress_bar = driver.find_element(By.CLASS_NAME, "_2YmyD")
        driver.implicitly_wait(2)

        while EC.presence_of_element_located(progress_bar):
            next_button = driver.find_element(By.CLASS_NAME, "_3HhhB")

            # Presses next_button until it is disabled
            while next_button.get_attribute("aria-disabled") == "false":
                next_button.click()

            question_title = driver.find_element(By.CLASS_NAME, "_2LZl6").text
            print(question_title)

            # Open Response Questions
            try:
                if question_title != "Write this in Spanish" and question_title != "Write this in English":
                    raise NoSuchElementException

                if not self.use_keyboard_button_pressed:
                    driver.find_element(By.CLASS_NAME, '_29cJe').click()
                    self.use_keyboard_button_pressed = True

                question_text = driver.find_element(By.CLASS_NAME, '_11rtD').text
                answer = dictionary.get(question_text)

                if answer is not None:
                    driver.find_element(By.CLASS_NAME, '_2EMUT').send_keys(answer)
                    next_button.click()
                else:
                    driver.find_element(By.CLASS_NAME, '_2EMUT').send_keys("Unknown Answer")
                    # TO-DO
                    # wait until next_button's attribute 'aria-disabled' is false
                    next_button.click()
                    dictionary[question_text] = driver.find_element(By.CLASS_NAME, '_1UqAr').text
                    self.save_dictionary_to_json(dictionary)
                    print("Saved Response to JSON")
                continue
            except NoSuchElementException:
                pass

            # Multiple Choice Questions
            try:
                buttons = driver.find_elements(By.CLASS_NAME, '_2CuNz')

                if question_title == "Read and respond":
                    question_text = driver.find_element(By.CLASS_NAME, '_9XgpY').text
                else:
                    # If it is a multiple-select fill in the blank, it should skip it
                    if driver.find_element(By.CLASS_NAME, "_1_wIY"):
                        raise NoSuchElementException
                    question_text = driver.find_element(By.CLASS_NAME, '_3Fi4A').text
                answer = dictionary.get(question_text)

                if answer is None:
                    # Hit skip and add answer
                    driver.find_element(By.CSS_SELECTOR, '.J51YJ').click()
                    dictionary[question_text] = driver.find_element(By.CLASS_NAME, '_1UqAr').text
                    self.save_dictionary_to_json(dictionary)
                    print("Saved MQA to JSON")
                else:
                    for button in buttons:
                        if button.text == answer:
                            button.click()
                            next_button.click()
                            break
                continue
            except NoSuchElementException:
                pass

            # Last Resort - Skips Question
            try:
                # Skip button
                driver.find_element(By.CSS_SELECTOR, '.J51YJ').click()
            except NoSuchElementException:
                pass

        print("Lesson complete")
        self.save_dictionary_to_json(dictionary)
        self.driver = driver

    @staticmethod
    def save_dictionary_to_json(dictionary):
        with open("dict.json", 'w') as file:
            file.write(json.dumps(dictionary))

    @staticmethod
    def load_dictionary_from_json():
        return json.load(open("dict.json"))

    def quit(self):
        time.sleep(5)
        self.driver.quit()
