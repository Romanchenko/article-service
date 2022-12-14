import faiss
import pandas as pd
import pyarrow.parquet as pq
import torch

from transformers import BertTokenizer, BertModel
from typing import Iterable, Optional, List
from ..storage.articles_storage import get_ids_by_author


class IndexModel:
    def __init__(self, model_path='prajjwal1/bert-tiny', index_path='', data_path=''):
        self.model_path = model_path
        self.model = BertModel.from_pretrained(model_path, output_attentions=True)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.index = faiss.read_index(index_path)
        self.load_data(data_path)

    def load_data(self, path):
        years = range(2015, 2021)
        columns = ['id', 'title', 'author_ids']
        self.df_train = pd.DataFrame(columns=columns)
        for year in years:
            file = f'{path}/data_tiny_{str(year)}.parquet'
            train = pq.read_table(file, columns=columns, use_threads=False).to_pandas()
            self.df_train = self.df_train.append(train, ignore_index=True)
            print(f'get {train.shape} for {year}')
        self.index_map_id = self.df_train['id'].to_dict()
        self.id_map_index = {v: k for k, v in self.index_map_id.items()}

    def encode(self, texts: List[str], do_norm: bool = True) -> torch.Tensor:
        print('Called encode with texts')
        print(f'Texts: {texts}')
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input.to(self.model.device))
            embeddings = model_output.pooler_output
            if do_norm:
                embeddings = torch.nn.functional.normalize(embeddings)
        return embeddings

    def batch_predict(self, titles, k=10):
        # idx = [self.id_map_index[i] for i in titles]
        # titles = self.df_train[self.df_train.index.isin(idx)].title.tolist()
        embeddings = self.encode(titles)
        embedding = embeddings.mean(dim=0).numpy()
        k_search = self.index.search(embedding.reshape(1, -1), k)[1]
        return [self.df_train.iloc[i].title for i in k_search[0]]

    def predict(self, id_author, k=10):
        list_titles = get_ids_by_author(id_author)
        return self.batch_predict(list_titles, k)


index_model = IndexModel(index_path='/models/faiss_index', data_path='/models/data')


def predict(author_id: str) -> List[str]:
    global index_model
    if index_model is None:
        index_model = IndexModel(index_path='/models/faiss_index', data_path='/models/data')

    ids = index_model.predict(author_id)
    return ids

