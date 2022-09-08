
from scrape_reviews.gmaps_constants import (FOUND_IN_ATTRIBUTES, FOUND_IN_CLASSES, INFO_DICTIONARY,GENERAL_WAIT_TIME,
                                   CLASS_OF_REVIEW_CONTAINER, CLASS_OF_REVIEWS_BUTTON, REVIEWS_WINDOWS_CLASS,
                                    CLASS_OF_STARS, COOKIES_XPATH, PARENT_XPATH_OF_CATEGORIES,
                                    XPATH_OF_EACH_CATEGORY, #FIRST_ENTITY_IS_AT_THIS_POSITION_OF_ELEMENTS_OF_LEFT_PANEL,
                                    CLASS_OF_CATEGORIES_OF_INTEREST_BUTTONS
                                    )

from scrape_reviews.categories_of_interest import GoogleMapsCategories

from scrape_reviews.connect_with_sqlite_db import DbConnector

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import logging


def prettify_log_msg(msg):
        """
        Makes a msg appear like that:
        
        ****************************************************************************************************
        msg
        ****************************************************************************************************
        
        """
        return( "\n" + "*"*100 + "\n"+  msg +"\n" +"*"*100  )

def calculate_elapsed_time(func):
    """
    A decorator that calculates time needed for a function to run
    """
    import time
    import logging
    
    def func_inside_it(*args, **kwargs):

        start_time =  time.perf_counter()

        func(*args, **kwargs)

        end_time =  time.perf_counter()
        
        time_msg = "Total seconds needed for : " + func.__name__ + " " + str(end_time - start_time)

        logging.debug( prettify_log_msg(time_msg))

    return func_inside_it

def clean_one_review(
        review_element, 
        FOUND_IN_ATTRIBUTES:dict[str:str] = FOUND_IN_ATTRIBUTES, 
        FOUND_IN_CLASSES:dict[str:str] = FOUND_IN_CLASSES,
        CLASS_OF_STARS = CLASS_OF_STARS): 
    
    """
    Take one review element and return it clean.
    """

    #TODO: FOUND_IN_CLASSES & FOUND_IN_ATTRIBUTES will become properties of self
        
    this_reviews_line = {}
    for header in FOUND_IN_ATTRIBUTES:
        
        try:
            extracted = review_element.get_attribute(header)
        except:
            #An Empty String
            extracted = ""

        this_reviews_line[header] = extracted

    for info in FOUND_IN_CLASSES:
        
        try:
            extracted = review_element.find_element(By.CLASS_NAME,FOUND_IN_CLASSES[info]).text
        except:
            #An Empty String
            extracted = ""

        this_reviews_line[info] = extracted
        
    def extract_rating_from_review_stars(review_element,CLASS_OF_STARS = CLASS_OF_STARS):
        
        import re
        
        raw_stars_content = review_element.find_element(By.CLASS_NAME,CLASS_OF_STARS).get_attribute("aria-label")
        
        tbr = re.sub(r'\D', '', raw_stars_content) + '/5'

        return tbr 
        
    if this_reviews_line['rating'] == "":
        
        this_reviews_line['rating'] = extract_rating_from_review_stars(review_element=review_element, CLASS_OF_STARS = CLASS_OF_STARS)
    
    if this_reviews_line['date_created'] =="":
        
        this_reviews_line['date_created'] = review_element.find_element(By.CLASS_NAME,'rsqaWe').text
        
    
    return this_reviews_line

@calculate_elapsed_time
def scroll_down_to_reveal_all_elements(
    #xpath_of_pane_to_scroll_down:str, 
    driver,
    search_what = REVIEWS_WINDOWS_CLASS, 
    search_by = By.CSS_SELECTOR,
    #pane, 
    scroll_step:int = 5000,
    sleep_time_between_scrolls:int = 1 ):
    """
    Scrolling a pane/ part of a webpage so that all un-loaded elements get revealed 
    """    
    wait = WebDriverWait(driver,60)
    procrastinate_until_available(search_by,search_what, driver = driver)
    
    pane = driver.find_element(search_by,search_what)

    previous_height = driver.execute_script("return arguments[0].scrollHeight",pane)
    current_height = driver.execute_script("return arguments[0].scrollHeight",pane)+1

    while current_height > previous_height:

        previous_height = driver.execute_script("return arguments[0].scrollHeight",pane)

        sleep(sleep_time_between_scrolls)
        
        script_to_execute = "arguments[0].scrollTo(0, {});".format(previous_height+scroll_step)
            
        driver.execute_script(script_to_execute,pane)

        sleep(sleep_time_between_scrolls)

        current_height = driver.execute_script("return arguments[0].scrollHeight",pane)

        sleep(sleep_time_between_scrolls)

