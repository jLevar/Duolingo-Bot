from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import platform


# To - Do:
# Single word dictionary unreliable due to gendered words: Current solution is to delete the answer if it doesn't work
# But I would prefer it to store both answers and try both
# Optimize open responses by not checking for the use keyboard button on lesson 4 and up

class Webdriver:
    def __init__(self):
        op_sys = platform.system()

        if op_sys == "Darwin":
            self.loginPath = "/Users/joshua.levar/Desktop/I'm Stuff/duoLogin.txt"
            chrome_options = Options()
            chrome_options.add_argument("--start-fullscreen")
            driver = webdriver.Chrome(service=Service("/Users/joshua.levar/Desktop/chromedriver"),
                                      chrome_options=chrome_options)
        elif op_sys == "Windows":
            self.loginPath = "C:/Users/alanl/Desktop/duoLogin.txt"
            driver = webdriver.Chrome(service=Service("C:/Users/alanl/Downloads/chromedriver_win32/chromedriver.exe"))
            driver.set_window_position(2000, 0)
            driver.maximize_window()
        else:
            raise "Error: OS Not Recognized"

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
        driver.implicitly_wait(2)
        dictionary = self.load_dictionary_from_json("answers.json")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_2YmyD"))
        )

        while True:
            try:
                driver.find_element(By.CLASS_NAME, "_2YmyD")  # Progress bar
            except NoSuchElementException:
                break

            next_button = driver.find_element(By.CLASS_NAME, "_3HhhB")
            if next_button.get_attribute("aria-disabled") == "false":
                next_button.click()
                continue

            # The only reason this is in a try block is that on the read and respond questions, the next button
            # doesn't actually get clicked until a second run through. Because there is no skip button on this screen,
            # it throws an error
            try:
                skip_button = driver.find_element(By.CLASS_NAME, 'J51YJ')
            except NoSuchElementException:
                continue

            question_title = driver.find_element(By.CLASS_NAME, "_2LZl6").text

            # Type Missing Word Questions
            if question_title == "Type the missing word":
                driver.find_element(By.CLASS_NAME, '_29cJe').click()  # Make Harder Button
                skip_button.click()
                continue

            # Open Response Questions
            if "Write" in question_title:
                if not self.use_keyboard_button_pressed:
                    try:
                        use_keyboard_button = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.CLASS_NAME, '_29cJe'))
                        )
                        if use_keyboard_button.text == "USE KEYBOARD":
                            use_keyboard_button.click()
                            self.use_keyboard_button_pressed = True
                    except TimeoutException:
                        pass

                try:
                    question_title.index('“')
                    question_text = question_title[question_title.index('“') + 1: question_title.rindex('”')]
                    answer_box_str = 'x_l95'
                    one_word_answer = True
                except ValueError:
                    question_text = driver.find_element(By.CLASS_NAME, '_11rtD').text
                    answer_box_str = '_2EMUT'
                    one_word_answer = False

                answer = dictionary.get(question_text)

                if answer is not None:
                    driver.find_element(By.CLASS_NAME, answer_box_str).send_keys(answer)
                    next_button.click()
                else:
                    skip_button.click()
                    answer = driver.find_element(By.CLASS_NAME, '_1UqAr').text

                    if one_word_answer:
                        try:
                            answer = answer[:answer.index(",")]
                        except ValueError:
                            pass
                    dictionary[question_text] = answer
                continue

            # Matching Pairs Questions
            if question_title == "Select the matching pairs":
                left_words = [""] * 5
                right_words = [""] * 5
                left_buttons = []
                right_buttons = []

                for i in range(5):
                    left_buttons.append(
                        driver.find_element(By.XPATH, f'/html/body/div[1]/div/div/div/div/div[2]/div/div'
                                                      f'/div/div/div[2]/div/div/div[1]/div[{i + 1}]/button'))
                    right_buttons.append(
                        driver.find_element(By.XPATH, f'/html/body/div[1]/div/div/div/div/div[2]/div/div'
                                                      f'/div/div/div[2]/div/div/div[2]/div[{i + 1}]/button'))

                    left_words[i] = left_buttons[i].text
                    right_words[i] = right_buttons[i].text

                    left_words[i] = left_words[i][left_words[i].index("\n") + 1:]
                    right_words[i] = right_words[i][right_words[i].index("\n") + 1:]

                for i in range(5):
                    if left_buttons[i].get_attribute("aria-disabled") == "true":
                        continue

                    answer = dictionary.get(left_words[i])

                    if answer is not None:
                        for j in range(5):
                            if right_words[j] == answer:
                                left_buttons[i].click()
                                right_buttons[j].click()
                                break
                            if j == 4:
                                del dictionary[left_words[i]]
                        continue

                    for j in range(5):
                        if right_buttons[j].get_attribute("aria-disabled") == "true":
                            continue
                        left_buttons[i].click()
                        right_buttons[j].click()

                        time.sleep(1)
                        if left_buttons[i].get_attribute("aria-disabled") == "true":
                            dictionary[left_words[i]] = right_words[j]
                            break
                continue

            # Speaking Questions (Skipping)
            if question_title == "Speak this sentence":
                skip_button.click()
                continue

            # Word Bank Questions
            try:
                driver.find_element(By.CLASS_NAME, "_1_wIY")
                question_text = driver.find_element(By.CLASS_NAME, "_3NgMa").text

                answer = dictionary.get(question_text)
                buttons = driver.find_elements(By.CLASS_NAME, "_1yW4j")

                if answer is None:
                    skip_button.click()
                    answers = driver.find_elements(By.CLASS_NAME, "_3gI0Y")
                    answer = ""
                    for word in answers:
                        answer += word.text + "|"
                    dictionary[question_text] = answer
                else:
                    while len(answer) > 1:
                        for button in buttons:
                            try:
                                seperator_index = answer.index('|')
                            except ValueError:
                                del dictionary[question_text]
                                answer = ""
                                break
                            if button.text != answer[:seperator_index]:
                                continue
                            button.click()
                            buttons.remove(button)
                            # Truncates the leftmost word in the answer string
                            answer = answer[seperator_index + 1:]
                            break
                continue

            except NoSuchElementException:
                pass

            # Multiple Choice Questions
            try:
                buttons = driver.find_elements(By.CLASS_NAME, '_2CuNz')

                if question_title == "Read and respond":
                    question_text = driver.find_element(By.CLASS_NAME, '_9XgpY').text
                elif question_title == "Complete the chat":
                    question_text = driver.find_element(By.CLASS_NAME, '_29e-M').text
                elif "How do you say" in question_title:
                    question_text = driver.find_element(By.CLASS_NAME, '_2LZl6').text
                    question_text = question_text[question_text.index("\""):question_text.rindex("\"")]
                else:
                    question_text = driver.find_element(By.CLASS_NAME, '_3Fi4A').text

                answer = dictionary.get(question_text)

                if answer is None:
                    skip_button.click()
                    dictionary[question_text] = driver.find_element(By.CLASS_NAME, '_1UqAr').text
                else:
                    for index, button in enumerate(buttons):
                        if button.text == answer:
                            button.click()
                            next_button.click()
                            break
                        if index == len(buttons)-1:
                            del dictionary[question_text]

                continue
            except NoSuchElementException:
                pass

            # Last Resort - Skips Question
            print("Skipping: " + question_title)
            skip_button.click()

        print("Lesson Complete")
        self.save_dictionary_to_json(dictionary, "answers.json")
        print("Saved Answers to JSON")
        self.driver = driver

    def reset_driver(self):
        self.driver.get("https://www.duolingo.com/learn")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, '_1rl91'))  # "NO THANKS" Button
            ).click()
        except TimeoutException:
            pass

    def update_lesson(self, lesson: str):
        self.driver.implicitly_wait(10)

        if lesson == "ALL":
            lessons = {}
            lesson_buttons = self.driver.find_elements(By.CLASS_NAME, '_3TK8W')
            for button in lesson_buttons:

                if "\n" in button.text:
                    lesson_name = button.text[button.text.index("\n") + 1:]
                    lesson_crowns = int(button.text[:button.text.index("\n")])
                else:
                    lesson_name = button.text
                    lesson_crowns = 0

                lesson_name = lesson_name.replace(" ", "-")
                lessons[lesson_name] = lesson_crowns

            self.save_dictionary_to_json(lessons, "lessons.json")
            print("Saved Lessons to JSON")
        else:
            lessons = self.get_lessons()
            lesson_buttons = self.driver.find_elements(By.CLASS_NAME, '_3TK8W')
            for button in lesson_buttons:
                if "\n" in button.text:
                    lesson_name = button.text[button.text.index("\n") + 1:]
                    lesson_crowns = int(button.text[:button.text.index("\n")])
                else:
                    lesson_name = button.text
                    lesson_crowns = 0

                lesson_name = lesson_name.replace(" ", "-")

                if lesson_name == lesson:
                    lessons[lesson] = lesson_crowns
                    print(f"Updated Lesson \"{lesson}\"")
                    self.save_dictionary_to_json(lessons, "lessons.json")
                    return

    def get_lessons(self) -> dict:
        return self.load_dictionary_from_json("lessons.json")

    @staticmethod
    def save_dictionary_to_json(dictionary: dict, file_path: str):
        with open(file_path, 'w') as file:
            file.write(json.dumps(dictionary, indent=1))

    @staticmethod
    def load_dictionary_from_json(file_path: str) -> dict:
        return json.load(open(file_path))

    def quit(self):
        time.sleep(5)
        self.driver.quit()
