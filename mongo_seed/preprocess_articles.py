import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import json
from collections import defaultdict
from igraph import *
import igraph as ig
from cairo import *
import math
import os
def dump_jsons():
    from bson import ObjectId
    from bson import json_util
    references_dict = []

    for path in [
        'test1.json'
    ]:
        with open(path, 'rb') as fin:
            cur_num = 0
            max_num = 1000000 - 1
            line = next(fin)

            try:
                while line:
                    cur_num += 1
                    if cur_num == max_num:
                        break

                    element = json.loads(line)
                    line = next(fin)
                    cur = {}

                    cur['_id'] = ObjectId(element.get('_id'))
                    for key in ['abstract', 'doi', 'fos', 'isbn', 'issn', 'issue',
                                'keywords', 'lang', 'n_citation', 'page_end', 'page_start', 'pdf',
                                'references', 'title', 'volume', 'year']:
                        el = element.get(key, None)
                        if el is not None:
                            cur[key] = el

                    cur['url'] = element.get('url', [])

                    authors = element.get('authors')
                    if authors is not None:
                        authors_ids = [x.get('_id', '') for x in authors if x is not None]
                        author_names = [x.get('name', '') for x in authors if x is not None]
                    else:
                        authors_ids = []
                        author_names = []
                    cur['authors'] = authors_ids
                    cur['author_names'] = author_names

                    venue = element.get('venue')
                    if venue is not None:
                        venue_id = element['venue'].get('_id', None)
                        venue_name = element['venue'].get('raw', None)
                    else:
                        venue_id = None
                        venue_name = None
                    if venue_id is not None:
                        cur['venue_id'] = venue_id
                    if venue_name is not None:
                        cur['venue_name'] = venue_name
                    references = element.get('references', [])
                    obj_id_refs = list(map(lambda x: ObjectId(x), references))
                    cur['references'] = obj_id_refs
                    references_dict.append(cur)

            except StopIteration as ex:
                pass

if __name__ == '__main__':
    dump_jsons()