import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pickle
import json

import sys
sys.stdout.reconfigure(encoding='utf-8')

def NS_Visualization(folder_path,date_actions,date_start,date_end,publications,visualization):
        print(folder_path,date_actions,date_start,date_end,publications,visualization)
        dict_action_list = {'NetworkX':'networkx', 'Pyvis' : 'pyvis', 'Save Graph': 'save'}
        options_list = {}
        for item in dict_action_list:
                if item in visualization:
                        options_list[dict_action_list[item]] = dict_action_list[item]
                else :
                        options_list[dict_action_list[item]] = ''
        hierarchical_topics = pd.read_csv(f"{folder_path}/database_hierarchical_topics.csv",sep=',',encoding='utf8')
        news_data = pd.read_csv(f"{folder_path}/database_update.csv",sep=',',encoding='utf8')
        all_topic = pd.read_csv(f"{folder_path}/all_topics.csv",sep=',',encoding='utf8').iloc[1:].reset_index(drop=True)
        date_actions = [int(num) for num in date_actions]
        if publications != []:        
                news_data = news_data[news_data['publication'].isin(publications)].reset_index(drop=True)
        if date_actions != [] :
                news_data = news_data[news_data['year'].isin(date_actions)].reset_index(drop=True)
        
        all_topic = all_topic[all_topic['Topic'].isin(news_data['topic'])].reset_index(drop=True)


        noms_uniques = news_data['publication'].unique()
        cmap_complete = plt.cm.tab20
        colors = cmap_complete.colors[:len(noms_uniques)]

        cmap_custom = ListedColormap(colors)
        couleur_par_journal = {journal: cmap_custom.colors[i] for i, journal in enumerate(noms_uniques)}
        news_data['Couleur'] = news_data['publication'].map(couleur_par_journal)



        news_net = nx.Graph()

        topic_to_name = dict(zip(hierarchical_topics.Child_Left_ID, hierarchical_topics.Child_Left_Name))
        topic_to_name.update(dict(zip(hierarchical_topics.Child_Right_ID, hierarchical_topics.Child_Right_Name)))
        topic_to_name.update(dict(zip(hierarchical_topics.Parent_ID, hierarchical_topics.Parent_Name)))

        topic_to_name = {topic: name for topic, name in topic_to_name.items()}
        tree = {row[1].Parent_ID: [row[1].Child_Left_ID, row[1].Child_Right_ID]
                for row in hierarchical_topics.iterrows()}

        hierarchical_topics['Topics'] = hierarchical_topics['Topics'].astype(str).str.strip('[]').str.split(',').apply(lambda x: [int(i.strip()) if i.strip().isdigit() else None for i in x])


        for parent,childs in tree.items():
                src = parent
                src_names = topic_to_name[parent]
                topic, distance = hierarchical_topics.loc[hierarchical_topics['Parent_ID'] == parent, ['Topics', 'Distance']].values[0]
                news_net.add_node(src, name = src_names, title=src,size=len(topic), color='red')
                for child in childs:
                        dst = child
                        dst_names = topic_to_name[child]
                        count = all_topic.loc[all_topic['Topic'] == child, ['Count']].values
                        if len(count) ==0 :
                                news_net.add_node(dst, name = dst_names, title=dst, size = 1, color='blue')
                        else : 
                                news_net.add_node(dst, name = dst_names, title=dst, size = int(count[0][0]), color='blue')
                        news_net.add_edge(src, dst) 
                


        for index,row in news_data.iterrows():
                if int(row['topic']) != -1 :
                        news_net.add_node(row['id'],name=row['title'],title=row['id'], size = 1, color=row['Couleur'])
                        news_net.add_edge(row['topic'],row['id'])


        p = dict(nx.shortest_path(news_net, target=hierarchical_topics.iat[0,0]))
        topic_keys = list(all_topic['Topic'].values)
        values = [p.get(key) for key in topic_keys]
        flat_list = [node for sublist in values for node in sublist]
        unique_values = np.concatenate([np.unique(flat_list), news_data['id'].values])

        list_nodes = [int(value) for value in unique_values]
        #list_nodes = list(unique_values)
        news_net = news_net.subgraph(list_nodes)
        pos = nx.spring_layout(news_net, iterations=50, dim=2)

        if options_list['save'] == 'save':
                with open(f'{folder_path}/positions.pickle', 'wb') as f:
                        pickle.dump(pos, f)
                graph_json = nx.node_link_data(news_net)
                with open(f'{folder_path}/my_graph.json', "w") as f:
                        json.dump(graph_json, f)

        fig_nx, ax = plt.subplots(figsize=(30, 18))
        if options_list['networkx'] == 'networkx':
                ax.axis("off")
                plot_options = { "with_labels": False, "width": 0.15}
                colors = [news_net.nodes[n]['color'] for n in news_net.nodes]
                sizes = [news_net.nodes[n]['size'] for n in news_net.nodes]
                nx.draw_networkx(news_net, node_size=sizes, node_color=colors,pos=pos, ax=ax, **plot_options)

        if options_list['pyvis'] == 'pyvis':
                news_net_pyvis = Network()
                news_net_pyvis.from_nx(news_net)
                news_net_pyvis.barnes_hut()
                html = news_net_pyvis.generate_html()
                html = html.replace("'", "\"")
                
                data = f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera; 
                display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
                allow-scripts allow-same-origin allow-popups 
                allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
                allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""

                with open(f"{folder_path}\graphs_pyvis.html", "w", encoding='utf-8') as f:
                        f.write(data)

        return process_options(options_list,fig_nx,folder_path)

def analyse(folder_path):
    news_data = pd.read_csv(f"{folder_path}/database_update.csv",sep=',',encoding='utf8')
    list_date = list(map(str, sorted(news_data['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(news_data['publication'].unique())
    list_publication.insert(0,'all')
    return list_date,list_publication


def process_options(options_list, fig, dir_path):
        print(options_list, fig, dir_path)
        nx_to_return = None
        pv_to_return = ''
        pickle_to_return = ''
        json_to_return = ''

        if options_list['save'] == 'save':
                pickle_to_return = f"{dir_path}\positions.pickle"
                json_to_return = f"{dir_path}\my_graph.json"
        if options_list['networkx'] == 'networkx':
                nx_to_return = fig
        if options_list['pyvis'] == 'pyvis':
                with open(f"{dir_path}\graphs_pyvis.html", 'r', encoding='utf-8') as file:
                        pv_to_return = file.read()
        return nx_to_return,pv_to_return,[pickle_to_return,json_to_return]