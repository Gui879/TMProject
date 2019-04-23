# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 10:50:19 2019

@author: Guilherme
"""
#java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
import pandas as pd
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')
df = []

def get_relations(sentences):
    output = nlp.annotate(sentences, properties={
    'annotators': 'tokenize, ssplit, pos, depparse, parse, openie',
    'outputFormat': 'json'
    })
    df = []
    for sentence in output['sentences']:
        for relation in sentence['openie']: 
            df.append([sentences,relation['subject'], relation['relation'], relation['object']])
    return pd.DataFrame(df),output['sentences']

test = "Who is the sister of Jon Snow's Grandfather?"