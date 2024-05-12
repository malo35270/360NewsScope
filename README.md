# Welcome to 360 News Scope!
Welcome to 360 News Scope, where you can explore a visualisation tool for exploring US newspaper articles in the [All the News 2.0](https://components.one/datasets/all-the-news-2-news-articles-dataset) database structure using NLP algorithms ( KeyBert & BERTopic ). 


You can use the interface made with gradio for a friendly use or directly use the preprocessing or visualisation.

## Gradio Interface : 
    python app.py
### Preprocessing process :
1. **Files of data :** Load csv file of the data file. The data file must have a 'content', 'year' and 'publication' columns.
2. **Name for the save folder :** Give a name where the resut will be save.
3. **Preprocessing button :** Press the button.

### Visualisation process :
1. **Name for the save folder :** Give a name where the resut if saved, press enter for load the year and publication interface.
2. **Apply filter :** Select year, date or publication you want to see. If nothing this select, the process don't apply filter.
3. **Select Actions to made :** Select the actions to made : NetworkX create a image of the networkx, Pyvis creat a iframe to explore dynamicly the network, Pickle positions and Json graph creat file to download.
4. **Visualization button :** Press the button.

## NS_Preprocessing File : 

Merge CSV files and preprocess data

##### options:
    -h, --help            show this help message and exit
    --files FILES [FILES ...]
                        List of file paths to be merged
    --dossier DOSSIER     Path to the output folder where the merged file will be stored

## NS_result File : 
Launch the visualisation 
###### options :
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

                        
