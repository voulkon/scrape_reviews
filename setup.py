import os
import setuptools

required = [
    "pandas",
    "webdriver_manager == 3.8.3",
    "selenium >= 4.1.0",
    "elasticsearch >=8.5.3",
    "pyperclip>=1.8.2",
]


setuptools.setup(
    # license="MIT",
    # #long_description=long_description,
    # #long_description_content_type="text/markdown",
    # url="https://github.com/voulkon/scrape_reviews",
    install_requires=required,
    keywords=[
        "scrape",
        "reviews",
        "maps",
        "google",
        "gmaps",
        "hotels",
        "restaurants",
        "hotel_reviews",
        "restaurant_reviews",
    ],
    # project_urls = {"Source Code":"https://github.com/voulkon/scrape_reviews"},
    # packages=setuptools.find_packages(),
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
)
