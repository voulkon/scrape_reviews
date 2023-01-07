from dotenv import dotenv_values, find_dotenv
from elasticsearch import Elasticsearch
from uuid import uuid4
import pandas as pd
import numpy as np
import random

config = dotenv_values(find_dotenv())
my_api_key = config['ELASTIC_CLOUD_API_KEY']
CLOUD_ID = config['ELASTIC_CLOUD_ID']

# Create the client instance
client = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=my_api_key
)

client.info()

# FIND SOME REVIEWS ##
reviews_file = r"C:\Users\kvoul\Downloads\amazon_uk_shoes_products_dataset_2021_12.csv"
all_reviews = pd.read_csv(reviews_file)

random_no_of_reviews = random.randint(100, 2000)

random_ind_of_reviews = np.random.choice(
    all_reviews.shape[0], random_no_of_reviews)

reviews_to_send = all_reviews.iloc[random_ind_of_reviews]


for r in range(reviews_to_send.shape[0]):

    this_reviews = reviews_to_send.iloc[r]
    this_reviews_clean = this_reviews.dropna()
    doc_in_proper_form = this_reviews_clean.to_dict()

    client.create(
        index=config['WANTED_INDEX_TO_APPEND'],
        id=uuid4(),
        document=doc_in_proper_form)


# docs_to_delete = ['98e70c77-bfb3-45ba-b7b5-fcece8839cb4', '7297b346-72c5-45b8-b1e4-4f5d0889be68' ]

# for doc_to_delete in docs_to_delete:
#     client.delete(index = config['WANTED_INDEX_TO_APPEND'], id = doc_to_delete)

# sample_data = {
#     "name": "George Dooe",
#     "address": {
#         "country": "USA",
#         "state": "New York",
#         "city": "New York"
#     },
#     "review": "I love it so much. It made my life way easier!"
# }
