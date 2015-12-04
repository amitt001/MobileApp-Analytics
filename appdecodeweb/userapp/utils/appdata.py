"""
A simple utility module to hit api and get data and process it
"""

import requests
from datetime import datetime


class AppProcessor(object):
    """Class to process and clean all he app data that is returned from PlayAPI."""

    def __init__(self):
        self.result = {}

    def get_result(self, url, app_id):
        """Gets """
        resp = requests.get(url)
        self.result = {'_id': app_id} if resp.status_code != 200 else resp.json()
        self.result['id'] = self.result.pop('_id')
        return self.result

    def get_ranks(self, country='in'):
        """Process category and topchart rank and returns data"""
        cat_rank = self.result['category_rank']
        top_rank = self.result['topchart_rank']
        country = self.result['country']
        date = self.result['crawling_date']
        ranks = [[], [], []]
        for idx, c in enumerate(country):
            if c =='in':
                ranks[0].append(cat_rank[idx] if cat_rank[idx] else None)
                ranks[1].append(top_rank[idx] if top_rank[idx] else None)
                ranks[2].append('-'.join(date[idx].split()[1:4]))
        return ranks
