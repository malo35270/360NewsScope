import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pickle
import json


def NS_Visualization(dossier,date_actions,date_start,date_end,publications,visualization):

    print(dossier,date_actions,date_start,date_end,publications,visualization) 
    
    hierarchical_topics = pd.read_csv(f"{dossier}/database_hierarchical_topics.csv",sep=',',encoding='utf8')
    news_data = pd.read_csv(f"{dossier}/database_update.csv",sep=',',encoding='utf8')
    all_topic = pd.read_csv(f"{dossier}/all_topics.csv",sep=',',encoding='utf8').iloc[1:].reset_index(drop=True)

    if date_actions != [] :
        news_data = news_data.isin({'year': date_actions,'publication':publications})

    


    noms_uniques = news_data['publication'].unique()
    cmap_complete = plt.cm.tab20
    colors = cmap_complete.colors[:len(noms_uniques)]

    cmap_custom = ListedColormap(colors)
    couleur_par_journal = {journal: cmap_custom.colors[i] for i, journal in enumerate(noms_uniques)}
    news_data['Couleur'] = news_data['publication'].map(couleur_par_journal)



    news_net = nx.Graph()   
    max_original_topic = hierarchical_topics.Parent_ID.astype(int).min() - 1

    topic_to_name = dict(zip(hierarchical_topics.Child_Left_ID, hierarchical_topics.Child_Left_Name))
    topic_to_name.update(dict(zip(hierarchical_topics.Child_Right_ID, hierarchical_topics.Child_Right_Name)))
    topic_to_name.update(dict(zip(hierarchical_topics.Parent_ID, hierarchical_topics.Parent_Name)))

    topic_to_name = {topic: name for topic, name in topic_to_name.items()}
    tree = {row[1].Parent_ID: [row[1].Child_Left_ID, row[1].Child_Right_ID]
            for row in hierarchical_topics.iterrows()}


    for parent,childs in tree.items():
            src = parent
            src_names = topic_to_name[parent]
            topic_str, distance = hierarchical_topics.loc[hierarchical_topics['Parent_ID'] == parent, ['Topics', 'Distance']].values[0]
            topics = set(int(topic.strip()) for topic in topic_str.strip('[]').split(','))
            news_net.add_node(src, name = src_names, title=src,size=len(topics), color='red')
            for child in childs:
                    dst = child
                    dst_names = topic_to_name[child]
                    count = all_topic.loc[all_topic['Topic'] == child, ['Count']].values
                    if len(count) ==0 :
                            news_net.add_node(dst, name = dst_names, title=dst, size = 1, color='blue')
                    else : 
                            news_net.add_node(dst, name = dst_names, title=dst, size = int(count[0][0]), color='blue')
                    news_net.add_edge(src, dst) 
            
    number_of_topic = len(news_net.nodes)
            
    for index,row in news_data.iterrows():
            if int(row['topic']) != -1 :
                    news_net.add_node(row['id'],name=row['title'],title=row['id'], size = 1, color=row['Couleur'])
                    news_net.add_edge(row['topic'],row['id'])

    
    pos = nx.spring_layout(news_net, iterations=15, dim=2)

    with open('positions.pickle', 'wb') as f:
        pickle.dump(pos, f)

    graph_json = nx.node_link_data(news_net) 

    with open("mon_graphe.json", "w") as f:
        json.dump(graph_json, f)

    fig_nx, ax = plt.subplots(figsize=(30, 18))
    ax.axis("off")
    plot_options = { "with_labels": False, "width": 0.15}
    colors = [news_net.nodes[n]['color'] for n in news_net.nodes]
    sizes = [news_net.nodes[n]['size'] for n in news_net.nodes]
    nx.draw_networkx(news_net, node_size=sizes, node_color=colors,pos=pos, ax=ax, **plot_options)


    news_net_pyvis = Network(height="750px", width="100%", bgcolor="white", font_color="white", select_menu=True, layout=True)
    news_net_pyvis.from_nx(news_net)
    news_net_pyvis.toggle_physics(True)
    news_net_pyvis.show_buttons(True)
    news_net_pyvis.save_graph(f"{dossier}/graphs_pyvis.html") 



    return fig_nx,f"{dossier}/graphs_pyvis.html"

def analyse(dossier):
    news_data = pd.read_csv(f"{dossier}/database_update.csv",sep=',',encoding='utf8')
    list_date = list(map(str, sorted(news_data['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(news_data['publication'].unique())
    list_publication.insert(0,'all')
    print(list_date,list_publication)
    return list_date,list_publication