@calculate_elapsed_time
def scroll_down_to_reveal_all_reviews(
    no_of_reviews:int,
    driver,
    search_what = REVIEWS_WINDOWS_CLASS, 
    search_by = By.CSS_SELECTOR,
    #pane, 
    scroll_step:int = 5000,
    sleep_time_between_scrolls:int = 1,
    CLASS_OF_REVIEW_CONTAINER = CLASS_OF_REVIEW_CONTAINER
    ):
    """
    Scrolling the reviews pane so that all un-loaded reviews get revealed 
    """
    # from time import sleep
    # from selenium.webdriver.support.ui import WebDriverWait
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver.support import expected_conditions as EC
    # import logging

    #sleep(1)
    
    
    procrastinate_until_available(search_by,search_what, driver = driver)
    
    pane = driver.find_element(search_by,search_what)

    no_of_reviews_right_now = len(driver.find_elements(By.CLASS_NAME,  CLASS_OF_REVIEW_CONTAINER ))

    logging.debug( prettify_log_msg(f'no_of_reviews before entering the while: {no_of_reviews_right_now}') )

    trials = 0
    while no_of_reviews_right_now < no_of_reviews and trials < 10 :

        sleep(sleep_time_between_scrolls)
        
        previous_height = driver.execute_script("return arguments[0].scrollHeight",pane)
        
        logging.debug(f' Pane Height : {previous_height}')

        script_to_execute = "arguments[0].scrollTo(0, {});".format(previous_height+scroll_step)
            
        driver.execute_script(script_to_execute,pane)

        sleep(sleep_time_between_scrolls)
        
        current_height = driver.execute_script("return arguments[0].scrollHeight",pane)
        
        if current_height > previous_height:
            trials = 0
        else:
            print_trials = str(trials+1)
            logging.info(f'Stuck in scrolling. Trial Number: {print_trials}')
            trials += 1

        no_of_reviews_right_now = len(driver.find_elements(By.CLASS_NAME,  CLASS_OF_REVIEW_CONTAINER ))
        
        sleep(sleep_time_between_scrolls)

def extract_info_of_each_element(specific_element, INFO_DICTIONARY:str = INFO_DICTIONARY) -> dict[str]:
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
        specific_element.find_element( By.CLASS_NAME,INFO_DICTIONARY['Name'] )

    except:
        # If entity's name is not found, the element we've clicked on does not contain an entity
        # Most probably we've cleaned all entites and we're examining 
        # the very bottom elements of the page
        # By returning None, we signal to the fetch_reviews function that the entities are finished
        return None

    try:
        # Fetch info for each element - the name, the rating, etc.
        clean_info = {info : specific_element.find_element( By.CLASS_NAME,INFO_DICTIONARY[info] ).text  for info in INFO_DICTIONARY}
        
    #In case it has no reviews
    except:
        # Return N/A as string and the Name
        clean_info = {info : "N/A"  for info in INFO_DICTIONARY if info not in ['Name'] }
        clean_info['Name'] = specific_element.find_element( By.CLASS_NAME,INFO_DICTIONARY['Name'] ).text
        

    return clean_info

