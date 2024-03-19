from keybert import KeyBERT
import pandas as pd
from bertopic import BERTopic
import os

def preprocessing(path):
    dataframe = pd.read_csv(path,sep=',')
    print(dataframe.head())
    dataframe = dataframe.head(1000)
    #BERTopic
    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(dataframe['content'])
    print(topic_model.get_topic_info())
    dataframe['topic'] = topics

    #KeyBERT
    kw_model = KeyBERT(model='all-MiniLM-L6-v2')
    keywords = kw_model.extract_keywords(dataframe['content'])
    dataframe['keyword'] = keywords
    
    print(dataframe.head())

    #Save the dataframe in a csv
    #dataframe.to_csv(f'{path}.csv', index=False)

if __name__ == '__main__':

    dossier = 'archive/test'

    for fichier in os.listdir(dossier):
        path_file = os.path.join(dossier, fichier)
        
        if fichier.endswith('.csv'):
            preprocessing(path_file)


#https://www.youtube.com/watch?v=IZCScM_gB94&ab_channel=Cohere