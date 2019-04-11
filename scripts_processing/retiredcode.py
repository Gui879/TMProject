# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 12:12:24 2019

@author: Guilherme
"""

def find_vocative(sentence):
    sentence_l = sentence.lower()
    if re.search('\w+, \w+, \w+',sentence_l):
        return
    
    for word in family_words:
        vocative = re.search(r"(?<!\w )\b"+word + r"\b(?= ?[\.!?,])|(?<=, )\b" + word +r"\b",sentence_l)
        if vocative:
            return vocative.group(0)
        
def find_vocative3(sentence):
    sentence_l = sentence.lower()
    if re.search('\w+, \w+, \w+,',sentence_l):
        return
    
    vocative = re.findall(r'^\w+\s*[.,]',sentence_l)
    
    if vocative:
        if vocative[0].strip() in family_words:
            return vocative[0].strip()
    else:
        vocative=re.findall(r'[^\w\s\"]\s*(\w+)[^\w\s]',sentence_l)
        
        if len(vocative)==1:
            if vocative[0].strip() in family_words:
                return vocative[0].strip()
        elif len(vocative)>1:
            for word in vocative:
                if word.strip() in family_words:
                    return word.strip()
        else:
            return
        
def pattern_recognizer(sentence,source,target):
    dataframe,output = DependencyParser.get_relations(sentence)
    found_relation = False
    for phrase in output:
        tokens = np.array([(token['word'],token['pos']) for token in phrase['tokens']])
        for rel in phrase['openie']:
            subjectspan = np.array(rel['subjectSpan'])
            subjects = tokens[np.arange(subjectspan[0],subjectspan[1])]
            relationspan = np.array(rel['relationSpan'])
            relation = tokens[np.arange(relationspan[0],relationspan[1])]
            objectspan = np.array(rel['objectSpan'])
            object_ = tokens[np.arange(objectspan[0],objectspan[1])]
            
            #Subjects, relation and object_ are arrays with pos tagged tokens inside.
            #Column 0 is words, Column 1 is labels
            #Check Subject
            if len(subjects[:,]) > 1:
                if subjects[0,1] == 'PRP$' and subjects[1,1] == 'NN':
                    #Check PRP
                    if subjects[0][0].lower() == 'my':
                        directed = classes.Character(source)
                    elif subjects[0][0].lower() == 'your':
                        directed = classes.Character(target)
                    else:
                        #Explore alternatives
                        #I am assuming break exits
                        break
                    if subjects[1][0] in family_words:
                        type_ = subjects[1][0]
                    else:
                        break
                    #Check if verb is be(For now just checks if word is is but should probably look for the verb 'be'):
                    if relation[0][0].lower() == 'is':
                        if len(np.unique(object_[:,1])) == 1:
                            if np.unique(object_[:,1])== ['NNP']:
                                found_relation = True
                                directed.set_relation(classes.Character(' '.join(object_[:,0])), type_)
                                return (directed.relations[0].print_(), sentence)
        
            if subjects[-1,1] == 'NNP':
                if len(relation[:,0]) > 1:
                    if relation[0,0].lower() in family_words and relation[1,0].lower() == 'of':
                        if len(np.unique(object_[:,1])) == 1:
                            if np.unique(object_[:,1]) == ['NNP']:
                                found_relation = True
                                directed = classes.Character(' '.join(subjects[:,0]))
                                directed.set_relation(classes.Character(' '.join(object_[:,0])), relation[0,0].lower())
                                return (directed.relations[0].print_(), sentence)