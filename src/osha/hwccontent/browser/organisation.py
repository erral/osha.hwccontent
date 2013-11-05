# _+- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from five import grok
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.directives import dexterity
from osha.hwccontent.organisation import IOrganisation
import logging

log = logging.getLogger(__name__)

grok.templatedir("templates")


class View(dexterity.DisplayForm):
    grok.context(IOrganisation)
    grok.require('zope2.View')
    grok.template("organisation")

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def get_events(self):
        results = self.portal_catalog(
            portal_type='plone.app.event.dx.event',
            path='/'.join(self.context.getPhysicalPath()))
        return [x.getObject() for x in results]

    def get_news(self):
        results = self.portal_catalog(
            portal_type='News Item',
            path='/'.join(self.context.getPhysicalPath()))
        return [x.getObject() for x in results]

    def get_news_folder_url(self):
        try:
            return self.context.restrictedTraverse('news').absolute_url()
        except KeyError:
            return ''

    def get_events_folder_url(self):
        try:
            return self.context.restrictedTraverse('events').absolute_url()
        except KeyError:
            return ''


class PostAddView(grok.View):
    grok.context(IOrganisation)

    def render(self):
        properties = api.portal.get_tool('portal_properties')
        fallback = self.context.__parent__.absolute_url()
        url = getattr(
            properties.site_properties,
            'organisation_added_page',
            fallback
        )
        if not url.startswith('http'):
            try:
                obj = self.context.restrictedTraverse(url)
                url = obj.absolute_url()
            except:
                log.warn('Could not get feedback page: {0}'.format(url))
                url = fallback
        api.portal.show_message('Profile has been created',
                                request=self.request)
        self.redirect(url)


class OrganisationManage(ViewletBase):
    """ Manage organisation (OCP) in the themed site """

    def update(self):
        # get user etc
        if api.user.is_anonymous():
            self.can_review = False
            self.can_edit = False
            self.can_delete = False
            user_email = None
        else:
            user = api.user.get_current()
            user_email = user.getProperty('email')
            self.can_review = bool(user.checkPermission(
                'Review portal content', self.context))
            self.can_edit = bool(user.checkPermission(
                'Modify portal content', self.context))
            self.can_delete = bool(user.checkPermission(
                'Delete objects', aq_parent(self.context)))
        self.contenttype = self.context.Type()
        workflow = api.portal.get_tool('portal_workflow')
        self.wfactions = dict()
        for action in workflow.listActions(object=self.context):
            action['name'] = action['name'].format(
                contenttype=self.contenttype)
            self.wfactions[action['id']] = action
        self.wfstate = workflow.getInfoFor(self.context, 'review_state')
        self.wfstatetitle = workflow.getTitleForStateOnType(
            self.wfstate, self.context.portal_type)
        self.owner = getattr(self.context, 'key_email', None) == user_email

        self.available = self.can_review or self.can_edit or self.owner
