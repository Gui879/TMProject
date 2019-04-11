# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 17:04:11 2019

@author: Guilherme
"""
from scripts_processing import classes,DependencyParser,patterns
import numpy as np
import pandas as pd
import re

joined_family_sentences = np.load('scripts_processing/final_sentences.npy')
family_words = np.load('scripts_processing/family_words.npy')
accuracy = pd.read_excel('scripts_processing/GT.xlsx',header = None)



def find_vocative(sentence):
    sentence_l = sentence.lower()
    if re.search('\w+, \w+, \w+',sentence_l):
        return
    
    for word in family_words:
        vocative = re.search(r"(?<!\w )\b"+word + r"\b(?= ?[\.!,])|(?<=, )\b" + word +r"\b(?=[\.!?,])",sentence_l)
        if vocative:
            return vocative.group(0)



    
def get_relations(vocative_function,sentences=joined_family_sentences):
    relations = []
    found=[]
    for sentence in sentences:
        #Find target of sentence
        speaker = re.search("(?<=[\.?!] )([\w\s]+)(?= said to )",sentence)
        target = re.search("(?<=said to )([\w\s]+)(?=\.)",sentence)
        
        if speaker and target:
            speaker = speaker.group(0)
            target = target.group(0)
            found = found  + patterns.pattern_recognizer(sentence,speaker,target,family_words)
            #rel = pattern_recognizer(sentence,speaker,target)
            #if rel:
                #relations.append(rel)
            #else:
            characters = [classes.Character(speaker),classes.Character(target)]
            #Find Vocative
                    
            rel = vocative_function(sentence)
    
            if rel:
                characters[0].set_relation(characters[1],rel)
                relations.append([characters[1].name , characters[0].name , rel,sentence])
    return relations,found


#df['Acc'] = accuracy
relations,found,df = get_relations(find_vocative)
df = pd.DataFrame(df,columns = ['Relation','Sentence'])
found = pd.DataFrame(found,columns = ['Relation','Sentence'])
found = found.drop_duplicates('Relation', keep='first')
df = df.drop_duplicates('Relation', keep='first')
df = pd.concat(df,found)
df = df.drop_duplicates('Relation', keep='first')

#relations = pd.DataFrame(relations,columns = ['RELATION','SENTENCE'])

relations = pd.DataFrame(relations,columns = ['char1','char2','type'])
relations.shape
relations['type'].unique()

relations = relations.apply(lambda x: x.str.lower(), axis=1)
#parents
relations.loc[(relations['type']=='father') ,'type']='father_of'
relations.loc[(relations['type']=='mother') | (relations['type']=='mom'),'type']='mother_of'

#childrens
relations.loc[(relations['type']=='son') ,'type']='son_of'
relations.loc[(relations['type']=='daughter'),'type']='daughter_of'
relations.loc[(relations['type']=='children') ,'type']='children_of'

#married
relations.loc[(relations['type']=='wife') ,'type']='wife_of'
relations.loc[(relations['type']=='husband'),'type']='husband_of'

#grandparents
relations.loc[(relations['type']=='grandmother') ,'type']='grandmother_of'
relations.loc[(relations['type']=='grandfather') ,'type']='grandfather_of'

#cousins
relations.loc[relations['type']=='cousin','type']='cousin_of'

#uncles
relations.loc[(relations['type']=='aunt') ,'type']='aunt_of'
relations.loc[(relations['type']=='uncle'),'type']='uncle_of'

#relations.loc[relations['type']=='niece', ['char1','char2']] = relations.loc[relations['type']=='niece', ['char2','char1']].values
#relations.loc[relations['type']=='nephew', ['char1','char2']] = relations.loc[relations['type']=='nephew', ['char2','char1']].values
#relations.loc[(relations['type']=='niece') | (relations['type']=='nephew'),'type']='uncleof'
relations.loc[(relations['type']=='brother'),'type']='brother_of'
relations.loc[(relations['type']=='sister') ,'type']='sister_of'
#relations = relations[relations['type'].isin(['parentof','siblings'])]

#relations.drop_duplicates(inplace=True)

target_relations = pd.read_csv('model/relationships.csv', names=['char1','char2','type'], skiprows=1)
pd.merge(relations, target_relations, on=['char1','char2','type'],how = 'inner').shape


target_relations[target_relations['char1'].str.contains('yara')]

target_relations[target_relations['type']=='uncleof']

target_relations['char1'].unique()

relations['accuracy'] = accuracy

relations.loc[relations['accuracy']=='Certo','accuracy'] = True
relations.loc[relations['accuracy']=='Errado','accuracy'] = False

relations[relations['accuracy']].drop_duplicates()


temp = pd.merge(relations[relations['accuracy']].drop_duplicates(), target_relations, on=['char1','char2','type'],how = 'inner').drop_duplicates()


relations[(~relations.isin(temp))]
relations[(relations['accuracy']) & (~relations.isin(pd.merge(relations[relations['accuracy']].drop_duplicates(), target_relations, on=['char1','char2','type'],how = 'inner').drop_duplicates()))]
