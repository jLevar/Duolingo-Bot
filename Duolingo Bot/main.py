from Webdriver import Webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

gs_lessons = ["Pres-Tense-1"]
myWebdriver = Webdriver()
try:
    myWebdriver.login()
    myWebdriver.update_lesson("ALL")
    lessons = myWebdriver.get_lessons()
    for lesson in lessons:
        if lesson in gs_lessons:
            continue
        while lessons[lesson] < 5:
            myWebdriver.do_lesson(f'https://www.duolingo.com/skill/es/{lesson}')
            myWebdriver.reset_driver()
            myWebdriver.update_lesson(lesson)
            lessons = myWebdriver.get_lessons()

except (NoSuchElementException, TimeoutException):
    print("Error: Element Not Found (Timed Out)")
finally:
    print("Shutting down...")
    myWebdriver.quit()
