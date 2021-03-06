from Products.CMFCore.interfaces import IFolderish
from osha.hwccontent.interfaces import IMaterialsView
from osha.hwccontent.browser.helper import get_path_to_icon
from plone.app.textfield.interfaces import IRichTextValue
from five import grok
from zope import interface

import logging

log = logging.getLogger(__name__)
grok.templatedir('templates')


@interface.implementer(IMaterialsView)
class MaterialsView(grok.View):
    grok.name('folder_materials_view')
    grok.context(IFolderish)
    grok.template('folder_materials_view')

    def get_icon_path(self, obj, content_type=None):
        return get_path_to_icon(obj, content_type)

    @property
    def disclaimer(self):
        item = getattr(self.context, 'disclaimer', None)
        value = item and getattr(item, 'text', None)
        if value:
            if IRichTextValue.providedBy(value):
                return value.output
            else:
                return value
        return ""
