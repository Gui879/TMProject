import sys
sys.path.append('/scripts_processing')
from scripts_processing import utils,word2vec,DependencyParser,patterns
import utils,classes,DependencyParser,patterns
import numpy as np
import pandas as pd
import re

joined_family_sentences = np.load('scripts_processing/final_sentences.npy')
family_words = np.load('scripts_processing/family_words.npy')
accuracy = pd.read_excel('scripts_processing/GT.xlsx',header = None)

sample = np.random.choice(joined_family_sentences,300)



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
    return relations


#df['Acc'] = accuracy
relations,found = get_relations(find_vocative)
relations = pd.DataFrame(relations,columns = ['Char1','Char2','Rel','Sentence'])
found = pd.DataFrame(found,columns = ['Char1','Char2','Rel','Sentence'])
data = pd.concat([relations,found])

found = []
for i in range(len(joined_family_sentences)-2000):
    sentence = joined_family_sentences[i]
    speaker = re.search("(?<=[\.?!] )([\w\s]+)(?= said to )",sentence)
    target = re.search("(?<=said to )([\w\s]+)(?=\.)",sentence)
    found = found + patterns.pattern_recognizer(sentence,speaker,target,family_words)
