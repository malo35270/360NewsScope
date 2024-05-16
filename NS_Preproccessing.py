import pandas as pd
from bertopic import BERTopic
import os
from spacy.lang.en import stop_words
import argparse
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import torch
os.environ["TOKENIZERS_PARALLELISM"] = "false"
stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
    if not isinstance(text, str):
        return ""
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return ' '.join(filtered_text)


def preprocessing(files, dossier):
    path = merge_csv(files,dossier)

    if not os.path.exists(f"{dossier}/BERTopic"):
            os.makedirs(f"{dossier}/BERTopic")
    dataframe = pd.read_csv(f"{dossier}/database.csv",encoding='utf8')
    try :
        dataframe['content_filtered'] = dataframe['article'].fillna('').apply(remove_stop_words).str.replace('’', '', regex=False)
        columns_data = 'article'
    except KeyError as e:
        print(f"KeyError: {e}. 'article' column does not exist. Trying 'content' column.")
        try:
            dataframe['content_filtered'] = dataframe['content'].fillna('').apply(remove_stop_words).str.replace('’', '', regex=False)
            columns_data = 'content'
        except KeyError as e:
            print(f"KeyError: {e}. Neither 'article' nor 'content' columns exist in the DataFrame.")
    
    if check_cuda_and_compute_capability():
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
        topic_model.save(f"{dossier}/BERTopic/database_bertopic_model", serialization="safetensors", save_ctfidf=True, save_embedding_model=embedding_model)
    
    if not os.path.exists(f"{dossier}/Preproccessing"):
            os.makedirs(f"{dossier}/Preproccessing")
    
    all_topics = topic_model.get_topic_info()
    all_topics.to_csv(f'{dossier}/Preproccessing/all_topics.csv', index=False,encoding='utf8')

    dataframe['topic'] = topic_model.topics_

    if 'date' not in dataframe.columns: 
        dataframe['date']= pd.to_datetime(dataframe[['year', 'month', 'day']])
    dataframe.to_csv(f'{dossier}/Preproccessing/database_update.csv', index=False,encoding='utf8')
        
    hierarchical_topics = topic_model.hierarchical_topics(dataframe['content_filtered']) 
    hierarchical_topics.to_csv(f"{dossier}/Preproccessing/database_hierarchical_topics.csv",index=False,encoding='utf8')

    list_date = list(map(str, sorted(dataframe['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(dataframe['publication'].unique())

    return [f'{dossier}/Preproccessing/all_topics.csv',f'{dossier}/Preproccessing/database_update.csv',f"{dossier}/Preproccessing/database_hierarchical_topics.csv"], list_date, list_publication
    

def merge_csv(files,dossier):
        dfs = [pd.read_csv(fichier,sep=',',encoding='utf8') for fichier in files]
        df_final = pd.concat(dfs, ignore_index=True)
        if not os.path.exists(f"{dossier}"):
            os.makedirs(f"{dossier}")
        df_final.to_csv(f"{dossier}/database.csv", index=False,encoding='utf8')
        return f"{dossier}/database.csv"

def split_csv(file_path,dossier, chunk_size=100000):
    chunk_iter = pd.read_csv(file_path, chunksize=chunk_size,encoding='utf8')
    file_number = 0
    for chunk in chunk_iter:
        new_file_path = f"{dossier}/database_part_{file_number}.csv"
        chunk.to_csv(new_file_path, index=False,encoding='utf8')
        file_number += 1
    return file_number


def check_cuda_and_compute_capability(required_capability=(7, 0)):
    if torch.cuda.is_available():
        device_index = torch.cuda.current_device()
        capability = torch.cuda.get_device_capability(device_index)
        if capability >= required_capability:
            return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge CSV files and preprocess data")
    parser.add_argument('--files', nargs='+', required=True, help="List of file paths to be merged")
    parser.add_argument('--dossier', type=str, required=True, help="Path to the output folder where the merged file will be stored")
    
    args = parser.parse_args()
    preprocessing(args.files, args.dossier)    