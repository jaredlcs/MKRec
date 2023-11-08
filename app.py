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
import requests

# Tool using Youtube API to find the top video
API_KEY = os.getenv('YOUTUBE_API_KEY')  # Use the YouTube API key from your .env

def find_top_video(query):
    url = f'https://www.googleapis.com/youtube/v3/search?key={API_KEY}&q={query}&part=snippet&type=video&maxResults=1'
    
    response = requests.get(url)
    data = response.json()

    if 'items' in data:
        top_result = data['items'][0]
        video_id = top_result['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return video_url
    else:
        return 'No search results found for the query.'

def create_video_link(video_url, keyboard_name):
    return f"{video_url} ({keyboard_name} Video)"
    
def generate_video_list(results):
    videos = []
    for keyboard_data in results:
        keyboard_name = keyboard_data.get('keyboard')
        if keyboard_name:
            video_url = find_top_video(keyboard_name)
            videos.append({'keyboard': keyboard_name, 'link': create_video_link(video_url, keyboard_name)})
        else:
            videos.append({'keyboard': 'No Video Link Yet', 'link': ''})
    return videos




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
    videos = generate_video_list(results)

    try:
        df = pd.DataFrame(results, columns=['keyboard', 'layout', 'mounting style', 'price', 'features'])
        videosDF = pd.DataFrame(videos, columns=['keyboard', 'video (copy / paste into URL)'])
        return df, videosDF
    except Exception as e:
        raise gr.Error(e.message)
    

with gr.Blocks() as demo:
    with gr.Tab("Custom Keyboard Kit Finder"):
        with gr.Row():
            with gr.Column():
                layout = gr.Dropdown(["60%", "65%", "75%", "FRL", "TKL", "FRL-TKL", "Full Sized",], label="Layout")
                hotswap = gr.Dropdown(["Yes", "No", "No Preference"], label="Hotswap")
                budget = gr.Dropdown([100, 200, 300, 400, 500, 600, "None"], label="Budget")
                mounting_style = gr.Dropdown(["Gasket-mounted", "Tray mount", "Top mount", "Plate mount", "No Preference"], label="Mounting Style")
                flexcuts = gr.Dropdown(["Yes", "No", "No Preference"], label = "Flex cuts")

                n_results = gr.Slider(label="Results to Display (There may not be enough keyboards that meet your preferences. In which case, we will fill the results with what best fits)", minimum=0, maximum=10, value=2, step=1)
                btn = gr.Button(value="Submit")

                table = gr.Dataframe(label="Results", headers=['keyboard', 'layout', 'mounting style', 'price', 'features'])
                table_links = gr.Dataframe(label="Video Links", headers=['keyboard', 'link'])

            btn.click(search, inputs=[layout, hotswap, budget, mounting_style, flexcuts, n_results], outputs=[table, table_links])

    demo.launch(share=True)