======================
sphinx_multitheme_ext
======================

.. warning:: this is very rough implemented extension.


`sphinx_multitheme_ext` the sphinx extension support 2 features.

1. Specifies a template for each page (regex matching).
2. Specifies a theme for each page (regex matching).


Specifies a template for each page
====================================

configure in conf.py:

.. code-block:: python

   html_page_template = {
       # eg. 'regex-path', 'template-name',
       r'^egg.*': 'egg.html',
   }


Specifies a theme for each page
====================================

configure in conf.py:

.. code-block:: python

   html_multi_themes = {
       # eg. 'regex-path', ('theme-name', theme_options),
       r'.*bar.*': ('agogo', {}),
       r'^foo1.*': ('haiku', {}),
   }


LICENSE
=========

MIT License. see also: http://shimizukawa.mit-license.org/

