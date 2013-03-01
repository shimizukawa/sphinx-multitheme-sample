# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.abspath('.'))
extensions = ['sphinx_multitheme_ext']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'multi-theme'
copyright = u'2013, shimizukawa'
version = release = '0.1'
exclude_patterns = ['_build']

html_theme = 'default'


##########################
# sphinx_multitheme_ext

html_multi_themes = {
    # eg. 'regex-path', ('theme-name', theme_options),
    r'.*bar.*': ('agogo', {}),
    r'^foo1.*': ('haiku', {}),
}

html_page_template = {
    # eg. 'regex-path', 'template-name',
    r'^egg.*': 'egg.html',
}
