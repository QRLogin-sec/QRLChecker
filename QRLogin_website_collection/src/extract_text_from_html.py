import os
import re
import logging
import time

from bs4 import BeautifulSoup

from common.utils import write_file_names_to_csv
from config.params import HTMLS_PATH, EXTRACT_TEXT_PATH, LOGS_PATH, SAVE_FOLDER_PATH, EXTRACT_TEXT_TRANSLATION_RECORD

logging.basicConfig(filename=f'{LOGS_PATH}/extraction.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def extract_text_from_html(directory):
    """
    Extract text content from HTML files in a given directory and save as text files.

    Args:
        directory (str): The directory containing HTML files to process.

    Returns:
        None
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_file = os.path.join(root, file)
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Remove content inside <script> tags
                    for script in soup.select('script'):
                        script.extract()

                    # Remove tags with style attribute 'display: none;'
                    all_tags = soup.find_all()
                    for tag in all_tags:
                        if tag.get('style') and 'display: none' in tag['style']:
                            tag.extract()

                    # Extract text content
                    text = soup.get_text(separator='\n')
                    file_name = os.path.splitext(file)[0]
                    output_file = os.path.join(EXTRACT_TEXT_PATH, f'{file_name}.txt')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    logging.info(f'Text extracted from file: {file}')
                except Exception as e:
                    logging.error(f'Error processing file: {file}. Exception: {str(e)}')
    logging.info(f'Text extraction completed. Output files are saved in {EXTRACT_TEXT_PATH}')


def filter_tags_with_style(soup, style_value):
    """
        Recursively filter tags in the BeautifulSoup soup object that contain a specific style value.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object to filter.
            style_value (str): The style value to filter for.

        Returns:
            None
        """
    if not soup:
        return

    for tag in soup.find_all():
        if tag.has_attr('style') and style_value in tag['style']:
            tag.decompose()
        else:
            filter_tags_with_style(tag, style_value)


def extract_text_from_html_regular(html_file):
    """
        Extract text content from an HTML file using regular expressions and save it as a text file.

        Args:
            html_file (str): The path to the HTML file to process.

        Returns:
            None
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Remove content inside <script> tags
        html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content,
                              flags=re.IGNORECASE)
        # Extract text content by removing HTML tags
        text = re.sub('<[^>]+>', '', html_content)
        text = re.sub(r' {2,}', ' ', text)

        # Get the file name
        file_name = os.path.basename(html_file)
        output_file = os.path.join(EXTRACT_TEXT_PATH, os.path.splitext(file_name)[0] + '.txt')

        # Save the extracted text to a text file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        logging.info(f'Text extracted from {html_file} and saved as {output_file}')
    except Exception as e:
        logging.error(f'Failed to extract text from {html_file}: {str(e)}')


def extraxt_text_from_html():
    start = time.time()
    logging.info(f"Started at {start}, extraxt_text_from_html")
    extract_text_from_html(HTMLS_PATH)
    write_file_names_to_csv(EXTRACT_TEXT_PATH, SAVE_FOLDER_PATH, EXTRACT_TEXT_TRANSLATION_RECORD)
    elapsed_time = time.time() - start
    logging.info(f"Completed, total time taken: {elapsed_time} seconds")


# if __name__ == '__main__':
#     extract_text_from_html(HTMLS_PATH)
#     write_file_names_to_csv(EXTRACT_TEXT_PATH, SAVE_FOLDER_PATH, EXTRACT_TEXT_TRANSLATION_RECORD)
