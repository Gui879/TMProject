# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 15:26:43 2019

@author: Guilherme
"""

#import gensim

class word2vec:
    
    
    def __init__(self,scripts,size,window,min_count):
        self.model = gensim.models.Word2Vec(scripts,size=size,window=window,min_count=min_count,workers=10)
        self.model.train(scripts,total_examples=len(scripts),epochs = 10)
        
    def get_matrix_of_vectors(self):
        M = []
        word_vocab =self.model.wv.vocab.keys()
        word2Ind = dict()
        
        for ix,word in enumerate(word_vocab):
            M.append(self.model.wv[word])
            word2Ind[word] = ix
        return M,word2Ind
    
    