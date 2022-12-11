import logging.config
import pickle
from collections import defaultdict, Counter
from .model_inf import TopicModeling
from ..storage.articles_storage import get_all_cursor, get_all_cursor_authors
from .general_logging import get_logging_conf

logging.config.dictConfig(get_logging_conf('recs.log'))
log = logging.getLogger(__name__)

COLLABS_FILE = "/models/collabs.pkl"
CLUSTER_TOP = "/models/klusters_top.pkl"

rs = None


def count_clusters(logger):
    klusters_top = defaultdict(dict)
    collabs = defaultdict(set)

    for document in get_all_cursor_authors():
        doc_id = document["_id"]
        logger.info(f"Lookup document {doc_id}")
        authors = document['authors']
        label = document['tag']
        for author in authors:
            if author != "":
                if author in klusters_top[label]:
                    klusters_top[label][str(author)] += 1
                else:
                    klusters_top[label][str(author)] = 1
        for author1 in authors:
            for author2 in authors:
                if author1 != author2:
                    logger.info(f"Added link {author1} -> {author2}")
                    collabs[str(author1)].add(str(author2))

    logger.info(f"Finished scanning documents")
    klusters_top_sorted = {}
    for label_key, dict_value in klusters_top.items():
        sorted_results = sorted(list(dict_value.items()), key=lambda x: -x[1])
        klusters_top_sorted[label_key] = sorted_results

    collabs_list = {}
    for author, coauthors in collabs.items():
        collabs_list[author] = list(coauthors)

    logger.info(f"Start dumping dict with {len(collabs_list)} authors")
    with open(COLLABS_FILE, "wb") as file:
        pickle.dump(collabs_list, file)
    logger.info(f"Dumped dict with {len(collabs_list)} authors")

    logger.info(f"Start dumping dict with {len(klusters_top_sorted)} labels")
    with open(CLUSTER_TOP, "wb") as file:
        pickle.dump(klusters_top_sorted, file)
    logger.info(f"Dumped dict with {len(klusters_top_sorted)} labels")


class RecommendationSystem:

    def __init__(self, model_path, train_dct_of_links, klusters_top):
        self.model = TopicModeling(model_path)
        self.train_dct_of_links = train_dct_of_links
        self.klusters_top = klusters_top
        self.top_authors = self.get_top_authors()

    def try_refresh(self):
        if len(self.klusters_top) == 0 or len(self.train_dct_of_links) == 0:
            with open(CLUSTER_TOP, 'rb') as file:
                self.klusters_top = pickle.load(file)
            with open(COLLABS_FILE, 'rb') as file:
                self.train_dct_of_links = pickle.load(file)
            self.top_authors = self.get_top_authors()

    def get_top_authors(self, top=1000):
        authors_by_collaborators = [(author, len(collaborators)) for author, collaborators in
                                    self.train_dct_of_links.items()]
        authors_by_collaborators.sort(key=lambda x: -x[1])  # fixed sort order

        log.info(f"Get top authors length: {len(authors_by_collaborators)}")
        out = [None] * top
        for i in range(min(top, len(authors_by_collaborators))):
            out[i] = authors_by_collaborators[i][0]

        return out

    @staticmethod
    def delete_elements_from_set(st, count):
        for _ in range(count):
            st.pop()

    def add_recommendations_from_top(self, out, top):
        indx = 0
        while len(out) < top:
            out.add(self.top_authors[indx])
            indx += 1

    def get_recommendations_on_articles(self, top, lst_of_articles):
        out = set()
        labels = list(filter(lambda x: x in self.klusters_top,
                             map(lambda x: int(x.split("_")[0]), self.model.score_text(lst_of_articles))))

        if len(labels) != 0:
            klusters_counter = Counter(labels).most_common()
            klusters_count_for_recommendation = min(len(klusters_counter), 3)
            articles_per_cluster = 1 if (top // klusters_count_for_recommendation) == 0 else (
                    top // klusters_count_for_recommendation)

            for i in range(klusters_count_for_recommendation):
                curr_kluster = klusters_counter[i][0]
                out.update(self.klusters_top[curr_kluster][:articles_per_cluster, 0])
                if len(out) >= top:
                    self.delete_elements_from_set(st=out,
                                                  count=len(out) - top)
                    return out

            for i in range(klusters_count_for_recommendation):
                curr_kluster = klusters_counter[i][0]
                out.update(self.klusters_top[curr_kluster][articles_per_cluster:(articles_per_cluster * 2), 0])
                if len(out) >= top:
                    self.delete_elements_from_set(st=out,
                                                  count=len(out) - top)
                    return out

            for i in range(klusters_count_for_recommendation, len(klusters_counter)):
                curr_kluster = klusters_counter[i][0]
                out.update(self.klusters_top[curr_kluster][articles_per_cluster:(articles_per_cluster * 2), 0])
                if len(out) >= top:
                    self.delete_elements_from_set(st=out,
                                                  count=len(out) - top)
                    return out

        self.add_recommendations_from_top(out, top)
        return out

    def get_recommendation(self, top=10, author_id=None, lst_of_articles=None):
        self.try_refresh()
        if (author_id is None) or (author_id not in self.train_dct_of_links):
            if lst_of_articles is None:
                return self.top_authors[-top:]

            out = self.get_recommendations_on_articles(top=top,
                                                       lst_of_articles=lst_of_articles)

            return out

        else:
            all_recommendation = set()
            first_layer = self.train_dct_of_links[author_id]

            for first_layer_item in first_layer:
                for second_layer_item in self.train_dct_of_links[first_layer_item]:
                    all_recommendation.add(second_layer_item)
                    # если скорость работы будет позволять, можно добавлять всех, а потом, храня словарь
                    # с количеством соавторов для каждого автора, добавлять их по популярности
                    if len(all_recommendation) == top:
                        return all_recommendation

            self.add_recommendations_from_top(all_recommendation, top)
            return all_recommendation


def recommend(author_id, top=10):
    if top is None:
        top = 10
    global rs
    if rs is None:
        with open(CLUSTER_TOP, "rb") as clusters_top_file, open(COLLABS_FILE, "rb") as collabs_file:
            clusters = pickle.load(clusters_top_file)
            collabs = pickle.load(collabs_file)
            rs = RecommendationSystem('/models/bert_model_100k', collabs, clusters)
    recs = rs.get_recommendation(author_id=author_id, top=top)
