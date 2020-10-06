# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

import recommonmark
from recommonmark.transform import AutoStructify

# -- Project information -----------------------------------------------------

project = 'Pluma Automation'
copyright = '2020, Witekio'
author = 'Witekio'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.apidoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'recommonmark'
]


# API docs generation
apidoc_module_dir = '../pluma'
apidoc_output_dir = '_api'
# apidoc_excluded_paths = ['tests']
apidoc_separate_modules = True

# Recommonmark
autosectionlabel_prefix_document = True


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

master_doc = 'index'

# Recommonark
def setup(app):
    app.add_config_value('recommonmark_config', {
            'auto_toc_tree_section': 'Contents',
            }, True)
    app.add_transform(AutoStructify)