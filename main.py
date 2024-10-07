import csv
from extractor import extract_urls, fetch_soundcloud_metadata, fetch_youtube_metadata, fetch_generic_metadata

# File paths
file_path = '_chat.txt'
output_csv = 'metadata_output.csv'
checkpoint_file = 'processed_urls.txt'

# Function to load processed URLs from checkpoint file
def load_processed_urls(checkpoint_file):
    try:
        with open(checkpoint_file, 'r') as file:
            processed_urls = {line.strip() for line in file}
    except FileNotFoundError:
        processed_urls = set()  # Start fresh if no checkpoint exists
    return processed_urls

# Function to save a processed URL to the checkpoint file
def save_processed_url(checkpoint_file, url):
    with open(checkpoint_file, 'a') as file:
        file.write(f"{url}\n")

# Main function to process URLs and save metadata line by line
def process_urls(file_path, output_csv, checkpoint_file):
    # Load processed URLs from the checkpoint file
    processed_urls = load_processed_urls(checkpoint_file)

    # Open the output CSV in append mode
    with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'title', 'uploader', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file is empty (new CSV)
        if csvfile.tell() == 0:
            writer.writeheader()

        # Extract URLs from the text file
        urls = extract_urls(file_path)

        for url in urls:
            if url in processed_urls:
                print(f"Skipping already processed URL: {url}")
                continue

            try:
                # Fetch metadata based on the URL type
                if 'soundcloud.com' in url:
                    metadata = fetch_soundcloud_metadata(url)
                elif 'youtube.com' in url or 'youtu.be' in url:
                    metadata = fetch_youtube_metadata(url)
                else:
                    metadata = fetch_generic_metadata(url)

                # Add the URL to the metadata
                metadata['url'] = url

                # Write metadata to the CSV file line by line
                writer.writerow(metadata)
                print(f"Processed: {url}")

                # Save the URL to the checkpoint file
                save_processed_url(checkpoint_file, url)

            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue  # Move to the next URL even if an error occurs

# Run the process
process_urls(file_path, output_csv, checkpoint_file)
