# Lens User Word Cloud Generator

This is a Python Streamlit application that generates a word cloud image for a specific user based on their posts on the Lens platform. It uses Google BigQuery to fetch the user's posts and visualizes the most frequently used words in their content.

The application is available here, but is down frequently due to the high number of requests: https://lens-wordcloud.streamlit.app/

Before you can run the application, you'll need to have a Google Cloud Platform (GCP) account with BigQuery API access.

## Setup

1. Clone the repository to your local machine:

```
git clone https://github.com/ries9112/lens_wordcloud.git
cd lens_wordcloud
```

2. Set up a virtual environment (optional):

```
python -m venv venv
source venv/bin/activate  # For Linux and macOS
.\venv\Scripts\activate   # For Windows
```

3. Install the required packages:

```
pip install -r requirements.txt
```

Create a Google Cloud Platform (GCP) service account and download the JSON key file. Save the file as gcp_service_account_key.json in the project directory. For more information on how to create a service account and download the key file, follow the instructions [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

4. Add the Google Cloud Platform (GCP) service account key to Streamlit secrets:

```
streamlit secrets add gcp_service_account gcp_service_account_key.json
```

Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your service account key file:

```
export GOOGLE_APPLICATION_CREDENTIALS=gcp_service_account_key.json  # For Linux and macOS
set GOOGLE_APPLICATION_CREDENTIALS=gcp_service_account_key.json     # For Windows
```

## Running the application

1. Start the Streamlit server:

```
streamlit run lens_user_word_cloud.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (e.g., http://localhost:8501).

3. Enter a user handle in the text input field and press Enter. The word cloud will be generated based on the user's posts on the Lens platform.

## Troubleshooting

If you encounter any issues while setting up or running the application, please refer to the [Streamlit documentation](https://docs.streamlit.io/) and the [Google Cloud Platform documentation](https://cloud.google.com/docs) for guidance.

You can also reach out to [Ricky on Lens at rickydata.lens](https://lenster.xyz/u/rickydata) and on [Twitter @Esclaponr](https://twitter.com/Esclaponr).
