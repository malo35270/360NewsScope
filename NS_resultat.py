import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np
import os
import matplotlib.pyplot as plt
import argparse
from matplotlib.colors import ListedColormap
import matplotlib
import pickle
import json

import sys
sys.stdout.reconfigure(encoding='utf-8')

def NS_Visualization(folder_path,years_actions,date_start,date_end,publications,visualization):
        dict_action_list = {'NetworkX':'networkx', 'Pyvis' : 'pyvis', 'Pickle positions':"pos", 'JSON Graph':"json"}
        options_list = {}
        for item in dict_action_list:
                if item in visualization:
                        options_list[dict_action_list[item]] = dict_action_list[item]
                else :
                        options_list[dict_action_list[item]] = ''
        hierarchical_topics = pd.read_csv(f"{folder_path}/database_hierarchical_topics.csv",sep=',',encoding='utf8')
        news_data = pd.read_csv(f"{folder_path}/database_update.csv",sep=',',encoding='utf8')
        news_data['date'] = pd.to_datetime(news_data['date'])
        all_topic = pd.read_csv(f"{folder_path}/all_topics.csv",sep=',',encoding='utf8').iloc[1:].reset_index(drop=True)

        if publications != [] and 'NONE' not in publications:        
                news_data = news_data[news_data['publication'].isin(publications)].reset_index(drop=True)
        if years_actions != [] and 'NONE' not in years_actions:
                if 'custom' in years_actions:
                        years_actions.remove('custom')
                        filtered_datetime = news_data[(news_data['date'] >= date_start) & (news_data['date'] <= date_end)]
                        years_actions = [int(num) for num in years_actions]
                        filtered_year = news_data[news_data['year'].isin(years_actions)]
                        news_data = pd.concat([filtered_datetime, filtered_year]).drop_duplicates().reset_index(drop=True)
                else :
                        years_actions = [int(num) for num in years_actions]
                        news_data = news_data[news_data['year'].isin(years_actions)].reset_index(drop=True)
        all_topic = all_topic[all_topic['Topic'].isin(news_data['topic'])].reset_index(drop=True)


        noms_uniques = news_data['publication'].unique()
        cmap_complete = ['orange', 'brown', 'pink', 'gray', 'olive', 'cyan' , 'purple', 'green']
        colors = cmap_complete[:len(noms_uniques)]

        couleur_par_journal = {journal: colors[i] for i, journal in enumerate(noms_uniques)}
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
        news_net = news_net.subgraph(list_nodes)
        pos = nx.nx_agraph.graphviz_layout(
                news_net,
                prog="twopi",
                root=hierarchical_topics['Parent_ID'].astype(int).max(),
                args="-Granksep='1.2 equally' -Goverlap='scale'"
        )
        if options_list['pos'] == 'pos':
                with open(f'{folder_path}/positions.pickle', 'wb') as f:
                        pickle.dump(pos, f)
        if options_list['json'] == 'json': 
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
                news_net_pyvis.from_nx(nx_graph=news_net)
                neighbor_map = news_net_pyvis.get_adj_list()                        
                for node in news_net_pyvis.nodes:
                        print(node)
                        node.update({'physics': False, 'x':pos[node['id']][0], 'y':pos[node['id']][1]})
                        node_title_str = node["name"]
                        neighbors_str = ", ".join(news_net_pyvis.get_node(neighbor)['name'] for neighbor in neighbor_map[node["id"]])
                        node["title"] = node_title_str + "\n Neighbors : [" + neighbors_str + "]"
                        node["value"] = len(neighbor_map[node["id"]])
                with open('options.json', 'r') as f:
                        options_viz = f.read()
                        news_net_pyvis.set_options(options_viz)
                
                html = news_net_pyvis.generate_html()
                html = html.replace("'", "\"")
                
                data = f"""<iframe style="width: 100%; height: 600px;margin:0 auto" name="result" allow="midi; geolocation; microphone; camera; 
                display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
                allow-scripts allow-same-origin allow-popups 
                allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
                allowpaymentrequest="" frameborder="0" srcdoc='{html}'></iframe>"""

                with open(f"{folder_path}/graphs_pyvis.html", "w", encoding='utf-8') as f:
                        f.write(data)

        return process_options(options_list,fig_nx,folder_path)

def analyse(folder_path):
    news_data = pd.read_csv(f"{folder_path}/database_update.csv",sep=',',encoding='utf8')
    list_date = list(map(str, sorted(news_data['year'].astype(int).unique())))
    list_date.append('custom')
    list_publication = sorted(news_data['publication'].unique())
    return list_date,list_publication


def process_options(options_list, fig, dir_path):
        nx_to_return = None
        pv_to_return = None
        pickle_to_return = None
        json_to_return = None

        if options_list['pos'] == 'pos':
                pickle_to_return = f"{dir_path}\positions.pickle"
        if options_list['json'] == 'json':
                json_to_return = f"{dir_path}\my_graph.json"
        if options_list['networkx'] == 'networkx':
                nx_to_return = fig
        if options_list['pyvis'] == 'pyvis':
                with open(f"{dir_path}\graphs_pyvis.html", 'r', encoding='utf-8') as file:
                        pv_to_return = file.read()
        return nx_to_return,pv_to_return,pickle_to_return,json_to_return


if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="NS_Visualization function arguments")
        parser.add_argument('--folder_path', type=str, required=True, help='Path to the folder containing data')
        parser.add_argument('--example', action='store_true', help='Start a example, need the folder_path')
        parser.add_argument('--years_actions', nargs='*',type=str,default=[], help='List of action years (can be empty, pass "NONE")')
        parser.add_argument('--date_start', type=str, help='Start date in YYYY-MM-DD HH:MM:SS format')
        parser.add_argument('--date_end', type=str, help='End date in YYYY-MM-DD HH:MM:SS format')
        parser.add_argument('--publications', nargs='*', default=[], help='List of publications (can be empty, pass "NONE")')
        parser.add_argument('--visualization',type=str, nargs='+', help='Types of visualization to use')

        args = parser.parse_args()
        if args.example:
                nx_to_return,pv_to_return,pickle_to_return,json_to_return =  NS_Visualization(args.folder_path, ['2011','2012', '2013','2014', '2013'], "2024-05-11 00:00:00", "2024-05-11 00:00:00", ['Atlantic', 'New York Times', 'CNN','Breitbart'] ,['Pyvis', 'NetworkX'])
                plt.show()
        else:
        # Ensure that all parameters are provided for normal operations
                if not all([args.years_actions, args.date_start, args.date_end, args.publications, args.visualization]):
                        parser.error("The --years_actions, --date_start, --date_end, --publications, and --visualization parameters are required unless --example is specified.")
                
                nx_to_return, pv_to_return, pickle_to_return, json_to_return = NS_Visualization(
                                                                                        args.folder_path,
                                                                                        args.years_actions,
                                                                                        args.date_start,
                                                                                        args.date_end,
                                                                                        args.publications,
                                                                                        args.visualization
                                                                                        )
                plt.show()