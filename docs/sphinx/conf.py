project = "SAP AI SDK Python"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
html_theme = "furo"
exclude_patterns = ["_autogen/*/modules.rst"]
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "show-inheritance": True,
    "special-members": "__init__",
}
autodoc_member_order = "bysource"
html_copy_source = False
