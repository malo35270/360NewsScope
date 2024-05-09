import gradio as gr
from gradio_calendar import Calendar
import seafom
from NS_Preproccessing import merge_csv,preprocessing
from NS_resultat import NS_Visualization, analyse

seafoam = seafom.Seafoam()


def accordion_func(evt: gr.SelectData,s: int):
    if str(evt.value)=='custom' :
        if bool(s):
            return gr.Accordion("Custom Dates", open=True,visible=False),gr.Number(0, label="Switch a on/off", visible=False)
        else : 
            return gr.Accordion("Custom Dates", open=True,visible=True),gr.Number(1, label="Switch a on/off", visible=False)
    else :
        return gr.Accordion("Custom Dates", open=True,visible=bool(s)), gr.Number(s, label="Switch a on/off", visible=False)


def exception():
    raise ValueError("The name of the folder isn't right")   
    
def analyse_gradio(names_folder):
    try : 
        list_actions,list_publications = analyse(names_folder)
        return gr.CheckboxGroup(list_actions,label="Vizualisation", info="Do you want to add some options ?"), gr.CheckboxGroup(list_publications,label="Publications", info="Do you want to add some options ?")
    except :
        exception()
        return None,None


def on_select(evt: gr.SelectData):  # SelectData is a subclass of EventData
    print(f"You selected {evt.value} at {evt.index} from {evt.target}")

with gr.Blocks(theme=seafoam) as app:
    s = gr.Number(0, label="Switch a on/off", visible=False)
    description = gr.Markdown(
    """
    # Welcome to 360 News Score.
     
    """)
    with gr.Row():
        paths = gr.Files(label="Files of data",file_types=[".csv"],scale=3)
        names_folder = gr.Textbox(label='Name for the save folder',scale=1)
    preprocesssing = gr.Button("Preprocesssing")
    with gr.Row():
        date_actions = gr.CheckboxGroup([],label="Vizualisation", info="Do you want to add some options ?")
        with gr.Accordion("Custom Dates",visible=False) as Accordion:
            with gr.Group():
                date_start = Calendar(type="datetime", label="Select a start date", info="Click the calendar icon to bring up the calendar.")
                date_end = Calendar(type="datetime", label="Select a end date", info="Click the calendar icon to bring up the calendar.")
        publications = gr.CheckboxGroup([],label="Publications", info="Do you want to add some options ?")
        visualization = gr.CheckboxGroup(["NetworkX", "Pyvis"], label="Vizualisation", info="Do you want to add some options ?")
    btn = gr.Button("Visualization")
    
    nx_plot = gr.Plot()
    pyvis_html = gr.HTML()

    names_folder.submit(fn=analyse_gradio,inputs=[names_folder],outputs=[date_actions,publications])
    date_actions.select(on_select, None, None)
    date_actions.select(fn=accordion_func,inputs=[s],outputs=[Accordion,s])
    preprocesssing.click(fn=preprocessing,inputs=[paths,names_folder],outputs=[paths,date_actions,publications])
    btn.click(fn=NS_Visualization,inputs=[names_folder,date_actions,date_start,date_end,publications,visualization],outputs=[nx_plot,pyvis_html])
    
    #gr.ClearButton([paths,number_t,number_l,model,dataframe,options,base_prompt,log,plot], scale=1)


   

if __name__ == "__main__":
    
    app.launch(debug=True,show_error=True)
