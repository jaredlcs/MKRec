# GPT Powered Mechanical Keyboard Recommendations

This project aims to provide you with recommendations for mechanical keyboards based on your preferences. The recommendation system utilizes a database of mechanical keyboards, their features, and sound test videos from YouTube. You can input your preferences, and the system will generate recommendations for you.

## Features

- **Database**: The system maintains a database of mechanical keyboards from various manufacturers, including:
  - QwertyKeys
  - Meletrix
  - Wuque Studios
  - Pixelspace
  - Vertex
  - TKD
  - RAMA
  - Keychron
  - Glorious

- **Additional Keyboards**: The database is continuously expanding. The following keyboards are planned to be added soon:
  - DROP
  - AKKO
  - Monsgeek
  - Epomaker
  - Wind Studio
  - IQUNIX

- **Data Preprocessing**: The data is loaded from a JSON file. For better handling, the prices are extracted and converted to floating-point values.

- **YouTube Integration**: The system leverages the YouTube API to find top sound test videos for each keyboard in the database.

- **Embedding and Query**: It uses the ChromaDB library to embed keyboard data and search for similar keyboards based on your query.

## How to Use

1. Make sure you have the required libraries and dependencies installed. You can install them using `pip`.

2. You will need to set up the YouTube API Key. You should store this API Key in a file named `.env` in your project directory.

   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

3. Run the system to access the recommendation interface. You can input your preferences, including the layout, hotswap, budget, mounting style, flex cuts, and the number of results you want to display.

4. Click the "Submit" button to get recommendations. The system will generate a table of recommended keyboards and corresponding YouTube video links where you can explore their sound tests.

5. Explore the recommended keyboards and watch  to make an informed decision.

## Additional Information

- The system relies on Python, Gradio for creating the interface, and Pandas for data manipulation.

- The database is continuously updated and expanded to provide more options and accurate recommendations.

- Enjoy exploring the world of mechanical keyboards and finding the perfect one for your preferences.