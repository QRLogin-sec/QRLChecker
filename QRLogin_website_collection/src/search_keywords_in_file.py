import os
import csv
import logging
import time

from config.constants import QR_KEYWORDS
from config.params import SAVE_FOLDER_PATH, LOGS_PATH, TEXT_TRANSLATION_PATH, QR_LOGIN_WEBSITES

logging.basicConfig(filename=f'{LOGS_PATH}/search.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def search_keywords_in_files(directory, keywords, output_path):
    """
        Search for keywords in text files within a directory and save matching filenames to an output CSV file.

        Args:
            directory (str): The directory path to search for text files.
            keywords (list): List of keywords to search for in the text files.
            output_path (str): Path to the output CSV file to store matching filenames.

        Returns:
            None
    """
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Name'])

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    txt_file = os.path.join(root, file)

                    with open(txt_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    filtered_lines = [line for line in lines if 'download' not in line.lower()]

                    if any(keyword.lower() in "".join(filtered_lines).lower() for keyword in keywords):
                        logging.info(f'Keyword found in file: {txt_file}')
                        modified_file_name = modify_filename(file)
                        writer.writerow([modified_file_name])

    logging.info(f'Search completed. Results are saved in {output_path}')


def modify_filename(filename):
    """
    Modify a filename by removing the extension, replacing underscores with dots, and handling '_en' suffix.

    Args:
        filename (str): The original filename to modify.

    Returns:
        str: The modified filename.
    """
    # Remove the file extension
    filename_without_extension = os.path.splitext(filename)[0]

    modified_filename = filename_without_extension.replace('_en', '').replace('_', '.')

    return modified_filename


def search_keywords_in_file():
    start = time.time()
    logging.info(f"Started at {start}, search_keywords_in_file")
    search_keywords_in_files(TEXT_TRANSLATION_PATH, QR_KEYWORDS, f'{SAVE_FOLDER_PATH}/{QR_LOGIN_WEBSITES}')
    end = time.time()
    elapsed_time = end - start
    logging.info(f"Completed, total time taken: {elapsed_time} seconds")

# if __name__ == '__main__':
#     search_keywords_in_files(TEXT_TRANSLATION_PATH, QR_KEYWORDS, f'{SAVE_FOLDER_PATH}/{QR_LOGIN_WEBSITES}')