@calculate_elapsed_time
def expand_collapsed_reviews(driver):

    """Presses all "More" Buttons to reveal reviews' text"""
    
    keywords_to_look_for = ['Περισσότερα', 'More', 'more', 'Más' ,'Mas']

    more_text_buttons = []
    
    for keyword_to_look_for in keywords_to_look_for:

        search_result = driver.find_elements(By.XPATH,("//button[text()='{}']".format(keyword_to_look_for)))

        if len(search_result) > 0:
            for text_button in search_result:
                more_text_buttons.append(text_button)
    
    #TODO: include other languages too: more, mas, etc. 

    for b,more_text_button in enumerate(more_text_buttons):
        try:
            more_text_button.click()
        except:
            continue

def return_proper_position_of_variable_path_part(driver,entities_base_xpath) -> str:
    """
    A part of an xpath is dependent on whether this specific place has additional details,
    e.g. a small section warning about covid measures before the reviews
    
    This addition would displace part of the expected XPATH from div[2] to div[3]
    """
    # import logging
    
    for p in [3,2,1,4,5]:

        logging.debug(prettify_log_msg("return_proper_position_of_variable_path_part trying " + str(p)) )
        
        test_xpath = entities_base_xpath.format(to_be_confirmed = p, entity_position = 5)

        procrastinate_until_available(By.XPATH, test_xpath, driver, no_of_attempts=2, wait_time = 2 )

        test_element = driver.find_elements(By.XPATH, test_xpath)

        if test_element:

            logging.info( prettify_log_msg("Variable part for this case is " + str(p)) )
            
            return str(p)

#@calculate_elapsed_time
def procrastinate_until_available(search_by, search_what, driver,no_of_attempts = 2, wait_time = 20 ):
    """
    A function that forces a chrome driver to wait until a certain element (identified by the search_by and search_what)
    
    Probably useless. 
    
    The same can be achieved with longer wait_time in a WebDriverWait
    instead of iterating over many smaller ones.
    """
    import logging
    # We'll give it #no_of_attempts shots (each one c), 
    # in case it's loading too slowly
    # We need to account for the fact that the element does not exist at all (in contrast with existing but takes time to load)
    for r in range(no_of_attempts):

        try:
            wait = WebDriverWait(driver,wait_time)
            wait.until(EC.presence_of_element_located((search_by,search_what)))
            return None

        except:
            # If the try was unsuccessful (it returned an error)
            # Go to the next iteration 
            # e.g. from r == 0 --> r == 1
            logging.debug(  f" Attempt {str(r+1)} was unsuccessful. Heading for the attempt no. {str(r+2)}" )
            pass

def clean_one_entitys_reviews(
    no_of_reviews:int, 
    regards_entity:str, 
    driver,  
    fetched_at:str, 
    search_what = REVIEWS_WINDOWS_CLASS, 
    search_by = By.CSS_SELECTOR, 
    CLASS_OF_REVIEWS_BUTTON = CLASS_OF_REVIEWS_BUTTON, 
    REVIEWS_WINDOWS_CLASS = REVIEWS_WINDOWS_CLASS,
    this_sessions_connector = None
    ) -> dict[list[str]]:
    """
    Returns all reviews for an entity.
    """
    # import pandas as pd
    # import logging

    #reviews_window = driver.find_element(search_by,search_what)
    
    scroll_down_to_reveal_all_reviews(no_of_reviews = no_of_reviews,  driver = driver,  sleep_time_between_scrolls = GENERAL_WAIT_TIME  )

    expand_collapsed_reviews(driver = driver)

    reviews_of_this_entity = driver.find_elements(By.CLASS_NAME,  CLASS_OF_REVIEW_CONTAINER )
    
    logging.debug( prettify_log_msg(f'Number of children nodes after the scrolling: {len(reviews_of_this_entity)}. Total Expected Reviews: {no_of_reviews} ') )
    
    if this_sessions_connector:
        
        for rev in reviews_of_this_entity:
            
            this_sessions_connector.insert_values_in_table(
                table_waned = "reviews", 
                items = clean_one_review(rev)
                )
            
    else:
        
        this_entitys_reviews_clean = [clean_one_review(rev) for rev in reviews_of_this_entity]
    
    
        def merge_dictionary_list(dict_list):
            # From Alex Hall: https://stackoverflow.com/users/2482744/alex-hall 
            return {
                k: [d.get(k) for d in dict_list if k in d] # explanation A
                for k in set().union(*dict_list) # explanation B
                    }
    
        this_entitys_reviews_clean = merge_dictionary_list(this_entitys_reviews_clean)
        
        logging.debug( prettify_log_msg(f'Number of cleaned reviews (as dictionaries): {len(this_entitys_reviews_clean)}. Total Expected Reviews: {no_of_reviews} ') )
        
        no_of_reviews_cleaned = len(this_entitys_reviews_clean["data-review-id"])
    
        this_entitys_reviews_clean["regards_entity"] = [regards_entity] * no_of_reviews_cleaned
    
        this_entitys_reviews_clean["fetched_at"] =  [fetched_at] * no_of_reviews_cleaned
        
        logging.info( prettify_log_msg(f'Number of reviews cleaned: {no_of_reviews_cleaned}. Total Expected Reviews: {no_of_reviews} ') )
        
        return this_entitys_reviews_clean

