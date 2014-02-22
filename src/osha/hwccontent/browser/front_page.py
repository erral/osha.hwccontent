# _+- coding: utf-8 -*-

from osha.hwccontent.browser.event import EventListing
from osha.hwccontent.browser.newsitem import NewsItemListing
from osha.hwccontent.browser.utils import get_partners, css_by_orientation

import random


class FrontPageView(NewsItemListing, EventListing):

    def news(self):
        num_results = 2
        results = self.get_all_news_items()[:num_results]

        return results

    def events(self):
        num_results = 2
        results = self.get_all_events(batch=False)[:num_results]
        return results

    def partners(self):
        return get_partners()

    def css_by_orientation(self, partner):
        """ This is a helper to determine logo orientation for a partner.
        """
        return css_by_orientation(partner)

    def get_partner_start(self):
        return random.randint(1, 6)
