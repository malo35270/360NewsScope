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
import torch

stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
    # Tokenize the text
    word_tokens = word_tokenize(text)
    # Filter stopwords out of the tokenized text
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    # Join the filtered words back into a string
    return ' '.join(filtered_text)


def preprocessing(files, dossier):
    path = merge_csv(files,dossier)
    dataframe = pd.read_csv(path,sep=',',encoding='utf8')

    dataframe['content_filtered'] = dataframe['content'].apply(remove_stop_words).str.replace('’', '', regex=False)

    
    if torch.cuda.is_available():
        import cuml # type: ignore
        from cuml.cluster import HDBSCAN # type: ignore
        from cuml.manifold import UMAP # type: ignore
        umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.0)
        hdbscan_model = HDBSCAN(min_samples=10, gen_min_span_tree=True)
        topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model,language='english')
    else : 
        topic_model = BERTopic(language='english',verbose=True)

    topics, probs = topic_model.fit_transform(dataframe['content_filtered'])
    all_topics = topic_model.get_topic_info()
    all_topics.to_csv(f'{dossier}/all_topics.csv', index=False,encoding='utf8')
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

    dataframe.to_csv(f'{dossier}/database_update.csv', index=False,encoding='utf8')
    hierarchical_topics.to_csv(f"{dossier}/database_hierarchical_topics.csv",index=False,encoding='utf8')

    list_date = list(map(str, sorted(dataframe['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(dataframe['publication'].unique())
    list_publication.insert(0,'all')

    return [f'{dossier}/all_topics.csv',f'{dossier}/database_update.csv',f"{dossier}/database_hierarchical_topics.csv"], list_date, list_publication


def merge_csv(files,dossier):
        dfs = [pd.read_csv(fichier,sep=',',index_col=0,encoding='utf8') for fichier in files]
        df_final = pd.concat(dfs, ignore_index=True)
        if not os.path.exists(f"{dossier}"):
            os.makedirs(f"{dossier}")
        df_final.to_csv(f"{dossier}/database_merge.csv", index=False,encoding='utf8')
        return f"{dossier}/database_merge.csv"

