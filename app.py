import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import streamlit as st
from google.cloud import bigquery
import os
from io import BytesIO
from tempfile import NamedTemporaryFile
import json
from google.oauth2 import service_account
from datetime import datetime, timedelta

st.title("Word Cloud Generator")

# bigquery client login
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)

# Define your SQL query
sql_query_template = """
WITH hashtags AS (
  SELECT
  hashtag,
  post_id,
  block_timestamp
  FROM `lens-public-data.polygon.public_hashtag`
  WHERE NOT REGEXP_CONTAINS(hashtag, r'^\\d+$')
    AND block_timestamp >= '{start_date}'
    AND block_timestamp <= '{end_date}'
),
stats AS (
  SELECT
  publication_id,
  total_amount_of_collects,
  total_amount_of_mirrors,
  total_amount_of_comments,
  total_upvotes,
  total_downvotes
  FROM `lens-public-data.polygon.public_publication_stats`
),
hashtag_counts AS (
  SELECT
  post_id,
  COUNT(hashtag) as hashtag_count
  FROM hashtags
  GROUP BY post_id
  HAVING hashtag_count <= 3
),
aggregated_hashtags AS (
  SELECT
  hashtag,
  COUNT(h.post_id) as post_count,
  SUM(s.total_amount_of_collects) as total_collects,
  SUM(s.total_amount_of_mirrors) as total_mirrors,
  SUM(s.total_amount_of_comments) as total_comments,
  SUM(s.total_upvotes) as total_upvotes,
  SUM(s.total_downvotes) as total_downvotes
  FROM hashtags h
  INNER JOIN hashtag_counts hc ON hc.post_id = h.post_id
  LEFT JOIN stats s ON s.publication_id = h.post_id
  GROUP BY hashtag
)

SELECT *
  FROM aggregated_hashtags
ORDER BY total_upvotes DESC
LIMIT 300
"""

# Add date input widgets
start_date = st.sidebar.date_input("Start date", value=datetime.now() - timedelta(days=90))
end_date = st.sidebar.date_input("End date", value=datetime.now())

# Format the dates for the SQL query
start_date_str = start_date.strftime("%Y-%m-%d 00:00:00")
end_date_str = end_date.strftime("%Y-%m-%d 23:59:59")

# Fill in the placeholders with the selected dates
sql_query = sql_query_template.format(start_date=start_date_str, end_date=end_date_str)

# Wrap the data loading part with st.spinner
with st.spinner("Loading data..."):
    # Run the query
    df = client.query(sql_query).to_dataframe()

st.set_option('deprecation.showPyplotGlobalUse', False)

# add toggle for white or black background
background_color = st.radio("Choose background color:", ["black", "white"])

def process_mask_image(mask_image):
    mask_image = mask_image.convert('RGBA')
    
    # Remove the white outline
    pixels = mask_image.load() # create the pixel map
    for y in range(mask_image.size[1]): # for every pixel:
        for x in range(mask_image.size[0]):
            if pixels[x, y][:3] == (255, 255, 255): # if white,
                pixels[x, y] = (255, 255, 255, 0) # set the alpha to 0
                
    background = Image.new('RGBA', mask_image.size, (255, 255, 255))
    merged_image = Image.alpha_composite(background, mask_image)
    processed_mask = merged_image.convert('L')

    return np.array(processed_mask)


def generate_word_cloud(frequencies, mask_image, background_color):
    stopwords = set(STOPWORDS)
    mask = process_mask_image(mask_image)
    wordcloud = WordCloud(stopwords=stopwords, background_color=background_color, max_words=1000, mask=mask,
                          contour_width=1, contour_color='white', max_font_size=200).generate_from_frequencies(frequencies)

    with NamedTemporaryFile(suffix=".png") as temp_file:
        wordcloud.to_file(temp_file.name)
        temp_image = Image.open(temp_file.name)
        st.image(temp_image)


mask_image = Image.open("lens_logo_thick.png")

# Combine the hashtags and total_upvotes from the DataFrame into a dictionary
hashtags_frequencies = df.set_index('hashtag')['total_upvotes'].to_dict()


with st.spinner("Generating word cloud..."):
    generate_word_cloud(hashtags_frequencies, mask_image, background_color)


st.write(df)
