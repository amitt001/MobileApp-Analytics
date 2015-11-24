"""
Search the apps by name and ID. App data is stored in mongo. 
For search elastic search is used
"""
import elasticsearch


DB = 'playdb'

class Search(object):
    """
    Search apps by name or ID of apps
    """
    def __init__(self):
        # use default settings
        self.es = elasticsearch.Elasticsearch()

    def search(self, q):
        """Search apps by name from es index data"""
        try:
            result = self.es.search(index=DB, q=q)
        except elasticsearch.ConnectionError as e:
            print(e)
            return ['ElasticSearch connectionError: Failed to establish a new connection: Connection refused']
        return [r['_id'] for r in result['hits']['hits']]
