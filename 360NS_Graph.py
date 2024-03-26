import networkx as nx
import pandas as pd

data = {'source': [1, 2, 3, 4],
        'target': [2, 3, 4, 1]}
df = pd.DataFrame(data)


G = nx.Graph() # Create an empty undirected graph (or nx.DiGraph() for a directed graph)
# Add nodes from the 'source' and 'target' columns
G.add_nodes_from(df['source'])
G.add_nodes_from(df['target'])
# Add edges from the DataFrame
edges = [(row['source'], row['target']) for index, row in df.iterrows()]
G.add_edges_from(edges)



import matplotlib.pyplot as plt
# Draw the graph
pos = nx.spring_layout(G) # Define the layout for node positioning
nx.draw(G, pos, with_labels=True, node_size=300, node_color='skyblue', font_size=10, font_color='black')
# Display the graph
plt.show()