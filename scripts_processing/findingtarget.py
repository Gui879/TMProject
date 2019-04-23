# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 17:31:19 2019

@author: Guilherme
"""

#### Code to rearrange the phrases (source and target)
def rearrage_phrases(episode_script, characters_pattern, corrections):
        #creating a deep copy from the source scripts
        tagged_episodes = copy.deepcopy(episode_script)
        for episode in tagged_episodes.keys():
                characters=[]
                last_speaker=None
                for sentence in range(len(tagged_episodes[episode])):
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
                                # replacing the previous sentence with the new one
                                tagged_episodes[episode][sentence] = (ner_tagger(new_sentence),type)
                                
        return tagged_episodes