@calculate_elapsed_time
def surpass_cookies(driver, COOKIES_XPATH = COOKIES_XPATH):
    
    """Presses the accept cookies button"""

    try:
        cookies_button = driver.find_element(By.XPATH,COOKIES_XPATH)
    except:
        print("Cookies button not found - perhaps they have been already handled")
        return None
    
    try:
        cookies_button.click()
    except:
        print("An error occurred. Run the code to debug it.")
    
def category_in_proper_language(categories_of_interest_buttons, GoogleMapsCategory = GoogleMapsCategories.HOTELS ):
    """
    The text displayed for each category in Google Maps depends on our language.
    This function takes care to identify the proper one.
    
    For example, 
        The user might have passed the keyword "hotels" in the fetch_gmaps_reviews()
        And the actual category of Hotels is displayed as "hoteles" 
        (because it's appearing in spanish)

        This function will return "hoteles".

    """
    existing_keys = categories_of_interest_buttons.keys()

    for key in existing_keys:
        
        for category_in_a_specific_lang in GoogleMapsCategory:
            
            if key.lower() == category_in_a_specific_lang:
                
                return key

    print("This Category is not found")    
    return None

def find_entities_base_xpath_init(GoogleMapsCategory, XPATH_OF_EACH_CATEGORY:dict = XPATH_OF_EACH_CATEGORY ):
    
    for xpath,categories in XPATH_OF_EACH_CATEGORY.items():

        for cat in categories:

            for category_in_a_specific_lang in GoogleMapsCategory: 
               
                if cat == category_in_a_specific_lang:
                    return xpath
             

    print("This Category is not found")    
    return None 

@calculate_elapsed_time
def prepare_left_pane(driver, entities_base_xpath_init, sleep_time_between_scrolls_):
    """Takes care to scroll down until all elements are revealed"""

    procrastinate_until_available( By.XPATH,entities_base_xpath_init, driver = driver )
    
    entities_base = driver.find_element(By.XPATH,entities_base_xpath_init)

    scroll_down_to_reveal_all_elements(
        search_by = By.XPATH,
        search_what = entities_base_xpath_init,
        driver = driver,
        sleep_time_between_scrolls = sleep_time_between_scrolls_
    )

