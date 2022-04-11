from Webdriver import Webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

myWebdriver = Webdriver()
try:
    myWebdriver.login()
    myWebdriver.do_lesson('https://www.duolingo.com/skill/es/Community/1')
except (NoSuchElementException, TimeoutException):
    print("Error: Element Not Found (Timed Out)")
# except Exception as e:
#     print(e)
finally:
    print("Shutting down...")
    myWebdriver.quit()
