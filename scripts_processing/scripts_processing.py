import sys
sys.path.append('/scripts_processing')
from scripts_processing import utils,word2vec,DependencyParser
from pprint import pprint
import pandas as pd
import numpy as np
#import gensim
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import copy

'''
#loading the data
episode_script = np.load('scripts_processing/scripts.npy').item()
family_words= np.load('scripts_processing/family_words.npy')

#Processing data
episode_script = utils.pre_process(episode_script)

#Classifying sentences
# (Phrase, Description, Scene Change)
# EXT,INT,CUT TO
episode_script = utils.sentence_classifier(episode_script)

#removing unwanted keys from episodes dictionary
for key in list(episode_script.keys()):
         if re.match('.*None$', key):
                 del episode_script[key]

#Correcting and getting the characters name
our_characters, corrections = utils.characters_name_correction(episode_script)


np.save('scripts_processing/corrections.npy', corrections)
np.save('scripts_processing/processed_scripts.npy',episode_script)
np.save('scripts_processing/our_characters.npy',our_characters)
'''

corrections = np.load('scripts_processing/corrections.npy').item()
episode_script = np.load('scripts_processing/processed_scripts.npy').item()
family_words = np.load('scripts_processing/family_words.npy')
our_characters = np.load('scripts_processing/our_characters.npy')

#building a character pattern
initial_characters, characters_frequency = utils.get_characters(episode_script)
characters_pattern = ''
for character_index in range(len(initial_characters)):
        if character_index == len(initial_characters)-1:
                characters_pattern=characters_pattern+'\\b'+initial_characters[character_index]+'\\b'
        else:
                characters_pattern=characters_pattern+'\\b'+initial_characters[character_index]+'\\b|'

#rearrage the phrases (source and target)
improved_sentences = utils.rearrage_phrases(episode_script,characters_pattern, corrections)

np.save('scripts_processing/tagged_words_v0.npy',improved_sentences)
improved_sentences= np.load('scripts_processing/tagged_words_v0.npy').item()

epi = []
for split in improved_sentences['s1ep1']:
    epi.append(split[0])
    
joined_improved_sentences = [join_tokens(sentence) for sentence in epi]
#Filter phrases of interest
family_sentences = []
for episode in range(len(improved_sentences.values())):
    for sentence in episode:
        has_family = False
        if sentence[1] == 'Phrase':
            for tuple_ in sentence[0]:
                word = tuple_[0]
                if word.lower() in family_words:
                    has_family = True
                    break
        if has_family:
            epi = improved_sentences.keys()[episode]
            family_sentences.append((sentence[0],epi))
np.save('scripts_processing/family_sentences.npy',family_sentences)
family_sentences = np.load('scripts_processing/family_sentences.npy')

################################Liah's Code Here ###########################################################
tagged_episodes_fixed=copy.deepcopy(family_sentences)

#Correct character names
character_tags=["JJ","NN","NNS","NNP","NNPS"]

def update_char_name(episode,sentence,tuple_):
    if (any(tag in episode[sentence][tuple_] for tag in character_tags)) and episode[sentence][tuple_][0] in corrections.keys() :
        lst=list(episode[sentence][tuple_])
        lst[0]=corrections[lst[0]]
        episode[sentence][tuple_]=tuple(lst)
    return episode[sentence][tuple_]


for sentence in range(len(tagged_episodes_fixed)):
        for tuple_ in range(len(tagged_episodes_fixed[sentence])):
            tagged_episodes_fixed[sentence][tuple_]=update_char_name(tagged_episodes_fixed,sentence,tuple_)
            tagged_episodes_fixed[sentence][tuple_]=update_char_name(tagged_episodes_fixed,sentence,tuple_)
            
#tagged_episodes_fixed= [utils.find_composed_characters(sentence,our_characters) for sentence in tagged_episodes_fixed]

np.save('scripts_processing/tagged_words_v2.npy',tagged_episodes_fixed)
tagged_episodes= np.load('scripts_processing/tagged_words_v2.npy')
############################################################################################################

#Creating dataframe with all tagged words
tagged_words = pd.DataFrame([token for key in tagged_episodes.keys() for i in range(len(tagged_episodes[key])) for token in tagged_episodes[key][i][0]], columns = ['Word', 'Pos Label', 'Ner Label'])

#Creating Vocabulary
words,counts = np.unique(tagged_words['Word'],return_counts = True)
words_vocab = pd.DataFrame(list(zip(words,counts)),columns = ['Word','Count'])

family_words

#Join tokens to form sentence
def join_tokens(sentence):
    joined = sentence[0][0]
    iter_ = iter(range(1,len(sentence)))
    for tuple_ in iter_:
        if re.match("['’](?!\w)",sentence[tuple_][0]):
            joined = joined + sentence[tuple_][0] + sentence[tuple_ + 1][0]
            next(iter_,None)
        elif re.match("['’]",sentence[tuple_][0]) or re.search("['’]", sentence[tuple_][0]):
            joined = joined + sentence[tuple_][0]
        elif re.match('[\.,!?]',sentence[tuple_][0]):
            joined= joined + sentence[tuple_][0]
        else:
            joined = joined+ ' ' + sentence[tuple_][0]
    return joined

joined_family_sentences = [join_tokens(sentence) for sentence in family_sentences]

string = 'my father is'
utils.tokenizer(string)




np.save('scripts_processing/final_sentences.npy',joined_family_sentences)
joined_family_sentences = np.load('scripts_processing/final_sentences.npy')


#########################Dependency Parser##########################################################
grammar_relations = pd.DataFrame()
output_raw = []

def get_grammar_relations(grammar_relations,sentence):
    relations, output = DependencyParser.get_relations(sentence)
    output_raw.append(output)
    dt = pd.concat([grammar_relations,relations])
    return dt

for sentence in dataset:
    grammar_relations = get_grammar_relations(grammar_relations, sentence)
        
grammar_relations.columns = ['Sentence','Subject','Relation','Object']
grammar_relations.reset_index(drop = True, inplace = True)
grammar_relations.to_csv('scripts_processing/grammar_relations.csv')


#tree = parse.tree()
#utils.get_root(tree)
#utils.get_first_children(tree)

#########################Word2vec####################################################
wv_scripts = [gensim.utils.simple_preprocess(sentence[0]) for episode in episode_script.values() for sentence in episode]
temp = [character.split(' ') for character in our_characters]
characters = []
for character in temp:
    characters = characters + character

word2vec_model = word2vec.word2vec(wv_scripts, size = 150, window = 1, min_count = 2)

M,word2Ind = word2vec_model.get_matrix_of_vectors()

#Reduce Matrix to 2 dimensions
reduced_M = utils.reduce_to_k_dim(M,2)

#Plot characters
utils.plot_embeddings(reduced_M, word2Ind, characters)
##########################################################################################