def fetch_reviews(
    driver,
    entities_base_xpath:str, 
    fetched_at:str, 
    fetched_looking_at_place:str,
    this_sessions_connector = None
    ):
    """
    This function starts when we've loaded all available entities (hotels, restaurants, etc.)
    """
    
    def merge_dictionary_list(dict_list):
        # From Alex Hall: https://stackoverflow.com/users/2482744/alex-hall 
        return {
            k: [d.get(k) for d in dict_list if k in d] # explanation A
            for k in set().union(*dict_list) # explanation B
                }

    def find_where_first_entity_is(driver, entities_base_xpath = entities_base_xpath ):

        for try_position in range(10):
            temp_position = entities_base_xpath.format( entity_position = try_position )
            try:
                extracted = extract_info_of_each_element( driver.find_element(By.XPATH, temp_position ))
                if isinstance(extracted,dict):
                    if extracted["Name"] != "":
                        return try_position
            except:
                continue

        return None
    
    this_entitys_number = find_where_first_entity_is(driver = driver, entities_base_xpath = entities_base_xpath )
    
    all_info = []
    all_reviews = []

    time_to_break = False

    try:
            
        while not time_to_break:

            next_entitys_xpath = entities_base_xpath.format( entity_position = this_entitys_number )
            
            try:

                #Header - info regarding the whole entity and referring to many reviews
                procrastinate_until_available(By.XPATH, next_entitys_xpath, driver = driver)
                specific_element = driver.find_element(By.XPATH, next_entitys_xpath)
                specific_elements_info =  extract_info_of_each_element(specific_element)
                
                specific_elements_info['fetched_at'] = fetched_at
                specific_elements_info['fetched_looking_at_place'] = fetched_looking_at_place
                this_entitys_name = specific_elements_info['Name']
                this_entitys_number +=2
                
                this_entitys_name_already_exists = any([this_entitys_name in ent['Name'] for ent in all_info])

                logging.info(  prettify_log_msg("Now Scraping reviews for : " + this_entitys_name)  )
                
                if this_sessions_connector:
                    
                    #Make it a tuple
                    values_for_db = (val for val in specific_elements_info.values())
                    
                    #Append or ignore
                    this_sessions_connector.insert_values_in_table(table_wanted = 'entity_info',  items = values_for_db )

            except:
                #In case specific_elements_info didn't go as expected
                print("No More Entities to Scrape")
                break

            if specific_elements_info['Number_of_Ratings'] == 'N/A':
                
                logging.info(prettify_log_msg(f'{this_entitys_name} has no reviews. Moving On to the next. '))
                
                continue


            if this_entitys_name_already_exists:

                logging.info( prettify_log_msg( f'We\'ve already scraped {this_entitys_name}. Moving On to the next.' ))
                
                continue
            
            
            ### Click on the Entity ###
            logging.debug( prettify_log_msg( f'Preparing to click on reviews of {this_entitys_name}.' ))
            procrastinate_until_available(By.XPATH, next_entitys_xpath, driver = driver)
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_entitys_xpath))).click()
                logging.debug( f' Clicked on {this_entitys_name} on first attempt.' )
            except:
                sleep(1)
                logging.debug(f'Didn\'t manage to click on {this_entitys_name} on first attempt. Trying again to click on entity.')
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_entitys_xpath))).click()
                    logging.debug( f' Clicked on {this_entitys_name} on second attempt.' )
                except:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_entitys_xpath))).click()
                    logging.debug( f' Clicked on {this_entitys_name} on third attempt.' )
   
            procrastinate_until_available(By.CLASS_NAME, CLASS_OF_REVIEWS_BUTTON, driver = driver)
            #reviews_element = driver.find_element(By.CLASS_NAME, CLASS_OF_REVIEWS_BUTTON)
              
            #logging.info("Before finding the reviews_window")   
            procrastinate_until_available(By.CSS_SELECTOR, REVIEWS_WINDOWS_CLASS, driver = driver)
            #reviews_window = driver.find_element(By.CSS_SELECTOR, REVIEWS_WINDOWS_CLASS)
            
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, CLASS_OF_REVIEWS_BUTTON))).click()
                logging.info( f' Clicked on reviews of {this_entitys_name} on first attempt.' )
                
            except:

                logging.info(f'Didn\'t manage to click on reviews of {this_entitys_name} on first attempt. Trying again to click on entity.')
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, CLASS_OF_REVIEWS_BUTTON))).click()
                
                logging.info( f' Clicked on reviews of {this_entitys_name} on first attempt.' )

            logging.debug(f'sleeping for {GENERAL_WAIT_TIME}')

            sleep(GENERAL_WAIT_TIME)
            
            no_of_reviews = int(specific_elements_info['Number_of_Ratings'].replace("(","").replace(")",""))

            logging.info( f'Entering this_entitys_reviews. Expecting to extract {no_of_reviews} reviews'  )
            
            this_entitys_reviews = clean_one_entitys_reviews(no_of_reviews = no_of_reviews, 
                                                             driver = driver, 
                                                             regards_entity = this_entitys_name,
                                                             fetched_at = fetched_at,
                                                             this_sessions_connector = this_sessions_connector
                                                             )
            
            if not specific_elements_info: # equals if it's extract_info_of_each_element has returned None     
                
                logging.debug("in the specific_elements_info is null")
                break

            else:
                  
                #logging.info(prettify_log_msg(f'Scraped: {this_entitys_name} . Cleaned {this_entitys_reviews.shape[0]} reviews'))
                
                all_info.append(specific_elements_info)
                all_reviews.append(this_entitys_reviews)

    except KeyboardInterrupt:
    
        logging.info('KeyboardInterrupt exception is caught. So far cleaned ' , len(all_info) , ' Overall info.')
    
        return { "entity_info": merge_dictionary_list(all_info),"reviews" : merge_dictionary_list(all_reviews) }
        
    finally:

        return { "entity_info": merge_dictionary_list(all_info),"reviews" : merge_dictionary_list(all_reviews) }

