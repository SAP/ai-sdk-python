import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

import tomllib

project = 'SAP Cloud SDK for AI (Python) - base'
copyright = '2026, SAP SE'
author = 'SAP SE'

def get_version():
    pyproject = pathlib.Path(__file__).parents[2] / 'pyproject.toml'
    with open(pyproject, 'rb') as f:
        return tomllib.load(f)['project']['version']

release = get_version()

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinxawesome_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

smartquotes = False
html_title = "SAP Cloud SDK for AI (Python) - base v" + release
html_permalinks = False

autodoc_typehints = "description"
autodoc_class_signature = "separated"
add_module_names = False
autodoc_typehints_format = 'short'
autodoc_member_order = 'groupwise'
modindex_common_prefix = ['ai_api_client_sdk']
