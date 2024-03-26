from keybert import KeyBERT
import pandas as pd
from bertopic import BERTopic
import os
from scipy.cluster import hierarchy as sch
from spacy.lang.en import stop_words
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
    # Tokenize the text
    word_tokens = word_tokenize(text)
    # Filter stopwords out of the tokenized text
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    # Join the filtered words back into a string
    return ' '.join(filtered_text)


def preprocessing(path):
    dataframe = pd.read_csv(path,sep=',',index_col=0)
    print(dataframe.head())

    dataframe = dataframe.head(10000)

    dataframe['content_filtered'] = dataframe['content'].apply(remove_stop_words).str.replace('’', '', regex=False)

    #BERTopic
    topic_model = BERTopic(language='english',verbose=True)
    topics, probs = topic_model.fit_transform(dataframe['content_filtered'])
    """topic_labels = topic_model.generate_topic_labels(nr_words=5,topic_prefix=False,word_length=15,separator="-")
    topic_model.set_topic_labels(topic_labels)"""
    print(topic_model.get_topic_info())
    dataframe['topic'] = topics

    #KeyBERT
    kw_model = KeyBERT(model='all-MiniLM-L6-v2')
    keywords = kw_model.extract_keywords(dataframe['content_filtered'])
    dataframe['keyword'] = keywords
    
    print(dataframe.head())


    # Hierarchical topics
    linkage_function = lambda x: sch.linkage(x, 'single', optimal_ordering=True)
    hierarchical_topics = topic_model.hierarchical_topics(dataframe['content_filtered'], linkage_function=linkage_function)
    print(hierarchical_topics)
    tree = topic_model.get_topic_tree(hierarchical_topics)
    topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)

    #Save the dataframe in a csv
    #dataframe.to_csv(f'{path}.csv', index=False)

if __name__ == '__main__':

    dossier = 'archive/test'

    for fichier in os.listdir(dossier):
        path_file = os.path.join(dossier, fichier)
        
        if fichier.endswith('.csv'):
            preprocessing(path_file)


#https://www.youtube.com/watch?v=IZCScM_gB94&ab_channel=Cohere