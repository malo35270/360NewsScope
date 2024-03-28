import os
import pandas as pd
import networkx as nx
from pyvis.network import Network
from IPython.display import display, HTML



def create_network(path_folder):
    news_net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white",notebook=True)

    # set the physics layout of the network
    news_net.barnes_hut()
    news_data = pd.read_csv(f"{path_folder}/database_update.csv")
    print(news_data)
    hierarchical_topics = pd.read_csv(f"{path_folder}/database_hierarchical_topics.csv",index_col=0)
    print(hierarchical_topics.head())


    sources = pd.concat([hierarchical_topics["Parent_ID"], hierarchical_topics["Parent_ID"]], ignore_index=True)
    targets = pd.concat([hierarchical_topics["Child_Left_ID"], hierarchical_topics["Child_Right_ID"]], ignore_index=True)
    weights = pd.concat([hierarchical_topics["Distance"], hierarchical_topics["Distance"]], ignore_index=True)

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
                    src = e[0]
                    dst = e[1]
                    w = e[2]

                    news_net.add_node(src, src, title=src)
                    news_net.add_node(dst, dst, title=dst)
                    news_net.add_edge(src, dst, value=w)

    neighbor_map = news_net.get_adj_list()

    """# add neighbor data to node hover data
    for node in news_net.nodes:
                    node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
                    node["value"] = len(neighbor_map[node["id"]])
    """
    #news_net.show("gameofthrones.html")
    news_net.save_graph("graphs.html")
    return news_net


if __name__ == '__main__':

    dossier = 'archive/test/result'
    graph = create_network(dossier)

    
    with open('archive/test/result/graphs.html', 'r') as file:
        html_content = file.read()
# Display the HTML content
    display(HTML(html_content))