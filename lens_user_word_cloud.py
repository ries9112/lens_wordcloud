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
import base64
from io import StringIO
import re
from collections import Counter
import string

# add custom css
def custom_css():
    st.markdown("""
    <style>
        /* Hide the default Streamlit background */
        .stApp {
            background-color: transparent !important;
        }

        /* Set global text color */
        body {
            color: #4b7f40; /* Dark green */
        }

        /* Customize headings */
        h1, h2, h3, h4, h5 {
            font-family: "Cursive", "Comic Sans MS", sans-serif;
            color: #4b7f40; /* Dark green */
        }

        /* Customize text input */
        .stTextInput input {
            font-family: "Cursive", "Comic Sans MS", sans-serif;
            color: #4b7f40; /* Dark green */
            background-color: #f1f8ea;
        }

        /* Customize input label */
        .stTextInput label {
            color: #4b7f40; /* Dark green */
        }

        /* Customize radio buttons */
        .stRadio label {
            font-family: "Cursive", "Comic Sans MS", sans-serif;
            color: #4b7f40; /* Dark green */
        }

        /* Customize buttons */
        button {
            font-family: "Cursive", "Comic Sans MS", sans-serif;
            background-color: #4b7f40;
            color: white;
        }

        /* Customize tables */
        table {
            font-family: "Cursive", "Comic Sans MS", sans-serif;
            color: #4b7f40; /* Dark green */
            background-color: #f1f8ea;
        }

        /* Customize table header */
        th {
            background-color: #4b7f40;
            color: white;
        }

        /* Customize table rows */
        tr:nth-child(odd) {
            background-color: #f1f8ea;
        }

        tr:nth-child(even) {
            background-color: #c8e4c3;
        }

        /* Customize images */
        img {
            border: 3px solid #4b7f40;
            border-radius: 5px;
        }

    </style>
    """, unsafe_allow_html=True)

    # Add the background GIF using HTML
    st.markdown("""
    <div style="position: fixed; z-index: -1; top: 0; left: 0; right: 0; bottom: 0;">
        <img src="https://raw.githubusercontent.com/lens-protocol/brand-kit/main/Animations/Lens-Anim4_16x10.gif" alt="background gif" style="position: absolute; top: 0; left: 0; bottom: 0; right: 0; width: 100%; height: 100%; object-fit: cover;">
    </div>
    """, unsafe_allow_html=True)

# Call the custom_css function at the beginning of your Streamlit script
custom_css()


st.title("Lens User Word Cloud Generator")

# Add a text input box for entering the user handle
user_handle = st.text_input("Enter a user handle:", "rickydata.lens")

def process_content(content_series):
    content_str = ' '.join(content_series)
    content_str = re.sub(r'http\S+', '', content_str)
    content_str = re.sub(r'\S+\.com\S+', '', content_str)
    content_str = re.sub(r'\@\w+', '', content_str)
    content_str = re.sub(r'\#\w+', '', content_str)
    content_str = content_str.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    return content_str

def process_mask_image(mask_image):
    mask_image = mask_image.convert('RGBA')
    pixels = mask_image.load()
    for y in range(mask_image.size[1]):
        for x in range(mask_image.size[0]):
            if pixels[x, y][:3] == (255, 255, 255):
                pixels[x, y] = (255, 255, 255, 0)
    background = Image.new('RGBA', mask_image.size, (255, 255, 255))
    merged_image = Image.alpha_composite(background, mask_image)
    processed_mask = merged_image.convert('L')
    return np.array(processed_mask)

mask_image = Image.open("lens_logo_thick.png")

# Modify the first query to take the user input
profile_query = f"""
SELECT
  profile_id,
  owned_by,
  name,
  handle,
  profile_picture_s3_url,
  block_timestamp
FROM `lens-public-data.polygon.public_profile`
WHERE handle = '{user_handle}'
"""

# Get the profile_id
profile_df = client.query(profile_query).to_dataframe()
profile_id = profile_df['profile_id'].iloc[0] if not profile_df.empty else None

if profile_id:
    sql_query = f"""
    SELECT
      post_id,
      profile_id,
      content
    FROM `lens-public-data.polygon.public_profile_post`
    WHERE content IS NOT NULL AND profile_id = '{profile_id}'
    ORDER BY block_timestamp DESC
    """

    with st.spinner("Loading data..."):
        df = client.query(sql_query).to_dataframe()

    st.set_option('deprecation.showPyplotGlobalUse',
                          False)

    background_color = st.radio("Choose background color:", ["black", "white"])

    content_str = process_content(df['content'])

    mask_image = Image.open("lens_logo_thick.png")

    with st.spinner("Generating word cloud..."):
        stopwords = set(STOPWORDS)
        mask = process_mask_image(mask_image)
        wordcloud = WordCloud(stopwords=stopwords, background_color=background_color, max_words=1000, mask=mask,
                              contour_width=1, contour_color='white', max_font_size=200).generate(content_str)

        with NamedTemporaryFile(suffix=".png") as temp_file:
            wordcloud.to_file(temp_file.name)
            temp_image = Image.open(temp_file.name)
            st.image(temp_image)

    # Calculate word frequencies and display them in a table
    words = [word.lower() for word in content_str.split() if word.lower() not in stopwords]  # Convert to lowercase
    word_freqs = Counter(words).most_common()
    word_freqs_df = pd.DataFrame(word_freqs, columns=["Word", "Frequency"])
    st.subheader("Word Frequencies")
    st.write(word_freqs_df)
else:
    st.warning("No data found for the given user handle.")                 
