from keybert import KeyBERT
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import os
from scipy.cluster import hierarchy as sch
from spacy.lang.en import stop_words
import numpy as np
import argparse
import nltk
import glob
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import torch

stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
    if not isinstance(text, str):
        return ""
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_text)


def preprocessing(files, dossier):
    path = merge_csv(files,dossier)
    file_number = split_csv(path,dossier)
    if not os.path.exists(f"{dossier}/BERTopic"):
            os.makedirs(f"{dossier}/BERTopic")
    for i in range(file_number):
        dataframe = pd.read_csv(f"{dossier}_part{i}.csv",sep=',',encoding='utf8')
        try :
            dataframe['content_filtered'] = dataframe['article'].fillna('').apply(remove_stop_words).str.replace('’', '', regex=False)
        except KeyError as e:
            print(f"KeyError: {e}. 'article' column does not exist. Trying 'content' column.")
            try:
                dataframe['content_filtered'] = dataframe['content'].fillna('').apply(remove_stop_words).str.replace('’', '', regex=False)
            except KeyError as e:
                print(f"KeyError: {e}. Neither 'article' nor 'content' columns exist in the DataFrame.")
        
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
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        topic_model.save(f"{dossier}/BERTopic/_part{i}_bertopic_model", serialization="safetensors", save_ctfidf=True, save_embedding_model=embedding_model)

    merge_model  = BERTopic.load(f"{dossier}/BERTopic/_part{0}_bertopic_model")
    for i in range(1,file_number):
        merge_model_b = BERTopic.load(f"{dossier}/BERTopic/_part{i}_bertopic_model")
        merged_model = BERTopic.merge_models([merge_model, merge_model_b])
    
    all_topics = merge_model.get_topic_info()
    all_topics.to_csv(f'{dossier}/all_topics.csv', index=False,encoding='utf8')
    dataframe['topic'] = topics  
    
    hierarchical_topics = merge_model.hierarchical_topics(dataframe['content_filtered'])

    dataframe.to_csv(f'{dossier}/database_update.csv', index=False,encoding='utf8')
    hierarchical_topics.to_csv(f"{dossier}/database_hierarchical_topics.csv",index=False,encoding='utf8')

    list_date = list(map(str, sorted(dataframe['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(dataframe['publication'].unique())

    return [f'{dossier}/all_topics.csv',f'{dossier}/database_update.csv',f"{dossier}/database_hierarchical_topics.csv"], list_date, list_publication


def merge_csv(files,dossier):
        dfs = [pd.read_csv(fichier,sep=',',index_col=0,encoding='utf8') for fichier in files]
        df_final = pd.concat(dfs, ignore_index=True)
        if not os.path.exists(f"{dossier}"):
            os.makedirs(f"{dossier}")
        df_final.to_csv(f"{dossier}/database_merge.csv", index=False,encoding='utf8')
        return f"{dossier}/database_merge.csv"

def split_csv(file_path, chunk_size=100000):
    chunk_iter = pd.read_csv(file_path, chunksize=chunk_size,sep=',',encoding='utf8')
    file_number = 0
    for chunk in chunk_iter:
        new_file_path = f"{file_path[:-4]}_part{file_number}.csv"
        chunk.to_csv(new_file_path, index=False,encoding='utf8')
        file_number += 1
    return file_number

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge CSV files and preprocess data")
    parser.add_argument('--files', nargs='+', required=True, help="List of file paths to be merged")
    parser.add_argument('--dossier', type=str, required=True, help="Path to the output folder where the merged file will be stored")
    
    args = parser.parse_args()
    preprocessing(args.files, args.dossier)