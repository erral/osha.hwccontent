from DateTime import DateTime
from Products.CMFPlone.PloneBatch import Batch
from Products.ZCatalog.interfaces import ICatalogBrain
from json import load
from osha.hwccontent.browser.mixin import ListingView
from osha.hwccontent.interfaces import IFullWidth
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from plone.memoize import ram
from urllib import urlopen
from zope.interface import implements
import base64


class NewsItemListing(ListingView):
    implements(IFullWidth)


    def __init__(self, context, request):
        super(NewsItemListing, self).__init__(context, request)
        properties = api.portal.get_tool('portal_properties')
        self.osha_json_url = getattr(
            properties.site_properties,
            'osha_json_url',
            'https://osha.europa.eu/'
        )
        self.remote_news_query_tags = getattr(
            properties.site_properties,
            'remote_news_query_tags',
            'stress,hw2014'
        )

    @ram.cache(ListingView.cache_for_minutes(10))
    def get_remote_news_items(self):
        """ Queries the OSHA corporate site for news items.
            Items returned in JSON format.
        """
        items = []
        lang = api.portal.get_tool("portal_languages").getPreferredLanguage()
        qurl = '%s/%s/jsonfeed?portal_type=News%%20Item&Subject=%s&path=/osha/portal/%s&Language=%s' \
            % (self.osha_json_url, lang, self.remote_news_query_tags, lang, lang)

        result = urlopen(qurl)
        if result.code == 200:
            for item in load(result):
                items.append({
                    'remote_item': True,
                    'Title': item['title'],
                    'Date': item['effectiveDate'],
                    'getURL': item['_url'],
                    'Description': item.get('description', ''),
                    'image_base64': item.get('image'),
                    'image_content_type': item.get('image_type')
                })
        return items

    @ram.cache(ListingView.cache_for_minutes(1))
    def get_local_news_items(self):
        """ Looks in the current folder for Collection objects and then queries
            them for items.
        """
        items = []
        for child in self.context.values():
            if ICollection.providedBy(child):
                items.extend(child.results(
                    batch=False,
                    sort_on='Date',
                    brains=True))
        return items

    def get_all_news_items(self):
        items = self.get_remote_news_items() + \
            list(self.get_local_news_items())
        return sorted(
            items,
            key=lambda item: item.__getitem__('Date'),
            reverse=True
        )

    def get_batched_news_items(self):
        b_size = int(self.request.get('b_size', 20))
        b_start = int(self.request.get('b_start', 0))
        items = self.get_all_news_items()
        for i in range(b_start, b_size):
            if i >= len(items):
                break
            if ICatalogBrain.providedBy(items[i]):
                item = items[i]
                obj = item.getObject()
                blob = getattr(obj.image, '_blob', None)
                items[i] = {
                    'Title': item.Title,
                    'Date': DateTime(item.Date).utcdatetime(),
                    'getURL': item.getPath(),
                    'Description': item.Description,
                    'image': blob and base64.encodestring(blob.open().read()) or None,
                    'obj': obj
                }
            else: 
                items[i]['Date'] = DateTime(items[i]['Date']).utcdatetime()
        return Batch(items, b_size, b_start, orphan=1)