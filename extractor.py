import re
import validators
import requests
from bs4 import BeautifulSoup
import yt_dlp
import pandas as pd

# Function to extract URLs from the text file
def extract_urls(file_path):
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            found_urls = re.findall(r'(https?://\S+)', line)
            for url in found_urls:
                if validators.url(url):
                    urls.append(url)
    return urls


# Function to scrape SoundCloud metadata without using an API client
def fetch_soundcloud_metadata(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')

        # Scrape track title
        title = soup.find('meta', {'property': 'og:title'})['content'] if soup.find('meta', {'property': 'og:title'}) else 'Unknown'

        # Scrape uploader/artist
        uploader = soup.find('meta', {'property': 'og:description'})['content'] if soup.find('meta', {'property': 'og:description'}) else 'Unknown'

        # Scrape description
        description_tag = soup.find('meta', {'name': 'description'})
        description = description_tag['content'] if description_tag else 'No description available'

        return {
            'title': title,
            'uploader': uploader,
            'description': description
        }
    except Exception as e:
        print(f"Error fetching SoundCloud metadata: {e}")
        return {'title': 'Unknown', 'uploader': 'Unknown', 'description': 'Failed to retrieve metadata'}


# Function to fetch metadata for a YouTube video
def fetch_youtube_metadata(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'description': info.get('description', 'No description available'),
            }
    except yt_dlp.utils.ExtractorError as e:
        # Check if it's a private or unavailable video
        if 'Private video' in str(e) or 'sign in' in str(e):
            print(f"Skipping private or restricted video: {url}")
            return {
                'title': 'Private or Restricted Video',
                'uploader': 'Unknown',
                'description': 'This video is private or restricted'
            }
        else:
            print(f"Error fetching YouTube metadata: {e}")
            return {
                'title': 'Unknown',
                'uploader': 'Unknown',
                'description': 'Failed to retrieve metadata'
            }


# Function to scrape generic webpage metadata using BeautifulSoup
def fetch_generic_metadata(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        title = soup.title.string if soup.title else 'No Title'
        description_tag = soup.find('meta', {'name': 'description'})
        description = description_tag['content'] if description_tag else 'No description available'
        return {
            'title': title,
            'description': description
        }
    except Exception as e:
        return {'title': 'Unknown', 'description': 'Failed to retrieve metadata'}


# Function to get metadata and save to CSV
def save_metadata_to_csv(urls, output_csv):
    metadata_list = []
    
    for url in urls:
        if 'soundcloud.com' in url:
            metadata = fetch_soundcloud_metadata(url)  # Remove client_id here
        elif 'youtube.com' in url or 'youtu.be' in url:
            metadata = fetch_youtube_metadata(url)
        else:
            metadata = fetch_generic_metadata(url)
        
        metadata['url'] = url
        metadata_list.append(metadata)
    
    df = pd.DataFrame(metadata_list)
    df.to_csv(output_csv, index=False)
    print(f"Metadata saved to {output_csv}")
