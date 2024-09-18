import os
import re
import logging
import csv
import time

from googletrans import Translator
from config.params import LOGS_PATH, EXTRACT_TEXT_PATH, TEXT_TRANSLATION_PATH, SAVE_FOLDER_PATH, \
    EXTRACT_TEXT_TRANSLATION_RECORD

logging.basicConfig(filename=f'{LOGS_PATH}/translation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def update_csv_status(csv_file, output_directory):
    """
        Update the status of translated files in a CSV file based on their presence in the output directory.

        Args:
            csv_file (str): Path to the CSV file to update.
            output_directory (str): Path to the output directory containing translated files.

        Returns:
            None
    """
    translated_rows = []  # Store translated row data
    temp_rows = []  # Store untranslated row data

    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # header = next(csv_reader)

        for row in csv_reader:
            filename = row[0]
            status = row[1]
            if status == '0' or status == '':
                txt_file = os.path.join(output_directory, f"{filename}_en.txt")
                if os.path.exists(txt_file):
                    row[1] = '1'  # Update status to translated (1)
                    translated_rows.append(row)
                else:
                    logging.error(f'File not found: {txt_file}')
                    temp_rows.append(row)
            else:
                translated_rows.append(row)

    # Combine untranslated rows with translated rows
    translated_rows += temp_rows

    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(translated_rows)


def translate_non_english_text(text, filename):
    """
        Translate non-English text in a given text using Google Translate.

        Args:
            text (str): The text to translate.
            filename (str): The filename associated with the text.

        Returns:
            str: The translated text if successful, otherwise the original text.
    """
    try:
        if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\u0400-\u04ff\u00c0-\u017f]+', text):
            translator = Translator()
            translation = None
            length_max = 4950

            if len(text) <= length_max:
                try:
                    translation = translator.translate(text, dest='en')
                except Exception as e:
                    logging.error(f"Failed to translate text {filename}: {e}")
                    return None
            else:
                text_slices = [text[i:i + length_max] for i in range(0, len(text), length_max)]
                translations = []

                for text_slice in text_slices:
                    try:
                        slice_translation = translator.translate(text_slice, dest='en')
                        translations.append(slice_translation.text)
                    except Exception as e:
                        logging.error(f"Failed to translate text {filename}: {e}"
                                      f"")
                        return None

                translated_text = ' '.join(translations)
                return translated_text

            if translation:
                translated_text = translation.text
                return translated_text
            else:
                return text
        else:
            return text
    except Exception as e:
        logging.error(f"Failed to translate text --> {filename}: {e}")
        return None


def translate_text_files(csv_file, directory):
    """
      Translate text files listed in a CSV file and save the translations.

      Args:
          csv_file (str): Path to the CSV file containing file names and statuses.
          directory (str): Path to the directory containing text files to translate.

      Returns:
          None
    """
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # next(csv_reader)  # Skip the header

        for row in csv_reader:
            filename, status = row

            if status == '0' or status == '':
                txt_file = os.path.join(directory, filename + '.txt')

                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        text = f.read()

                    translated_text = translate_non_english_text(text, filename)

                    if not translated_text:
                        continue

                    output_file = os.path.join(TEXT_TRANSLATION_PATH, f"{filename}_en.txt")

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(translated_text)

                    logging.info(f'Text translated from {txt_file} and saved as {output_file}')
                else:
                    logging.error(f'File not found: {txt_file}')


def translate_non_english_text_main():
    start = time.time()
    logging.info(f"Started at {start}, translate_non_english_text")
    csv_file = f'{SAVE_FOLDER_PATH}/{EXTRACT_TEXT_TRANSLATION_RECORD}'
    update_csv_status(csv_file, TEXT_TRANSLATION_PATH)
    translate_text_files(csv_file, EXTRACT_TEXT_PATH)
    end = time.time()
    elapsed_time = end - start
    logging.info(f"Completed, total time taken: {elapsed_time} seconds")

# if __name__ == '__main__':
#     start = time.time()
#     csv_file = f'{SAVE_FOLDER_PATH}/{EXTRACT_TEXT_TRANSLATION_RECORD}'
#     update_csv_status(csv_file, TEXT_TRANSLATION_PATH)
#     translate_text_files(csv_file, EXTRACT_TEXT_PATH)
#     end = time.time()
#     elapsed_time = end - start
#     logging.info(f"Done, total time elapsed: {elapsed_time} seconds")
