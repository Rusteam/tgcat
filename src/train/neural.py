"""
Load fasttext weights and build a nueral net
"""

import io
from typing import List, Dict
import random

import torch
from torch import nn
from tqdm.autonotebook import tqdm



def load_vectors(fname,):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, fin.readline().split())
    data = {}
    i = 0
    for line in tqdm(fin, desc='lines'):
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
    fin.close()
    return data, d


class EmbeddingNet(nn.Module):
    """
    Embedding network to convert tokenized text to word vectors
    """
    def __init__(self, vectors: Dict[str, List[float]], dim: int):
        super().__init__()
        self.vocab = {w:i for i,w in enumerate(list(vectors.keys()))}
        self.dim = dim
        self.id2word = {i:w for i,w in self.vocab.items()}
        self.embeddings = torch.zeros(len(self.vocab), dim, requires_grad=False)
        for w,i in self.vocab.items():
            self.embeddings[i] = torch.tensor(vectors[w])
            
            
    
    def get_doc_vectors(self, doc: List[str]) -> List[torch.Tensor]:
        """ convert a list of tokens to a list of word vectors, if not present skip """
        res = [self.embeddings[self.vocab[token]] for token in doc if token in self.vocab.keys()]
        if len(res) == 0:
            res = [torch.zeros(self.dim)]
        return res
            
    
    def forward(self, documents: List[List[str]]) -> List[List[torch.Tensor]]:
        """ get word vectors for a batch of documents """
        res = [self.get_doc_vectors(doc) for doc in documents]
        return res
    
    
    def get_extremes(self, doc_vecs: List[torch.Tensor]) -> torch.Tensor:
        """ calculate mean,max,min and sum along each dimension and concat """
        if len(doc_vecs) == 0:
            return torch.zeros(self.dim * 4)
        stacked = torch.stack(doc_vecs, dim=0)
        t_max,_ = stacked.max(dim=0)
        t_min,_ = stacked.min(dim=0)
        t_mean = stacked.mean(0)
        t_sum = stacked.sum(0)
        concat = torch.cat([t_max, t_min, t_mean, t_sum],)
        return concat
    
    
    def get_batch_extremes(self, batch:  List[List[torch.Tensor]],) -> torch.Tensor:
        """ get extremes for each document and return as one batch tensor """
        batch_extremes = [self.get_extremes(doc) for doc in batch]
        batch_extremes = torch.stack(batch_extremes)
        return batch_extremes
        

def test_embeddings():
    dim_size = 10
    vocab = list('asdfqwerty')
    vecs = {
        w:[random.random() for i in range(dim_size)]
        for w in vocab
    }
    # net
    emb_net = EmbeddingNet(vecs, dim_size)
    assert emb_net.embeddings.size() == (len(vocab), dim_size)
    # doc vectors
    doc = list('qwzxdf')
    doc_vecs = emb_net.get_doc_vectors(doc)
    assert len(doc_vecs) == 4
    assert doc_vecs[1].size() == (dim_size,)
    # batch vectors
    docs = [list('asd'), list('asdfg'), list('qwerpoi'), list('zcvv')]
    batch_vecs = emb_net(docs)
    assert len(batch_vecs) == len(docs)
    assert len(batch_vecs[0]) == 3
    assert len(batch_vecs[3]) == 1
    assert batch_vecs[1][1].size() == (dim_size,)
    # extremes
    extremes = emb_net.get_extremes(batch_vecs[2])
    assert extremes.size() == (dim_size * 4, )
    assert all(extremes[:dim_size] > extremes[dim_size:dim_size*2])
    assert all(extremes[dim_size*3:dim_size*4] > extremes[dim_size*2:dim_size*3])
    batch_extremes = emb_net.get_batch_extremes(batch_vecs)
    assert batch_extremes.size() == (len(docs), dim_size * 4)
    return emb_net


emb_net = test_embeddings()
