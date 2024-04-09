import os
import sys

sys.path.append(
    os.path.abspath(
        "..",
    )
)
sys.path.insert(0, os.path.abspath("../"))
sys.path.append(os.path.join(os.getcwd(), "..", ".."))
project = "AddressBook"
copyright = "2024, VladyslavSkopenko"
author = "VladyslavSkopenko"


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "nature"
html_static_path = ["_static"]
