"""
A simple utility module to hit api and get data and process it
"""

import os
import requests
from datetime import datetime

import matplotlib.pyplot as plt
from wordcloud import WordCloud


class AppProcessor(object):
    """Class to process and clean all he app data that is returned from PlayAPI."""

    def __init__(self):
        self.result = {}

    def get_result(self, url, app_id):
        """Gets """
        resp = requests.get(url)

        if resp.status_code == 200:
            self.result = resp.json()
            self.result['error'] = 0
        else:
            #when no data available for an app set error=1 and check it in frontend
            self.result = {'_id': app_id, 'error': 1}

        try:
            self.result['id'] = self.result.pop('_id')
        except KeyError as ke:
            """"
            when _id is not in result and format is like 
                {'com.whatsapp': {key1:value1, ....}}
            """
            self.result['id'] = self.result.keys()[0]
            self.result.update(self.result.pop(self.result['id']))
        return self.result

    def get_ranks(self, country='in'):
        """Process category and topchart rank and returns data"""
        reskey = self.result.keys()
        cat_rank = self.result['category_rank'] if 'category_rank' in reskey else []
        top_rank = self.result['topchart_rank'] if 'category_rank' in reskey else []
        country = self.result['country'] if 'category_rank' in reskey else []
        date = self.result['crawling_date'] if 'category_rank' in reskey else []
        ranks = [[], [], []]
        for idx, c in enumerate(country):
            if c =='in':
                ranks[0].append(cat_rank[idx] if cat_rank[idx] else None)
                ranks[1].append(top_rank[idx] if top_rank[idx] else None)
                ranks[2].append('-'.join(date[idx].split()[1:4]))
        return ranks

    def word_cloud(self, app_id, url, static_dir):
        """Generates a word cloud PNG image and save 
        it in statc project directory"""
        try:
            result = self.get_result(url, app_id)
            #For generating wordcloud and saving an image
            nc, pc = result['negative_cloud'], result['positive_cloud']
            pstr, nstr = '', ''
            for c in pc:
                pstr += (c[0]+' ')*c[1]
            for c in nc:
                nstr += (c[0]+' ')*c[1]
            nw = WordCloud().generate(nstr)
            pw = WordCloud().generate(pstr)
            plt.imshow(nw)
            plt.axis('off')
            plt.savefig(os.path.join(static_dir, 'neg.png'))
            plt.imshow(pw)
            plt.axis('off')
            plt.savefig(os.path.join(static_dir, 'pos.png'))
        except Exception as err:
            print(err)
