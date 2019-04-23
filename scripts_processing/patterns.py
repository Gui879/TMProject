# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 20:12:52 2019

@author: Guilherme
"""
from scripts_processing import DependencyParser

sentence='I am Thommas Lannister, son of Shaun Lannister. Your son is Thommas Lannister. My son is Thommas Lannister. This is my son Thommas Lannister. Jon Lannister, my son, once said.'
df,output = DependencyParser.get_relations(sentence)
subseq = [['NNP',',','NN','IN','NNP'],['PRP$','NN','VBZ','NNP'],['NNP',',','PRP$','NN'],['PRP$', 'NN', 'NNP']]

def pattern_recognizer(sentence,speaker,target,family_words):
    relations = []
    _,phrases = DependencyParser.get_relations(sentence)
    #phrases = re.split('[.?!],)
    direction = None
    for phrase in phrases:
        tokens = phrase['tokens']
        label_seq = [dic['pos'] for dic in tokens]
        mark = None
        for pattern in subseq:
            try:
                mark = dict(find_sequence(pattern.copy(),label_seq))
                if mark:
                    break
            except:
                pass
        if mark:
            if tokens[mark['NN']]['word'] in set(family_words):
                
                if 'IN' in mark.keys():
                    if tokens[mark['IN']]['word'].lower() == 'of':
                        rel = tokens[mark['NN']]['word']
                        try:
                            prev_label= tokens[mark['NNP0']-1]['pos']
                            after_label = tokens[mark['NNP1']+1]['pos']
                            if prev_label == 'NNP' and after_label  == 'NNP':
                                char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                char2 = ' '.join([tokens[mark['NNP1']]['word'],tokens[mark['NNP1']+1]['word']])
                                relations.append([char1, char2,rel,sentence])
                            elif prev_label == 'NNP':
                                char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                char2 = tokens[mark['NNP1']]['word']
                                relations.append([char1, char2, rel,sentence])
                            elif after_label == 'NNP':
                                char1 = tokens[mark['NNP0']]['word']
                                char2 = ' '.join([tokens[mark['NNP1']]['word'],tokens[mark['NNP1']+1]['word']])
                            else:
                                char1 = tokens[mark['NNP0']]['word']
                                char2 = tokens[mark['NNP1']]['word']
                                relations.append([char1,char2,rel,sentence])
                        except:
                            char1 = tokens[mark['NNP0']]['word']
                            char2 = tokens[mark['NNP1']]['word']
                            relations.append([char1,char2,rel,sentence])
                        
                    
                elif 'PRP$' in mark.keys():
                    prp = tokens[mark['PRP$']]['word']
                    rel = tokens[mark['NN']]['word']
                    if prp.lower() == 'my':
                        direction = speaker
                        if 'VBZ' in mark.keys():
                            vrb = tokens[mark['VBZ']]['word']
                            if vrb.lower() == 'is':
                                try:
                                    after_label= tokens[mark['NNP0']+1]['pos']
                                    prev_label = tokens[mark['NNP0']-1]['pos']
                                    if after_label == 'NNP':
                                        char1 = ' '.join([tokens[mark['NNP0']]['word'],tokens[mark['NNP0']+1]['word']])
                                        relations.append([char1, direction,rel,sentence])
                                    elif prev_label == 'NNP':
                                        char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                        relations.append([char1, direction,rel,sentence])
                                    else:
                                        char1 = tokens[mark['NNP0']]['word']
                                        relations.append( [char1,direction,rel,sentence])
                                except:
                                    char1 = tokens[mark['NNP0']]['word']
                                    relations.append( [char1,direction,rel,sentence])
                            
                        else:
                            try:
                                after_label= tokens[mark['NNP0']+1]['pos']
                                prev_label = tokens[mark['NNP0']-1]['pos']
                                if after_label == 'NNP':
                                    char1 = ' '.join([tokens[mark['NNP0']]['word'],tokens[mark['NNP0']+1]['word']])
                                    relations.append([char1, direction,rel,sentence])
                                elif prev_label == 'NNP':
                                    char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                    relations.append([char1, direction,rel,sentence])
                                else:
                                    char1 = tokens[mark['NNP0']]['word']
                                    relations.append( [char1,direction,rel,sentence])
                            except:
                                char1 = tokens[mark['NNP0']]['word']
                                relations.append( [char1,direction,rel,sentence])
                        
                    if prp.lower() == 'your':
                        direction = target
                        if 'VBZ' in mark.keys():
                            vrb = tokens[mark['VBZ']]['word']
                            if vrb.lower() == 'is':
                                try:
                                    after_label= tokens[mark['NNP0']+1]['pos']
                                    prev_label = tokens[mark['NNP0']-1]['pos']
                                    if after_label == 'NNP':
                                        char1 = ' '.join([tokens[mark['NNP0']]['word'],tokens[mark['NNP0']+1]['word']])
                                        relations.append([char1, direction,rel,sentence])
                                    elif prev_label == 'NNP':
                                        char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                        relations.append([char1, direction,rel,sentence])
                                    else:
                                        char1 = tokens[mark['NNP0']]['word']
                                        relations.append( [char1,direction,rel,sentence])
                                except:
                                    char1 = tokens[mark['NNP0']]['word']
                                    relations.append( [char1,direction,rel,sentence])
                        else:
                            try:
                                after_label= tokens[mark['NNP0']+1]['pos']
                                prev_label = tokens[mark['NNP0']-1]['pos']
                                if after_label == 'NNP':
                                    char1 = ' '.join([tokens[mark['NNP0']]['word'],tokens[mark['NNP0']+1]['word']])
                                    relations.append([char1, direction,rel,sentence])
                                elif prev_label == 'NNP':
                                    char1 = ' '.join([tokens[mark['NNP0']-1]['word'],tokens[mark['NNP0']]['word']])
                                    relations.append([char1, direction,rel,sentence])
                                else:
                                    char1 = tokens[mark['NNP0']]['word']
                                    relations.append( [char1,direction,rel,sentence])
                            except:
                                char1 = tokens[mark['NNP0']]['word']
                                relations.append( [char1,direction,rel,sentence])
    return relations

                
        


    
def find_sequence(pat,seq):
    l_seq = len(seq)
    l_subseq = len(pat)
    indexes = []
    for i in range(l_seq):
        if i+l_subseq-1 < l_seq-1:
            if seq[i:i+l_subseq] == pat:
                indexes = [pat,np.arange(i,i+l_subseq)]
                nnps = [i for i in range(l_subseq) if pat[i] == 'NNP' ]
                if len(nnps)> 1:
                    indexes[0][nnps[0]] = 'NNP0'
                    indexes[0][nnps[1]] = 'NNP1'
                else:
                    indexes[0][nnps[0]] = 'NNP0'
                indexes = list(zip(indexes[0],indexes[1]))
                return indexes
    return