
class GoogleMapsCategories(object):
    """
    Instead of text that can take any form including potential typos, (hotels, Htels, etc. )
    Let's standardize them with this set
    """

    HOTELS = ["hotels", "hotéis", "hoteles","ξενοδοχεία", "hôtels"] #"hotels" #
    RESTAURANTS = ["restaurants","εστιατόρια", "restaurantes", "Gaststätten"] # "restaurants" #
