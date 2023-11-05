import json

def load_data():
    with open("data.json") as f:
        data = json.load(f)
        for item in data:
            # Extract the numeric part of the price and convert it to a float
            item["price"] = float(item["price"].strip('$').replace(',', ''))
    return data

data = load_data()
print(data)

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
import os

import chromadb
from chromadb.utils import embedding_functions


def get_chroma_collection(collection_name):
    chroma_client = chromadb.PersistentClient(path=".")

    chroma_client.delete_collection(name="keyboards")

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    api_base=os.getenv("OPENAI_API_BASE"),
                    model_name="text-embedding-ada-002"
                )

    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)
    return collection

collection = get_chroma_collection("keyboards")


def add_data_to_collection(data, collection):
    documents = []
    metadatas = []
    ids = []

    for i, keyboard in enumerate(data):
        keyboard_name= keyboard['keyboard']
        layout = keyboard['layout']
        description = keyboard['description']
        features = keyboard['features']
        colors = keyboard['colors']

        #what to embed
        embeddable_string = f"{keyboard_name} {description} {layout} {features}"
        documents.append(embeddable_string)

        # lets just store everything we have as metadata
        metadatas.append(keyboard)

        # lets use the index as the id
        ids.append(str(i))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

add_data_to_collection(data, collection)

def get_results(query, budget, mounting_style, n_results):
    metadatas = []
    results = collection.query(query_texts=[query], n_results=n_results)
    
    for i in range(n_results):
        metadata = results["metadatas"][0][i]

        if budget != "None":
            price = metadata.get("price", 0) 
            
            # If user has a mounting preference and a budget
            if mounting_style != "No Preference":
                mountingDB = metadata.get("mounting style", "")
                if budget is None or price <= float(budget) and mountingDB == mounting_style:
                    metadatas.append(metadata)
            
            #User has NO mounting preference and a budget
            else:
                if budget is None or price <= float(budget):
                    metadatas.append(metadata)

        #User has a mounting preference, but no budget
        elif mounting_style != "No Preference": 
            mountingDB = metadata.get("mounting style", "")
            if mountingDB == mounting_style:
                metadatas.append(metadata)

        #User has no mounting preference or budget
        else:
            metadatas.append(metadata)

    return metadatas

results = get_results(f"60% layout", 200, "No Preference", n_results=3)

for result in results:
    print(result)

import gradio as gr
import pandas as pd

def search(layout, hotswap, budget, mounting_style, flexcuts, n_results):
    # Create a query based on user selections
    if hotswap == "Yes":
        if flexcuts == "Yes":
            query = f"{layout} layout with hotswap and flexcut PCB."
        elif flexcuts == "No":
            query = f"{layout} layout with hotswap and no flexcuts for the PCB."
        else:
            query = f"{layout} layout with hotswap PCB."

    elif hotswap == "No":
        if flexcuts == "Yes":
            query =f"{layout} layout with flexcut PCB. soldered."
        elif flexcuts == "No":
            query = f"{layout} layout with solder and no flexcuts for the PCB."
        else:
            query = f"{layout} layout with solder PCB"
    
    else:
        query = f"{layout} layout"
        
    results = get_results(query, budget, mounting_style, n_results=n_results)
    try:
        df = pd.DataFrame(results, columns=['keyboard', 'layout', 'mounting style', 'price', 'features'])
        return df
    except Exception as e:
        raise gr.Error(e.message)

with gr.Blocks() as demo:
    with gr.Tab("Custom Keyboard Kit Finder"):
        with gr.Row():
            with gr.Column():
                layout = gr.Dropdown(["60%","65%","75%", "FRL", "TKL", "Full Sized"], label="Layout")
                hotswap = gr.Dropdown(["Yes", "No", "No Preference"], label="Hotswap")
                budget = gr.Dropdown([200, 300, 400, 500, "None"], label="Budget")
                mounting_style = gr.Dropdown(["Gasket-mounted", "Tray mount", "No Preference"], label="Mounting Style")
                flexcuts = gr.Dropdown(["Yes", "No", "No Preference"], label = "Flex cuts")

                n_results = gr.Slider(label="Results to Display (There may not be enough keyboards that meet your preferences. In which case, we will fill the results with what best fits)", minimum=0, maximum=10, value=2, step=1)
                btn = gr.Button(value="Submit")

                table = gr.Dataframe(label="Results", headers=['keyboard', 'layout', 'mounting style', 'price', 'features'])
            btn.click(search, inputs=[layout, hotswap, budget, mounting_style, flexcuts, n_results], outputs=[table])
    demo.launch(share=True)