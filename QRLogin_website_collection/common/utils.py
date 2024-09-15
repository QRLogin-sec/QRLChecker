import requests
import os
import logging
import json
import csv


def determine_full_url(domain: str) -> str | None:
    """
    Determines the full URL with correct protocol (HTTP or HTTPS) for a domain by attempting to access it.

    Args:
        domain (str): The domain name without the protocol (http:// or https://).

    Returns:
        str | None: The full URL with the correct protocol if successful, None otherwise.
    """
    protocols = ['https://', 'http://']

    for protocol in protocols:
        full_url = protocol + domain
        try:
            response = requests.head(full_url, timeout=10)
            if response.ok:
                return full_url
        except requests.exceptions.RequestException:
            continue

    return None


def write_file_names_to_csv(in_path, out_directory, cvs_name):
    """
    Write the filenames of text files in a directory to a CSV file.

    Args:
        in_path (str): Path to the input directory containing text files.
        out_directory (str): Path to the output directory to save the CSV file.
        cvs_name: cvs name

    Returns:
        None
    """
    try:
        # Get all file names in the folder
        file_names = [os.path.splitext(file)[0] for file in os.listdir(in_path) if file.endswith(".txt")]
        csv_file_path = os.path.join(out_directory, cvs_name)

        with open(csv_file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Extract File Name", "Status"])  # Write the header row in the CSV file

            for file_name in file_names:
                writer.writerow([file_name, "0"])  # Write each file name and status to the CSV

        logging.info(f"File names have been written to {csv_file_path}")

    except Exception as e:
        logging.error(f"Error occurred while recording the names of extracted text files: {str(e)}")


def save_file(file_content, save_path):
    """
    Saves different types of files (HTML, CSV, log, JSON, etc.) to a specified path.

    Args:
        file_content (str or list or dict): The content to be saved in the file.
        save_path (str): The path where the file will be saved.

    Raises:
        ValueError: If the file type is not supported.

    Returns:
        None
    """
    try:
        filename = os.path.basename(save_path)
        file_extension = os.path.splitext(filename)[1].lower()
        file_type_handlers = {
            '.html': lambda content: open(save_path, 'w', encoding='utf-8').write(content),
            '.csv': lambda content: csv.writer(open(save_path, 'w', newline='')).writerows(content),
            '.log': lambda content: logging.basicConfig(filename=save_path, level=logging.INFO) or logging.info(
                content),
            '.json': lambda content: json.dump(content, open(save_path, 'w'), indent=4)
        }
        handler = file_type_handlers.get(file_extension)
        if handler:
            handler(file_content)
            logging.info(f"{filename} saved successfully at {save_path}")
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        error_msg = f"Failed to save {filename} at {save_path}: {str(e)}"
        logging.error(error_msg)


if __name__ == '__main__':
    file_content = {'key': 'value'}
    save_path = '../data/logs/output.json'
    save_file(file_content, save_path)
