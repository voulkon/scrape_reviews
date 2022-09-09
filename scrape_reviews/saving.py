"""
The functions that save fetched objects in our disk
Can be shared with other, future modules.

That's why they're outside the gmaps module.
"""

import datetime
import pickle
import pytz
import os

def serialize_results(
    reviews_fetched:dict,
    this_time_I_want_as_place:str, 
    this_time_I_want_as_category:str,
    directory_to_save_at:str = None) -> str:
    
    """
    Saves reviews using a filename combining 
    """
    
    #Timezone is hardcoded as that of Athens, Greece
    #TODO: make the timezone dynamic - find the system's timezone and input it in pytz.timezone()

    saved_at = datetime.datetime.now(pytz.timezone('Europe/Athens')).strftime("%Y-%m-%d_%H.%M.%S")
    
    filename = f'{this_time_I_want_as_place}_{this_time_I_want_as_category}_saved_at_{saved_at}_reviews.pkl'
    
    # If we pass something and directory_to_save_at is not None 
    if directory_to_save_at:
        # Store it there
        filename = directory_to_save_at + "\\" + filename
    else:
        filename = os.getcwd() + "\\" + filename

    with open(filename, 'wb') as outp:
        print(f'saved_at: {filename}')
        pickle.dump( reviews_fetched, outp , pickle.HIGHEST_PROTOCOL  )

    return filename

def deserialize_results(pickle_path):

    import pickle

    with open(pickle_path, 'rb') as f: x = pickle.load(f)

    return x
