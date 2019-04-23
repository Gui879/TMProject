# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 14:50:23 2019

@author: Guilherme
"""
import re
import pandas as pd
import numpy as np
import copy
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags
import Levenshtein as lev

### NER FUNTIONS
def tokenizer(sent):
    sent = nltk.word_tokenize(sent)
    return sent

def removePunct(sent):
    sent = [(token[0],token[1],token[2]) for token in sent if not re.search('[^\w-]',token[0])]
    return sent

def pos_tagger(sent):
    sent = nltk.pos_tag(sent)
    #sent = [(token[0].lower(),token[1]) for token in sent]
    return sent

def ner_tagger(sent):
    sent = tokenizer(sent)
    sent = pos_tagger(sent)
    sent = tree2conlltags(ne_chunk(sent))
    sent = [(token[0],token[1],token[2]) for token in sent]

    #pattern = 'NP: {<DT>?<JJ>*<NN>}'
    #cp = nltk.RegexpParser(pattern)
    #cs = cp.parse(art_processed)
    
    #iob_tagged = tree2conlltags(cs)
    return sent


def get_characters(scripts):
    our_characters = []
    for sentence in scripts:
        match = re.search('(\w{2,}(\s\w{2,})?)(.*)?\:', sentence[0])
        if match:
            our_characters.append(match.group(1))

    our_characters = [character.lower() for character in our_characters]
    characters_frequency = {character:our_characters.count(character) for character in set(our_characters)}
    our_characters = list(set(our_characters))
    our_characters.sort()
    return our_characters, characters_frequency


def rearrage_phrases(sample,episode_script, characters_pattern, corrections):
        #creating a deep copy from the source scripts
        new_sample = []
        tagged_episodes = copy.deepcopy(episode_script)
        episodes = [s[2] for s in sample]
        episodes = list(set(episodes))
        
        for episode in episodes:
            sample_sentences = list(filter(lambda x: x[2] ==episode, sample))
            characters=[]
            last_speaker=None
            for sentence in range(len(tagged_episodes[episode])):
                #If sample_sentences no point in continuing
                if len(sample_sentences) == 0:
                    break
                type = tagged_episodes[episode][sentence][1]
                # if the scene change, the list of characters and the last_speaker are cleaned
                if type=='Scene Change':
                        characters=[]
                        last_speaker=None
                        tagged_episodes[episode][sentence] = (ner_tagger(tagged_episodes[episode][sentence][0]),type)
                # if it is a description, we will try to find the characters involved in the followign scence
                elif type=='Description':
                        [characters.append(character.title()) for character in re.findall(characters_pattern, tagged_episodes[episode][sentence][0].lower())]
                        tagged_episodes[episode][sentence] = (ner_tagger(tagged_episodes[episode][sentence][0]),type)
                # if it is a phrase, we try to extract the source and the target
                elif type=='Phrase':
                        #Try to find target by finding a vocative phrase
                        
                        # removing the source (For instance, in 'JON: Hi, how are you?', the JON is our source)
                        source = re.search('(\w{2,}(\s\w{2,})?)(.*)?\:', tagged_episodes[episode][sentence][0]).group(1)
                        # trying to find the target of the current phrase
                        # 1st option is to look to who is the following speaker
                        if sentence+1<len(tagged_episodes[episode]) and tagged_episodes[episode][sentence+1][1]=='Phrase':
                                target = re.search('(\w{2,}(\s\w{2,})?)(.*)?\:', tagged_episodes[episode][sentence+1][0]).group(1)
                        # 2nd option is to look back to the previous speaker
                        elif last_speaker is not None:
                                target = last_speaker
                        # 3rd option is to find if a new character will enter in the current scene
                        else:
                                # if we have more sentences, we try to find the new characters
                                if sentence+1<len(tagged_episodes[episode]):
                                        [characters.append(character.lower()) for character in re.findall(characters_pattern, tagged_episodes[episode][sentence+1][0].lower())]
                                        characters = list(set(characters))
                                        if len(characters)!=0:
                                            i = len(characters)-1
                                            target=characters[i]
                                            while(source==target):
                                                    i=i-1
                                                    try:
                                                            target = characters[i]
                                                    except :
                                                            target = 'Everybody'
                                        else:
                                            target = 'Anybody'
                                # otherwise, we assume the character is speaking to no one
                                else:
                                        target='Anybody'
                        
                        last_speaker=source
                        characters.append(source)
                        # correcting the character's names if needed
                        for i in range(2):
                                try:
                                        source = corrections[source.lower().strip()]
                                except :
                                        pass
                                try:
                                        target = corrections[target.lower().strip()]
                                except :
                                        pass

                        # rearraging the sentence
                        new_sentence = re.sub('((\w{2,}(\s\w{2,})?)(.*)?\:\s?)','', tagged_episodes[episode][sentence][0])
                        new_sentence = new_sentence +' '+source.lower().title()+' said to '+target.lower().title()+'.'
                        sample_phrases = [x[0] for x in sample_sentences]
                        try:
                            phrase_ix = sample_phrases.index(tagged_episodes[episode][sentence][0])
                            p = sample_sentences[phrase_ix]
                            del sample_sentences[phrase_ix]
                            new_sample.append((new_sentence,p[1],p[2],phrase_ix))
                        except ValueError:
                            pass
                        # replacing the previous sentence with the new one
                        #tagged_episodes[episode][sentence] = (ner_tagger(new_sentence),type)
        return new_sample

def characters_name_correction(episode_script):
    
    #Get characters' name from scripts
    our_characters, characters_frequency = get_characters(episode_script)

    #extract all characters' names from our target data
    target_relations = pd.read_csv('model/relationships.csv', names=['char1','char2','type'], skiprows=1)
    characters_names = list(set(np.concatenate([target_relations['char2'].unique(), target_relations['char1'].unique()])))
    #getting the nicknames of some characters
    nicknames = pd.read_csv('scripts_processing/nicknames.csv', names=['character','nickname'], skiprows=1)
    [characters_names.append(nickname) for nickname in nicknames['nickname'].values]

    #calculating the similarity between the scripts chracters' names and the desired names
    similarity = pd.DataFrame(0, columns=our_characters, index = characters_names)
    for word1 in our_characters:
        for word2 in characters_names:
                # if two characters have the same last name, we will compare their first name
                if len(word1.split(' '))>1 and len(word2.split(' '))>1 and word1.split(' ')[-1]==word2.split(' ')[-1]:
                    similarity.loc[word2,word1] = lev.ratio(word2.split(' ')[0],word1.split(' ')[0])
                # otherwise, we compare the full name, this is try to find the most similar word to the initial name, and return the given similarity score
                else:
                    similarity.loc[word2,word1] = np.max([lev.ratio(word1,substring) for substring in word2.split(' ')])

    #getting the names with a similarity score greater or equal to 0.7
    r,c = np.where(((similarity>=0.7)))
    temp = np.column_stack((similarity.index[r],similarity.columns[c],similarity.values[r,c]))
    similarity_t = pd.DataFrame(temp,columns=['character_1','character_2','final_score'])

    #building the corrections dictionary
    corrections = {}
    for name in similarity_t['character_2'].unique():
        corrections[name] = similarity_t[similarity_t['character_2']==name].sort_values(by=['final_score']).tail(1)['character_1'].values[0]
    
    #building the nicknames dictionary
    nicksnames_dict = {}
    for nickname in nicknames['nickname']:
        nicksnames_dict[nickname] = nicknames.loc[nicknames['nickname']==nickname,'character'].values[0] 

    #replace the nicknames by the real character name
    for key in corrections.keys():
        try:
            corrections[key] = nicksnames_dict[corrections[key]]
        except:
            pass
    
    our_characters = list(set([corrections[character] if character in corrections else character for character in our_characters]))

    return our_characters ,corrections