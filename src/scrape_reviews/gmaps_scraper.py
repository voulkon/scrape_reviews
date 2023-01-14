from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import inspect
import datetime
import pytz
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import logging
import urllib.parse
from selenium.webdriver.remote.webelement import WebElement
import pyperclip

logging.basicConfig(level=logging.INFO)


def prettify_log_msg(msg):
    """
    Makes a msg appear like that:

    ****************************************************************************************************
    msg
    ****************************************************************************************************

    """
    return "\n" + "*" * 100 + "\n" + msg + "\n" + "*" * 100


def calculate_elapsed_time(func):
    """
    A decorator that calculates time needed for a function to run
    """
    import time
    import logging

    def func_inside_it(*args, **kwargs):

        start_time = time.perf_counter()

        func(*args, **kwargs)

        end_time = time.perf_counter()

        time_msg = (
            "Total seconds needed for : "
            + func.__name__
            + " "
            + str(end_time - start_time)
        )

        logging.debug(prettify_log_msg(time_msg))

    return func_inside_it


class gMapsScraper(object):

    base_url = "https://www.google.com/maps/search/"

    ENTITIES_BASE_XPATH_INIT = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]'

    FOUND_IN_ATTRIBUTES = {"reviewer": "aria-label", "data-review-id": "data-review-id"}

    FOUND_IN_CLASSES = {
        "text_of_review": "wiI7pd",
        "date_created": "xRkPPb",
        "reviewer": "d4r55",
        "reviewers_no_of_reviews": "RfnDt",
        "rating": "fzvQIb",
    }

    INFO_DICTIONARY: dict[str] = {
        "Name": "qBF1Pd",
        "Overall_Rating": "MW4etd",
        "Number_of_Ratings": "UY7F9",
    }

    CLASS_OF_REVIEW_CONTAINER = "jftiEf"
    # CLASS_OF_REVIEWS_BUTTON = "DkEaL"  # "hh2c6.G7m0Af" #""
    # REVIEWS_WINDOWS_CLASS = "#QA0Szd > div > div > div.w6VYqd > div.bJzME.Hu9e2e.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf"
    # CLASS_OF_CATEGORIES_OF_INTEREST_BUTTONS = "KNfEk.Rqu0ae"
    # ENTITIES_BASE_XPATH_INIT = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]'
    CLASS_OF_STARS = "kvMYJc"
    # # The Button to Click in order to Avoid Cookies Screen and procceed with the actul website
    # COOKIES_XPATH = '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button'
    # PARENT_XPATH_OF_CATEGORIES = (
    #     '//*[@id="assistive-chips"]/div/div/div/div[1]/div/div/div/div/div[5]/div[2]'
    # )
    # XPATH_OF_EACH_CATEGORY = {
    #     '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]': GoogleMapsCategories.HOTELS,
    #     '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]': GoogleMapsCategories.RESTAURANTS,
    # }

    # ...

    def __init__(self, maximum_wait_time_in_seconds: int = 40) -> None:

        """Just prepare the browser"""

        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.wait = WebDriverWait(self.driver, maximum_wait_time_in_seconds)
        self.wait_lite = WebDriverWait(self.driver, maximum_wait_time_in_seconds / 3)

    def extract_info_of_each_element(self, specific_element) -> dict[str]:
        """
        Returns name, rating and number of reviews for an entity

        Parameters:
        -----------
            specific_element : selenium.webdriver.remote.webelement.WebElement
            INFO_DICTIONARY : dict

        Returns:
        --------
        A dict:
            e.g. {'Name': 'Ewa Lodge', 'Overall_Rating': '4,3', 'Number_of_Ratings': '(97)'}

        """

        # First check that we're looking for exists
        try:
            # We'll achieve this by looking for its name
            # specific_element.find_element(By.CLASS_NAME, self.INFO_DICTIONARY["Name"])
            self.wait_lite.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, self.INFO_DICTIONARY["Name"])
                )
            )

        except:
            # If entity's name is not found, the element we've clicked on does not contain an entity
            # Most probably we've cleaned all entites and we're examining
            # the very bottom elements of the page
            # By returning None, we signal to the fetch_reviews function that the entities are finished
            return

        try:
            # Fetch info for each element - the name, the rating, etc.
            clean_info = {
                info: specific_element.find_element(
                    By.CLASS_NAME, self.INFO_DICTIONARY[info]
                ).text
                for info in self.INFO_DICTIONARY
            }

        # In case it has no reviews
        except:
            # Return N/A as string and the Name
            clean_info = {
                info: "N/A" for info in self.INFO_DICTIONARY if info not in ["Name"]
            }
            clean_info["Name"] = specific_element.find_element(
                By.CLASS_NAME, self.INFO_DICTIONARY["Name"]
            ).text

        return clean_info

    def clean_one_review(self, review_element):
        """
        Take one review element and return it clean.
        """

        # TODO: FOUND_IN_CLASSES & FOUND_IN_ATTRIBUTES will become properties of self

        this_reviews_line = {}
        for header in self.FOUND_IN_ATTRIBUTES:

            try:
                extracted = review_element.get_attribute(header)
            except:
                # An Empty String
                extracted = ""

            this_reviews_line[header] = extracted

        for info in self.FOUND_IN_CLASSES:

            try:
                extracted = review_element.find_element(
                    By.CLASS_NAME, self.FOUND_IN_CLASSES[info]
                ).text
            except:
                # An Empty String
                extracted = ""

            this_reviews_line[info] = extracted

        def extract_rating_from_review_stars(
            review_element, CLASS_OF_STARS=self.CLASS_OF_STARS
        ):

            import re

            raw_stars_content = review_element.find_element(
                By.CLASS_NAME, CLASS_OF_STARS
            ).get_attribute("aria-label")

            tbr = re.sub(r"\D", "", raw_stars_content) + "/5"

            return tbr

        if this_reviews_line["rating"] == "":

            this_reviews_line["rating"] = extract_rating_from_review_stars(
                review_element=review_element, CLASS_OF_STARS=self.CLASS_OF_STARS
            )

        if this_reviews_line["date_created"] == "":

            this_reviews_line["date_created"] = review_element.find_element(
                By.CLASS_NAME, "rsqaWe"
            ).text

        return this_reviews_line

    def fetch_reviews(
        self, search_term: str = "Nauru Hotel", return_something: bool = True
    ):

        wanted_url = self.create_search_url(search_term)

        logging.info(prettify_log_msg(f"Trying url: {wanted_url}"))

        self.driver.get(wanted_url)

        # Prerequisite: Surpass Cookies

        # TODO: Make it class attribute
        self.push_a_button_by_its_text(
            id_of_button="span", text_of_button="Απόρριψη όλων"
        )

        # Find where entities start
        this_times_entities_start_from: int = self.find_where_first_entity_is(
            path_to_check=self.ENTITIES_BASE_XPATH_INIT
        )
        this_times_entities_base_xpath: str = self.ENTITIES_BASE_XPATH_INIT.format(
            to_be_confirmed=str(this_times_entities_start_from)
        )

        # //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[5]

        entities_pane: WebElement = self.driver.find_element(
            By.XPATH, this_times_entities_base_xpath
        )

        self.scroll_down_to_reveal_all_elements(entities_pane)

        specific_entitys_base_xpath = (
            this_times_entities_base_xpath + "/div[{to_be_confirmed}]"
        )

        entities_start_from: int = self.find_where_first_entity_is(
            specific_entitys_base_xpath
        )

        this_time_entitys_variable_part = entities_start_from
        # HACK: replace with while
        for _ in range(3):

            entitys_xpath = specific_entitys_base_xpath.format(
                to_be_confirmed=this_time_entitys_variable_part
            )

            entity_clear = self.scrape_an_entity_element(entitys_xpath)

            this_time_entitys_variable_part += 2

            return entity_clear

    def scrape_an_entity_element(self, entitys_xpath: str):

        entity: WebElement = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, entitys_xpath))
        )
        # //*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]

        self.scroll_down_to_reveal_all_elements(pane=entity)

        entitys_info = self.extract_info_of_each_element(entity)
        entity.click()
        entitys_details = self.fetch_entitys_details()

        # TODO: make ξιολογήσεις a class attribute
        self.push_a_button_by_its_text_containing(
            id_of_button="span", text_of_button_contains="ξιολογήσεις"
        )

        self.expand_collapsed_reviews()

        reviews_of_this_entity_right_now = self.driver.find_elements(
            By.CLASS_NAME, self.CLASS_OF_REVIEW_CONTAINER
        )

        clean_revs = []
        for r, rev in enumerate(reviews_of_this_entity_right_now):
            clean_rev = self.clean_one_review(rev)

            clean_revs.append(clean_rev)

            print(f"Number: {r+1}:\clean_rev: {clean_rev}")

        return [entitys_info, entitys_details, clean_revs]

        # TODO: Fix this
        # entitys_info["fetched_at"] = fetched_at
        # entitys_info["fetched_looking_at_place"] = fetched_looking_at_place
        # this_entitys_name = entitys_info["Name"]

        # TODO: Check whether it exists
        # this_entitys_name_already_exists =any([this_entitys_name in ent["Name"] for ent in all_info])

        # TODO: An early return
        # if specific_elements_info["Number_of_Ratings"] == "N/A"

        # entitys_sub_pane =

        ...
        ...

    @calculate_elapsed_time
    def scroll_down_to_reveal_all_elements(
        self,
        pane: WebElement,
        scroll_step: int = 5000,
        sleep_time_between_scrolls: int = 1,
    ):
        """
        Scrolling a pane/ part of a webpage so that all un-loaded elements get revealed
        """

        previous_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", pane
        )
        current_height = (
            self.driver.execute_script("return arguments[0].scrollHeight", pane) + 1
        )

        while current_height > previous_height:

            previous_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", pane
            )

            sleep(sleep_time_between_scrolls)

            script_to_execute = "arguments[0].scrollTo(0, {});".format(
                previous_height + scroll_step
            )

            self.driver.execute_script(script_to_execute, pane)

            sleep(sleep_time_between_scrolls)

            current_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", pane
            )

            sleep(sleep_time_between_scrolls)

    @calculate_elapsed_time
    def push_a_button_by_its_text(self, id_of_button: str, text_of_button: str) -> None:
        try:
            cookies_xpath = f'//{id_of_button}[text() = "{text_of_button}"]'

            cookies_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, cookies_xpath))
            )

            if cookies_button:
                cookies_button.click()
        except:
            logging.info(
                f"{id_of_button} element with text of {text_of_button} is not clickable"
            )
            return

    @calculate_elapsed_time
    def push_a_button_by_its_text_containing(
        self, id_of_button: str, text_of_button_contains: str
    ) -> None:

        try:
            cookies_xpath = (
                f'//{id_of_button}[ contains(text() , "{text_of_button_contains}")]'
            )

            cookies_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, cookies_xpath))
            )

            if cookies_button:
                cookies_button.click()
        except:
            logging.info(
                f"{id_of_button} element with text of {text_of_button_contains} is not clickable"
            )
            return

    def create_search_url(self, search_term: str) -> str:
        url_wanted = f"{self.base_url}{search_term}"

        # url_wanted = urllib.parse.quote(url_wanted)
        return url_wanted

    def find_where_first_entity_is(self, path_to_check: str) -> int:

        for try_position in range(10):
            temp_position = path_to_check.format(to_be_confirmed=try_position)
            try:
                extracted = self.extract_info_of_each_element(
                    self.driver.find_element(By.XPATH, temp_position)
                )
                if isinstance(extracted, dict):
                    if extracted["Name"] != "":
                        return try_position
            except:
                continue

        return

    def fetch_entitys_details(self):

        img_addresses = {
            "location": "place_gm_",
            "telephone": "phone_gm_",
        }

        clean_details = {}
        for detail, img_address in img_addresses.items():
            logging.info(f"Looking for {detail}")
            details_xpath = f'//img[ contains(@src, "{img_address}")] '

            detail_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, details_xpath))
            )

            # self.driver.find_element(By.XPATH, details_xpath)

            detail_element.click()

            detail_text = pyperclip.paste()  # Tk().clipboard_get()
            logging.info(f"extracted {detail} text: {detail_text}")

            clean_details[detail] = detail_text

        location_class_to_search_for = "meta"
        location_attribute_to_search_for = "content"
        location_content_to_search_for = "maps.google.com/maps/api/"
        locations_element_xpath = f'//{location_class_to_search_for}[ contains(@{location_attribute_to_search_for}, "{location_content_to_search_for}")] '
        locations_element = self.driver.find_element(By.XPATH, locations_element_xpath)
        maps_location = locations_element.get_attribute(
            location_attribute_to_search_for
        )
        clean_details["gmaps_image"] = maps_location

        return clean_details

    @calculate_elapsed_time
    def expand_collapsed_reviews(self):

        """Presses all "More" Buttons to reveal reviews' text"""

        keywords_to_look_for = ["Περισσότερα", "More", "more", "Más", "Mas"]

        more_text_buttons = []

        for keyword_to_look_for in keywords_to_look_for:

            search_result = self.driver.find_elements(
                By.XPATH, (f"//button[text()='{keyword_to_look_for}']")
            )

            if len(search_result) > 0:
                break

        if len(search_result) == 0:
            return

        for text_button in search_result:
            more_text_buttons.append(text_button)

        # TODO: include other languages too: more, mas, etc.

        # I don't remember why the hell i did this
        for b, more_text_button in enumerate(more_text_buttons):
            try:
                more_text_button.click()
            except:
                continue