def fetch_gmaps_reviews(
    category_wanted:str, 
    place_wanted:str, 
    search:bool = False,
    local_chromedriver_position:str = None,
    entities_base_xpath_init:str = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[{to_be_confirmed}]/div[1]',
    position_of_db_to_append_results:str = None
    ) -> list:

    """
    The main function

    It can either: 
        - scan a specific place (e.g. Nauru, Aspen, Punta Cana) using the search = False argument (the default) or
        - make a more generic search query  (e.g. Burgers in Myrina or Bungallows in Fiji) using the search = True
    
    Parameters
    ----------
    category_wanted : str

        A keyword signifying which category of interest (hotels, restaurants, museums, etc) 
        we want to scrape.

        As of Sep of 2022, it can only handle:
            Hotels
            Restaurants

        And it can work with the following 5 languages: 
        EN, PT, ES, EL , FR

        For example, for a computer that launches google:

        in the english language a user needs to provide the keyword  "hotels",
        in the french language a user needs to provide the keyword  "hôtels"
        in portuguese the word "hotéis",
        in greek the word "ξενοδοχεία",
        in spanish the word "hoteles"

    place_wanted:str
        A [city / village/ island / place in general] name.

    search:bool
        whether we want to search Google Maps instead of 
        generally looking for a place

        For example, 
        If we pass:

            place_wanted = "Souvlaki in Myrina"
        
        That's a keyword aiming conduct a search in Google Maps
        and it's the same as typing plain "Myrina" 

    local_chromedriver_position:str
        A path, in case the chromedriver executable is already downloaded.

        If not provided, the ChromeDriverManager().install() will handle it.
    
    entities_base_xpath_init:str
        The xpath of the column (in the left part of the window) that contains the reviews
    
    #TODO: Document this db position
    position_of_db_to_append_results:str
    
    Returns:
    -------
    A list containing two pd.DataFrames:
        One with info regarding the whole entity (be it hotel or restaurant)
        One with reviews

    """
    
    #import time
    import datetime
    import pytz
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import logging

    from scrape_reviews.categories_of_interest import GoogleMapsCategories
    
    will_work_with_db = position_of_db_to_append_results is not None
    
    #Initiate or set as None
    this_sessions_connector = DbConnector(db_name = position_of_db_to_append_results) if will_work_with_db else None
    
    def from_one_languages_text_to_a_list_of_all(category_wanted:str,attributes:list[tuple]) -> list[str]:

        """
        Takes a keyword in one language (e.g. hoteles) and attributes of the GoogleMapsCategories class and returns the list with the word in all languages
        
        Parameters
        ----------
        category_wanted : str
        e.g. hoteles

        attributes : list of tuples
        e.g.
        [
            ('HOTELS', ['hotels', 'hotéis', 'hoteles', 'ξενοδοχεία', 'hôtels']),
            ('RESTAURANTS', ['restaurants', 'εστιατόρια', 'restaurantes', 'Gaststätten']),
            ('__class__', <class 'type'>)
        ]
        
        Returns:
        -------
        A list:
            e.g. ['hotels', 'hotéis', 'hoteles', 'ξενοδοχεία', 'hôtels']

        """
        
        #TODO: A test where it takes 'hotéis' and returns the list, etc.
        
        attributes_we_will_iterate_over = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
        attributes_as_dict = { att[0]:att[1] for att in attributes_we_will_iterate_over }
        
        for h in attributes_we_will_iterate_over:

            for lang in h[1]:

                if category_wanted == lang:
                    
                    return (attributes_as_dict[h[0]])

        #If nothing's found     
        return None

    #if isinstance(category_wanted,str):
        
        import inspect

        attributes = inspect.getmembers(GoogleMapsCategories, lambda a:not(inspect.isroutine(a)))
        
        category_wanted = from_one_languages_text_to_a_list_of_all(category_wanted,attributes )
  
        #logging.info(f"category_wanted {(category_wanted[0])}")

    #Keep a timestamp to know when each dataset was extracted
    fetched_at = datetime.datetime.now(pytz.timezone('Europe/Athens')).strftime("%d-%m-%Y_%H.%M.%S")
    logging.debug(f"Fetched at: {fetched_at}")

    # We initiate the driver, this will be our vehicle throughout the scraping session
    # A chrome browser will open and 
    # several actions (like scrolling and waiting for the page to refresh) will take place through it 
    use_local_chromedriver = local_chromedriver_position is not None
    if use_local_chromedriver:
        driver = webdriver.Chrome(local_chromedriver_position)
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install())


    search_or_place_part = 'search' if search else 'place'
    url_wanted = f'https://www.google.com/maps/{search_or_place_part}/{place_wanted}'

    # Visit the page we want
    logging.info(prettify_log_msg(f'Trying url: {url_wanted}'))
    driver.get(url_wanted)

    # If prompted with cookies, accept them
    surpass_cookies(driver)
    logging.debug("Just passed cookies")

    # We want the categories button on top of the window
    # They need time to load, depending on our connection's speed
    if not search:

        procrastinate_until_available(search_by=By.XPATH, search_what=PARENT_XPATH_OF_CATEGORIES, driver = driver)
        
        # Then, locate the node of categories
        parent_node_of_categories = driver.find_elements(By.XPATH, PARENT_XPATH_OF_CATEGORIES )
   
        logging.debug( prettify_log_msg("parent_node_of_categories has {} categories in it".format(str(len(parent_node_of_categories))))  )

        # Fetch them
        categories_of_interest_buttons = {elem.text:elem  for elem in driver.find_elements(By.CLASS_NAME,CLASS_OF_CATEGORIES_OF_INTEREST_BUTTONS) }
        logging.info( prettify_log_msg(" Categories are : " + " , ".join([k for k in categories_of_interest_buttons.keys()]))  )

        
        # Locate the specific category (e.g. hotels)
        category_wanted_ = category_in_proper_language(categories_of_interest_buttons = categories_of_interest_buttons, GoogleMapsCategory = category_wanted )
        logging.info( prettify_log_msg("The keyword we want in our language is: " + category_wanted_) )

        # Click on it 
        categories_of_interest_buttons[category_wanted_].click()
        logging.debug( prettify_log_msg("And we just clicked it") )

    entities_base_xpath =  entities_base_xpath_init + '/div[{entity_position}]'
      
    numeric_variable_part = return_proper_position_of_variable_path_part(driver = driver,entities_base_xpath = entities_base_xpath)
    
    entities_base_xpath_init = entities_base_xpath_init.format(to_be_confirmed = numeric_variable_part)

    entities_base_xpath =  entities_base_xpath_init + '/div[{entity_position}]'
    
    logging.info( prettify_log_msg("entities_base_xpath: " + str(entities_base_xpath)) )
    
    # Start scrolling until our webpage gets updated with all available info
    prepare_left_pane(sleep_time_between_scrolls_= 1.5, driver = driver, entities_base_xpath_init = entities_base_xpath_init)

    this_towns_reviews = fetch_reviews(
        fetched_looking_at_place = place_wanted, 
        driver = driver, fetched_at=fetched_at , 
        entities_base_xpath = entities_base_xpath,
        this_sessions_connector = this_sessions_connector
        )

    return this_towns_reviews
