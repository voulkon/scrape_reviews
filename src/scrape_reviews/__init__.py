# -*- coding: utf-8 -*-
"""

The gmaps module contains functions that attempt to scrape
all reviews for a certain place or search term.

"""

#

__docformat__ = "restructuredtext"

#Check that hard dependencies exist
# Let users know if they're missing
_hard_dependencies = ("pandas", "selenium", "pytz", "webdriver_manager")
_missing_dependencies = []

for _dependency in _hard_dependencies:
    
    try:
        __import__(_dependency)
    except ImportError as _e:
        _missing_dependencies.append(f"{_dependency}: {_e}")

if _missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(_missing_dependencies)
    )
del _hard_dependencies, _dependency, _missing_dependencies