a = gMapsScraper(maximum_wait_time_in_seconds=10)

entities_pane = a.fetch_reviews()


# a.extract_info_of_each_element(entities_pane)

# entities_pane.click()

# a.push_a_button_by_its_text_containing()

# this_times_entities_base_xpath = a.ENTITIES_BASE_XPATH_INIT.format(
#     to_be_confirmed=str(3)
# )

# pane = a.driver.find_elements(By.XPATH, this_times_entities_base_xpath)


# for pos in range(10):

#     # //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[5]

#     # //*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[1]

#     try_this_xpath = (
#         this_times_entities_base_xpath  # f'{this_times_entities_base_xpath}/div{pos}'
#     )
#     print(f"pos {pos}\nxpath {try_this_xpath}")
#     element_to_extract = a.driver.find_element(By.XPATH, this_times_entities_base_xpath)

#     attempt_to_extract = a.extract_info_of_each_element(element_to_extract)

#     if attempt_to_extract:
#         print(attempt_to_extract)


# b = gMapsScraper(maximum_wait_time_in_seconds=10)

# b.fetch_reviews("Souvlaki Myrina")

# b.ENTITIES_BASE_XPATH_INIT

# self = a
# # Visit the page we want
#
# driver.get(url_wanted)

# surpass_cookies(driver)
