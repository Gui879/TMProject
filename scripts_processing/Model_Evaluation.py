# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 14:39:54 2019

@author: Guilherme
"""

import sys
sys.path.append('/scripts_processing')
from scripts_processing import evaluation_utils,word2vec,classes
import numpy as np
import pandas as pd
import re
from sklearn.metrics import recall_score


def flat_sentences_dict(dictionary):
    sentences = []
    for k,v in dictionary.items():
        for phrase in v:
            if phrase[1] == 'Phrase':
                sentences.append((phrase[0],phrase[1],k))
    return sentences
                
def has_family_word(sentences):
    s = []
    for sentence in sentences:
        for family_word in family_words:
            if family_word in sentence[0]:
                s.append(sentence)
    return s

def find_vocative(sentence):
    sentence_l = sentence.lower()
    if re.search('\w+, \w+, \w+',sentence_l):
        return
    
    for word in family_words:
        vocative = re.search(r"(?<!\w )\b"+word + r"\b(?= ?[\.!,])|(?<=, )\b" + word +r"\b(?=[\.!?,])",sentence_l)
        if vocative:
            return vocative.group(0)

def get_relations(vocative_function,sentences):
    rels = []
    for sentence in sentences:
        #Find target of sentence
        speaker = re.search("(?<=[\.?!] )([\w\s]+)(?= said to )",sentence)
        target = re.search("(?<=said to )([\w\s]+)(?=\.)",sentence)
        
        if speaker and target:
            speaker = speaker.group(0)
            target = target.group(0)
            #rel = pattern_recognizer(sentence,speaker,target)
            #if rel:
                #relations.append(rel)
            #else:
            characters = [classes.Character(speaker),classes.Character(target)]
            #Find Vocative
                    
            rel = vocative_function(sentence)
    
            if rel:
                characters[0].set_relation(characters[1],rel)
                rels.append([characters[1].name , characters[0].name , rel,sentence])

    return rels

episode_script = np.load('scripts_processing/processed_scripts.npy').item()
family_words = np.load('scripts_processing/family_words.npy')
#Get Samples
random_episodes = np.random.choice(list(episode_script.keys()), 200)
samples = []
i = 0
while i < len(random_episodes):
    epi = random_episodes[i]
    epi = episode_script[epi]
    sentence = np.random.choice(range(len(epi)),1)
    sentence = epi[sentence[0]]
    if sentence[1] == 'Phrase':
        sentence = (sentence[0],sentence[1],random_episodes[i])
        if sentence not in samples:
            samples.append(sentence)
            i += 1
        else:
            continue
        
sample_phrases = [x[0] for x in samples]

#Get characters and corrections from sample
our_characters, corrections = evaluation_utils.characters_name_correction(samples)
initial_characters, characters_frequency = evaluation_utils.get_characters(samples)
characters_pattern = ''
for character_index in range(len(initial_characters)):
        if character_index == len(initial_characters)-1:
            characters_pattern=characters_pattern+'\\b'+initial_characters[character_index]+'\\b'
        else:
            characters_pattern=characters_pattern+'\\b'+initial_characters[character_index]+'\\b|'

samplev2 = evaluation_utils.rearrage_phrases(samples,episode_script,characters_pattern,corrections)

sample_phrasesv2 = [x[0] for x in samplev2]
relations = get_relations(find_vocative,sample_phrasesv2)

Results = pd.DataFrame(samples, columns  =['Sentence','Phrase','Episode'])
Results['Target'] =['None'] * len(samples)
Results['Speaker'] = ['None']* len(samples)
Results['Vocative Relation'] = ['None'] * len(samples)
Results['Other Relation'] = ['None'] * len(samples)
Results['In-sentence Characters'] = ['None']* len(samples)

Results.iloc[:50,:].to_csv('joinas_part.csv')
Results.iloc[50:100,:].to_csv('liah_part.csv')
Results.iloc[100:150,:].to_csv('pipa_part.csv')
Results.iloc[150:200,:].to_csv('gui_part.csv')

g.to_csv('gui_part_done.csv')
g = Results.iloc[150:200,:]


g = pd.read_csv("gui_part_done.csv")
g.set_index('Unnamed: 0',drop = True,inplace=True)
j = pd.read_csv('joinas_part_done.csv')
j.set_index('Unnamed: 0',drop = True,inplace=True)
p = pd.read_csv('pipa_got.csv')
p.drop('Unnamed: 0',inplace=True,axis = 1)
p.set_index('Unnamed: 0.1', inplace=True, drop = True)
l = pd.read_csv('liah_part_done.csv')
l.set_index('id',drop = True,inplace=True)

Results_labeled = pd.concat([j,l,p,g])
our_characters



def extract_characters(results):
    characters = []
    for line in range(100,len(results)):
        characters.append(results['Speaker'][line])
        characters.append(results["Target"][line])
        characters.append(results['In-sentence Characters'][line])
    
    flat_list = [word.strip() for line in characters for word in line.split(",")]
    #Drop virgulas e Drop None
    flat_list = [re.sub(",","",x) for x in flat_list if x!='None']
    #Ficar com Unique
    flat_list = list(set(flat_list))
    return(flat_list)
        
Results_Characters = extract_characters(Results_labeled)


#Order by index
samplev2.sort(key = lambda x: x[3])
Results_labeled.sort_index(axis = 0, inplace=True)

speaker_results = []
target_results = []
for sentence in samplev2:
    #Remove ' from sentence
    temp = list(sentence)
    temp[0] = re.sub("'","",temp[0])
    sentence = tuple(temp)
    #Find speakers and targets
    speaker_results.append(re.search("(?<=[\.?!\)\-\"] )([\w\s]+)(?= said to )",sentence[0]).group(0))
    target_results.append(re.search("(?<=said to )([\w\s]+)(?=\.)",sentence[0]).group(0))

speaker = pd.DataFrame(columns=["Real","Guessed"])
speaker["Real"]= Results_labeled["Speaker"]
speaker["Guessed"] = speaker_results    
speaker_recall = recall_score(speaker["Real"], speaker["Guessed"], average=None)  
   
target = pd.DataFrame(columns=["Real","Guessed"])    
target["Real"] = Results_labeled["Target"]
target["Guessed"] = target_results
target_recall = recall_score(target["Real"], target["Guessed"], average=None) 
    