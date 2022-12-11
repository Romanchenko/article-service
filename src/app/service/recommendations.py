import pickle
import re
import spacy
import random
from bertopic import BERTopic
from collections import defaultdict, Counter
from tqdm import tqdm
from nltk.corpus import stopwords


klusters_top = defaultdict(list)
for item, label in tqdm(zip(df.author_ids.values, df.labels.values)):
    for author in list(map(lambda x: x.strip(), item.split(";"))):
        if author != "":
            flag = False
            for lst in klusters_top[label]:
                if lst[0] == author:
                    lst[1] += 1
                    flag = True
                    break
            if flag is False:
                klusters_top[label].append([author, 1])

for key, value in tqdm(klusters_top.items()):
    value.sort(key=lambda x: -x[1])
    klusters_top[key] = np.array(klusters_top[key])

with open("klusters_top.pkl", "wb") as file:
    pickle.dump(klusters_top, file)

class TopicModeling:

    def __init__(self, path_to_model: str):
        self.bert_model = BERTopic.load(path_to_model)
        self.topic_dict = dict(zip(self.bert_model.get_topic_info()['Topic'],
                                   self.bert_model.get_topic_info()['Name']))

    def text_preprocessing(self, text):
        if isinstance(text, str):
            text = [text]
        for idx, txt in enumerate(text):
            regex = re.compile('[A-Za-z]+')
            nlp = spacy.load('en_core_web_sm')
            mystopwords = stopwords.words('english') + ['paper', 'result', 'experiment', 'from', 'subject',
                                                        're', 'edu', 'use', 'data', 'method', 'based',
                                                        'new', 'approach', 'also', 'system', 'model',
                                                        'present', 'research', 'propose', 'base']

            text[idx] = ' '.join(regex.findall(txt))
            doc = nlp(txt)
            text[idx] = ' '.join([token.lemma_ for token in doc])
            text[idx] = ' '.join([token for token in txt.split() if not token in mystopwords])

        return text

    def score_text(self, text):
        text = self.text_preprocessing(text)
        topics, prob = self.bert_model.transform(text)
        for idx, topic in enumerate(topics):
            topics[idx] = self.topic_dict[topic]
        return topics


class Recommendation_system:

    def __init__(self, model, train_dct_of_links, klusters_top):
        self.model = model
        self.train_dct_of_links = train_dct_of_links
        self.klusters_top = klusters_top
        self.top_authors = self.get_top_authors()

    def get_top_authors(self, top=1000):
        authors_by_collaborators = [(author, len(collaborators)) for author, collaborators in
                                    self.train_dct_of_links.items()]
        authors_by_collaborators.sort(key=lambda x: x[1])

        out = [None] * top
        for i in range(top):
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
        if author_id is None:
            if lst_of_articles is None:
                return self.top_authors[-top:]

            out = self.get_recommendations_on_articles(top=top,
                                                       lst_of_articles=lst_of_articles)

            return out

        elif author_id in self.train_dct_of_links:
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

        elif author_id not in self.train_dct_of_links:
            if lst_of_articles is None:
                return self.top_authors[-top:]

            out = self.get_recommendations_on_articles(top=top,
                                                       lst_of_articles=lst_of_articles)

            return out
