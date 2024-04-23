import os
import sys


sys.path.append(os.path.join(os.getcwd(), ".."))
extensions = [
    'sphinx.ext.autodoc',
]

# Rest of your configuration...
project = "AddressBook"
copyright = "2024, VladyslavSkopenko"
author = "VladyslavSkopenko"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "nature"
html_static_path = ["_static"]
