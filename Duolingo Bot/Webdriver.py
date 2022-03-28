from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import platform

# To - Do
# Fill in the Blanks Questions
# Read and Respond Questions
# Note - The continue button and the check button have the same class name/css selector and it should be a variable
# bc it is used a lot

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
        use_keyboard_button_pressed = False

        progress_bar_class_name = "_2YmyD"

        driver.find_element(By.CLASS_NAME, progress_bar_class_name)
        driver.implicitly_wait(2)
        while EC.presence_of_element_located((By.CLASS_NAME, progress_bar_class_name)):
            # Open Response Questions
            try:
                if not use_keyboard_button_pressed:
                    driver.find_element(By.CLASS_NAME, '_29cJe').click()
                    use_keyboard_button_pressed = True

                question_text = driver.find_element(By.CLASS_NAME, '_11rtD').text
                answer_box = driver.find_element(By.CSS_SELECTOR, '._2EMUT')
                check_button = driver.find_element(By.CSS_SELECTOR, '._3HhhB')

                answer = dictionary.get(question_text)
                if answer is not None:
                    answer_box.send_keys(answer)
                    time.sleep(1)
                    check_button.click()
                else:
                    answer_box.send_keys("Unknown Answer")
                    time.sleep(1)
                    check_button.click()
                    dictionary[question_text] = driver.find_element(By.CLASS_NAME, '_1UqAr').text

                check_button.click()
                self.save_dictionary_to_json(dictionary)
                continue
            except NoSuchElementException:
                pass

            except Exception as e:
                print(type(e))
                pass

            # Multiple Choice Questions
            try:
                buttons = driver.find_elements(By.CLASS_NAME, '_2CuNz')
                question_text = driver.find_element(By.CLASS_NAME, '_3Fi4A').text
                check_button = driver.find_element(By.CSS_SELECTOR, '._3HhhB')
                answer = dictionary.get(question_text)

                if answer is None:
                    # Hit skip and add answer
                    driver.find_element(By.CSS_SELECTOR, '.J51YJ').click()
                    dictionary[question_text] = driver.find_element(By.CLASS_NAME, '_1UqAr').text
                else:
                    for button in buttons:
                        if button.text == answer:
                            button.click()
                            check_button.click()
                            break
                # Continue button
                driver.find_element(By.CLASS_NAME, "_3HhhB").click()
                self.save_dictionary_to_json(dictionary)
                continue
            except NoSuchElementException:
                pass

            # Error Handling - Finding Ways to Skip Question
            try:
                # Skip button
                driver.find_element(By.CSS_SELECTOR, '.J51YJ').click()
            except NoSuchElementException:
                pass

            try:
                # Continue button
                driver.find_element(By.CLASS_NAME, "_3HhhB").click()
                continue
            except NoSuchElementException:
                pass

            try:
                # Next button
                driver.find_element(By.CLASS_NAME, '_3HhhB').click()
                continue
            except NoSuchElementException:
                pass

            self.save_dictionary_to_json(dictionary)

        print("Lesson complete")
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
