# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 20:12:52 2019

@author: Guilherme
"""
from scripts_processing import DependencyParser

sentence='I am Thommas, son of Shaun. Your son is Thommas. My son is Thommas. This is my son Thommas. Jon, my son, once said.'
df,output = DependencyParser.get_relations(sentence)
subseq = [['NNP',',','NN','IN','NNP'],['PRP$','NN','VBZ','NNP'],['NNP',',','PRP$','NN'],['PRP$', 'NN', 'NNP']]

def pattern_recognizer(sentence,speaker,target,family_words):
    relations = []
    _,phrases = DependencyParser.get_relations(sentence)
    direction = None
    for phrase in phrases:
        tokens = phrase['tokens']
        label_seq = [dic['pos'] for dic in tokens]
        mark = None
        for pattern in subseq:
            try:
                mark = dict(find_sequence(pattern,label_seq))
            except:
                pass
        if mark:
            if tokens[mark['NN']]['word'] in set(family_words):
                
                if 'IN' in mark.keys():
                    if tokens[mark['IN']]['word'].lower() == 'of':
                        relations.append([tokens[mark['NNP0']]['word'],tokens[mark['NNP1']]['word'],tokens[mark['NN']]['word'],sentence])
                    
                elif 'PRP$' in mark.keys():
                    prp = tokens[mark['PRP$']]['word']
                    if prp.lower() == 'my':
                        direction = speaker
                        if 'VBZ' in mark.keys():
                            vrb = tokens[mark['VBZ']]['word']
                            if vrb.lower() == 'is':
                                relations.append( [tokens[mark['NNP0']]['word'],direction,tokens[mark['NN']]['word'],sentence])
                            
                        else:
                            
                            relations.append([tokens[mark['NNP0']]['word'], direction, tokens[mark['NN']]['word'], sentence])
                        
                    if prp.lower() == 'your':
                        direction = target
                        if 'VBZ' in mark.keys():
                            vrb = tokens[mark['VBZ']]['word']
                            if vrb.lower() == 'is':
                                relations.append( [tokens[mark['NNP0']]['word'], direction, tokens[mark['NN']]['word'], sentence])
                        else:
                                relations.append( [tokens[mark['NNP0']]['word'] + ' is ' + direction +"'s " + tokens[mark['NN']]['word'],sentence])
    return relations

                
        
def find_sequence(subseq,seq):
    i = 0
    nnps = 0
    indexes = []
    seq_len = len(seq)
    subseq_len = len(subseq)
    for t in range(seq_len):
        if i == subseq_len:
            return indexes
        
        if seq[t] == subseq[i]:
            i=i+1
            if seq[t] == 'NNP':
                
                indexes.append((seq[t]+str(nnps),t))
                nnps = nnps +1

            else:
                indexes.append((seq[t],t))
        else:
            i=0
            indexes = []
            nnps = 0
        if seq_len-t < subseq_len-i:
            return
    if i > 0:
        return indexes
    return
        
    