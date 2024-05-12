# Welcome to 360 News Scope!
Welcome to 360 News Scope, a comprehensive visualization tool for exploring U.S. newspaper articles within the [All the News 2.0](https://components.one/datasets/all-the-news-2-news-articles-dataset) database structure. Our tool leverages advanced NLP algorithms, including KeyBert & BERTopic, to enrich your understanding of news content.

You can interact with our platform through a user-friendly Gradio interface or directly engage with our preprocessing and visualization capabilities.

## Gradio Interface : 

To launch the Gradio interface, run the following command in your terminal:
```bash
    python app.py
```
### Preprocessing process :

Follow these steps to preprocess your data:

1. **Files of data :**  Load a CSV file containing the 'content', 'year', and 'publication' columns.
2. **Name for the save folder :** Specify a folder name where the results will be saved.
3. **Preprocessing button :** Click the button to start preprocessing.

### Visualisation process :

Steps to visualize your data :

1. **Name for the save folder :** Enter a folder name to save the results and load the year and publication selection on the interface.
2. **Apply filter :** Optionally select years, dates, or publications to filter the data. If no filters are selected, no filtering is applied.
3. **Select Actions to made :** Select Actions to Make :
    - NetworkX : Generates an image of the network.
    - Pyvis : Creates an interactive iframe to dynamically explore the network.
    - Pickle Positions and Json Graph : Creates files available for download.
4. **Visualization button :** Click to initiate the visualization process..

## NS_Preprocessing File : 

This script merges CSV files and preprocesses data.

options :
```bash
    -h, --help            show this help message and exit
    --files FILES [FILES ...]
                        List of file paths to be merged
    --dossier DOSSIER     Path to the output folder where the merged file will be stored
```
## NS_result File : 

Launch the visualization process using this script.

options :
```bash
    -h, --help            show this help message and exit
    --folder_path FOLDER_PATH
                        Path to the folder containing data
    --example             Start a example, need the folder_path
    --years_actions [YEARS_ACTIONS ...]
                        List of action years (can be empty, pass "NONE")
    --date_start DATE_START
                          Start date in YYYY-MM-DD HH:MM:SS format
    --date_end DATE_END   End date in YYYY-MM-DD HH:MM:SS format
    --publications [PUBLICATIONS ...]
                          List of publications (can be empty, pass "NONE")
    --visualization VISUALIZATION [VISUALIZATION ...]
                          Types of visualization to use
```
                        
