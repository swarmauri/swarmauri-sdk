import requests
from urllib.parse import urljoin  # For handling relative URLs
from bs4 import BeautifulSoup
import wget
import os
from docx import Document

def get_docx_links(url, file_url, download_directory):
    # Send a GET request to the website
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all anchor tags in the HTML
        anchor_tags = soup.find_all('a')
        # Open the file to save .docx links
        with open('docx_links.txt', 'w') as file:
            os.chdir(download_directory)
            for tag in anchor_tags:
                href = tag.get('href', '')
                if href.endswith('.docx'):
                    # Convert relative URL to absolute URL and save it
                    absolute_url = urljoin(file_url, href)
                    
                    wget.download(absolute_url)
                    #file.write(absolute_url + '\n')
        print("Links saved to docx_links.txt")
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
        
        
def docx_to_txt(docx_path, txt_path):
    document = Document(docx_path)
    all_text = []

    # Start the recursive text extraction from the document body
    for element in document.element.body:
        all_text.extend(extract_text_recursive(element))

    # Save all extracted text to a txt file
    if all_text != None:
        print(all_text)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write('\n'.join([each for each in all_text if each]))
        
for each in os.listdir():
    docx_to_txt(each, each+'.txt')    

