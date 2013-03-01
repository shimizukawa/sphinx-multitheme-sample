# -*- coding: utf-8 -*-
"""
#conf.py settings to use this extension.


extensions = ['sphinx_multitheme_ext']

html_theme = 'default'

html_multi_themes = {
    # eg. 'regex-path', ('theme-name', theme_options),
    r'^foo.*': ('haiku', {}),
    r'^bar/.*': ('pyramid', {}),
}

html_page_template = {
    # eg. 'regex-path', 'template-name',
    r'^egg.*': 'egg.html',
}

"""

import re
from os import path, makedirs
import codecs

from sphinx.theming import Theme
from sphinx.builders import html
from sphinx.util import copy_static_entry
from sphinx.util.osutil import os_path, relative_uri, ensuredir, copyfile


def init_multi_templates(self):
    self.multithemes = {}
    for key, (themename, themeoptions) in self.config.html_multi_themes.items():
        matcher = re.compile(key)
        theme, options = (Theme(themename), themeoptions.copy())
        templates = create_template_bridge(self)
        templates.init(self, theme)
        self.multithemes[matcher] = theme, options, templates


def create_template_bridge(self):
    """Return the template bridge configured."""
    if self.config.template_bridge:
        templates = self.app.import_object(
            self.config.template_bridge, 'template_bridge setting')()
    else:
        from sphinx.jinja2glue import BuiltinTemplateLoader
        templates = BuiltinTemplateLoader()
    return templates


def theme_context(theme, options):
    ctx = {}
    stylename = theme.get_confstr('theme', 'stylesheet')
    ctx['style'] = theme.name + '/' + stylename
    ctx.update(
        ('theme_' + key, val) for (key, val) in
        theme.get_options(options).iteritems())
    return ctx


def handle_page(self, pagename, addctx, templatename='page.html',
                outfilename=None, event_arg=None):
    ctx = self.globalcontext.copy()
    # current_page_name is backwards compatibility
    ctx['pagename'] = ctx['current_page_name'] = pagename
    default_baseuri = self.get_target_uri(pagename)
    # in the singlehtml builder, default_baseuri still contains an #anchor
    # part, which relative_uri doesn't really like...
    default_baseuri = default_baseuri.rsplit('#', 1)[0]

    def pathto(otheruri, resource=False, baseuri=default_baseuri):
        if resource and '://' in otheruri:
            # allow non-local resources given by scheme
            return otheruri
        elif not resource:
            otheruri = self.get_target_uri(otheruri)
        uri = relative_uri(baseuri, otheruri) or '#'
        return uri
    ctx['pathto'] = pathto
    ctx['hasdoc'] = lambda name: name in self.env.all_docs
    if self.name != 'htmlhelp':
        ctx['encoding'] = encoding = self.config.html_output_encoding
    else:
        ctx['encoding'] = encoding = self.encoding
    ctx['toctree'] = lambda **kw: self._get_local_toctree(pagename, **kw)
    self.add_sidebars(pagename, ctx)
    ctx.update(addctx)

    for key, _templatename in self.config.html_page_template.items():
        matcher = re.compile(key)
        if matcher.match(pagename):
            templatename = _templatename

    self.app.emit('html-page-context', pagename, templatename,
                  ctx, event_arg)

    try:
        for matcher in self.multithemes:
            if matcher.match(pagename):
                theme, options, templates = self.multithemes[matcher]
                ctx.update(theme_context(theme, options))
                break
        else:
            templates = self.templates

        output = templates.render(templatename, ctx)

    except UnicodeError:
        self.warn("a Unicode error occurred when rendering the page %s. "
                  "Please make sure all config values that contain "
                  "non-ASCII content are Unicode strings." % pagename)
        return

    if not outfilename:
        outfilename = self.get_outfilename(pagename)
    # outfilename's path is in general different from self.outdir
    ensuredir(path.dirname(outfilename))
    try:
        f = codecs.open(outfilename, 'w', encoding, 'xmlcharrefreplace')
        try:
            f.write(output)
        finally:
            f.close()
    except (IOError, OSError), err:
        self.warn("error writing file %s: %s" % (outfilename, err))
    if self.copysource and ctx.get('sourcename'):
        # copy the source file for the "show source" link
        source_name = path.join(self.outdir, '_sources',
                                os_path(ctx['sourcename']))
        ensuredir(path.dirname(source_name))
        copyfile(self.env.doc2path(pagename), source_name)


def copy_static_theme_files(self):
    # then, copy over theme-supplied static files
    for theme, options, templates in self.multithemes.values():
        ctx = self.globalcontext.copy()
        ctx.update(self.indexer.context_for_searchtool())
        ctx.update(theme_context(theme, options))

        themeentries = [path.join(themepath, 'static')
                        for themepath in theme.get_dirchain()[::-1]]
        theme_static_dir = path.join(self.outdir, '_static', theme.name)
        if not path.exists(theme_static_dir):
            makedirs(theme_static_dir)
        for entry in themeentries:
            copy_static_entry(entry, theme_static_dir, self, ctx)


def patch():
    init_templates = html.StandaloneHTMLBuilder.init_templates
    copy_static_files = html.StandaloneHTMLBuilder.copy_static_files
    def init(self):
        init_templates(self)
        init_multi_templates(self)

    def copy_files(self):
        copy_static_files(self)
        copy_static_theme_files(self)

    html.StandaloneHTMLBuilder.init_templates = init
    html.StandaloneHTMLBuilder.handle_page = handle_page
    html.StandaloneHTMLBuilder.copy_static_files = copy_files



def setup(app):
    app.add_config_value('html_multi_themes', {}, True)
    app.add_config_value('html_page_template', {}, True)
    patch()
