from keybert import KeyBERT
import pandas as pd
from bertopic import BERTopic
import os
from scipy.cluster import hierarchy as sch
from spacy.lang.en import stop_words
import numpy as np
import nltk
import glob
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


def preprocessing(path, dossier):
    dataframe = pd.read_csv(path,sep=',',encoding='utf8')
    print(dataframe.info())
    print(dataframe.head)

    dataframe['content_filtered'] = dataframe['content'].apply(remove_stop_words).str.replace('’', '', regex=False)

    #BERTopic
    topic_model = BERTopic(language='english',verbose=True)
    topics, probs = topic_model.fit_transform(dataframe['content_filtered'])
    all_topics = topic_model.get_topic_info()
    all_topics.to_csv(f'{dossier}/result/all_topics.csv', index=False,encoding='utf8')
    dataframe['topic'] = topics

    #KeyBERT
    kw_model = KeyBERT(model='all-MiniLM-L6-v2')
    print(dataframe['content_filtered'])
    keywords = kw_model.extract_keywords(dataframe['content_filtered'])
    dataframe['keyword'] = keywords
    
    
    hierarchical_topics = topic_model.hierarchical_topics(dataframe['content_filtered'])
    tree = topic_model.get_topic_tree(hierarchical_topics)
    fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    fig.write_html("figure.html")

    dataframe.to_csv(f'{dossier}/result/database_update.csv', index=False,encoding='utf8')
    hierarchical_topics.to_csv(f"{dossier}/result/database_hierarchical_topics.csv",index=False,encoding='utf8')


def merge_csv(files,dossier):
        dfs = [pd.read_csv(fichier,sep=',',index_col=0,encoding='utf8') for fichier in files]
        df_final = pd.concat(dfs, ignore_index=True)
        df_final.to_csv(f"{dossier}/database_merge.csv", index=False,encoding='utf8')
        return f"{dossier}/database_merge.csv"

if __name__ == '__main__':

    dossier = 'data/archive'
    fichiers_csv = glob.glob(f'{dossier}/*.csv')

    merge_path_csv = merge_csv(fichiers_csv,dossier)
    
    preprocessing(merge_path_csv,dossier)
        