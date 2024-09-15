import csv
import os
import random
import re
import time
import logging

import nest_asyncio
from fake_useragent import UserAgent
import asyncio
from typing import Union, List
from playwright.async_api import async_playwright, Page, ElementHandle
from bs4 import BeautifulSoup
from lxml import html
from concurrent.futures import ThreadPoolExecutor

from src.is_login_page import is_login_page
from common.utils import determine_full_url
from config import constants
from config.constants import LOGIN_IDENTITIES, HUMAN_VERIFICATION_KEYWORDS, HUMAN_VERIFICATION_HINTS
from config.params import WEBSITES_FILE_PATH, SAVE_FOLDER_PATH, LOGS_PATH, THREAD_COUNT, HTMLS_PATH

ua = UserAgent()
semaphore = asyncio.Semaphore(5)

os.makedirs(f"{HTMLS_PATH}", exist_ok=True)
os.makedirs(f"{SAVE_FOLDER_PATH}/screemshot", exist_ok=True)

logging.basicConfig(filename=f'{LOGS_PATH}/find_login_page.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def visit_and_save_login_page(index, domain, save_folder, context):
    logging.info(f"Visiting and saving login page for domain: {domain}")
    page = await context.new_page()
    try:
        url = determine_full_url(f'{domain}')
        if url is None:
            logging.error(f"Unable to access URL  {index}:{domain}")
            return
        await page.goto(url)
        await page.wait_for_load_state("load", timeout=30000)
        logging.info(f"{index}: Successful access to the {domain} page.")
        matched_elements = await find_elements_with_page(domain, page, LOGIN_IDENTITIES)
        login_element_found_flag = 0
        if matched_elements:
            for matched_element in matched_elements:
                await matched_element.dispatch_event('click')
                updated_page = await handle_page_changes(domain, page)
                new_page = await merge_iframe_content(domain, updated_page)
                new_page_content = await new_page.content()
                if is_login_page(await playwright_page_to_html_element(new_page)) \
                        or has_form_elements(domain, new_page_content):
                    await save_to_file(domain, f'{save_folder}/html', new_page_content)
                    await new_page.screenshot(path=f"{save_folder}/screemshot/{domain.replace('.', '_')}.png")
                    login_element_found_flag = 1
                    logging.info(f"{index}: Saved login page for {domain} successfully")
                    await new_page.close()
                    break
                await new_page.close()
        if login_element_found_flag == 0:
            await page.screenshot(path=f"{save_folder}/screemshot/{domain.replace('.', '_')}.png")
    except Exception as e:
        logging.error(f"Failed to visit and save login page for {domain} at index {index}: {e}")
    finally:
        if page:
            try:
                await page.close()
            except Exception as e:
                print(e)


async def handle_page_changes(domain, page):
    """
    Handle changes on the page such as new pages or popups.
    """
    try:
        updated_page = await asyncio.wait_for(
            asyncio.gather(
                page.context.wait_for_event('page'),
                page.wait_for_event('popup'),
                return_exceptions=True
            ),
            timeout=6  # 设置超时时间，单位为秒
        )
    except asyncio.TimeoutError:
        logging.error(f'Return the original page if timeout occurs {domain}:{page}')
        return page
    await updated_page[-1].wait_for_load_state("load", timeout=300000)
    return updated_page[-1]


async def merge_iframe_content(domain, page):
    """
        Merge content from iframes into the main page.

        Args:
            domain (str): The domain being processed.
            page: The Playwright Page object.

        Returns:
            Page: The page after merging iframe content.
        """
    # Get all <iframe> elements on the current page
    iframe_elements = await page.query_selector_all('iframe')
    for iframe_element in iframe_elements:
        # Get the content frame of the current <iframe> element
        frame_element = await iframe_element.content_frame()
        if frame_element:
            frame_content = await frame_element.content()
            # Use JavaScript to create a new container element in the page
            await page.evaluate('''
                (frameContent) => {
                    const containerElement = document.createElement("div");
                    containerElement.innerHTML = frameContent;
                    document.body.appendChild(containerElement);
                }
            ''', frame_content)
        else:
            logging.info(f"Unable to retrieve content frame of <iframe> in {domain}")
    return page


async def find_elements_with_page(domain: str, page: Page, target_texts: Union[str, List[str]]) -> list[ElementHandle]:
    """
        Find elements on the page matching the target texts.
        Returns:
            List[Page]: A list of matched Page elements.
    """
    if isinstance(target_texts, str):
        target_texts = [target_texts]

    matched_elements = []

    for target_text in target_texts:
        elements = await page.query_selector_all(f':text("{target_text}")')

        for element in elements:
            try:
                element_text = await element.inner_text()
                # Check if the element is attached to the DOM
                is_attached = await is_element_attached(element)
                if len(element_text) > 20:
                    continue
            except Exception as e:
                logging.error(f"Error getting element text of {domain}: {e}")
                continue
            if not is_attached:
                logging.info(f"Element not attached to the DOM of {domain}")
                continue
            try:
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
            except Exception as e:
                logging.error(f"Error checking visibility and enablement status of {domain}: {e}")
                continue
            if is_visible and is_enabled:
                matched_elements.append((element, element_text))
    # Sort elements based on the length of the element text
    matched_elements.sort(key=lambda x: len(x[1]))
    return [element[0] for element in matched_elements]


async def playwright_page_to_html_element(page):
    html_content = await page.evaluate('document.documentElement.outerHTML')
    html_element = html.fromstring(html_content)
    return html_element


async def is_element_attached(element):
    """
    Check if the element is attached to the DOM.

    Args:
        element: The element to check.

    Returns:
        bool: True if the element is attached, False otherwise.
    """
    try:
        is_attached = await element.evaluate('(element) => document.contains(element)', element)
    except Exception as e:
        # logging.error(f"Error checking if the element is attached to the DOM: {e}")
        return False
    return is_attached


def has_form_elements(domain, html_content):
    """
        Check if the HTML content contains Login form elements like form, input, textarea, or select tags.

        Args:
            domain (str): The domain being processed.
            html_content (str): The HTML content to check for form elements.

        Returns:
            bool: True if form elements are found, False otherwise.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    form_tags = soup.find_all('form')
    if form_tags:
        return True

    input_tags = soup.find_all('input')
    textarea_tags = soup.find_all('textarea')
    select_tags = soup.find_all('select')

    if input_tags or textarea_tags or select_tags:
        logging.info(f"{domain} - Login form elements found.")
        return True

    return False


async def save_to_file(site: str, save_path: str, content: str) -> None:
    """
    Save content to an HTML file in the specified down_folder_path.
    """
    filename = f"{site.replace('.', '_')}.html"
    try:
        filepath = os.path.join(save_path, filename)

        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(site + '\n')
                file.write(content)
            logging.info(f"Successfully saved {filename}.html file!")
        else:
            logging.info(f"File already exists: {filename}")
    except FileNotFoundError as e:
        error_msg = f"Failed to save {filename}. File path not found."
        logging.error(error_msg)
    except PermissionError as e:
        error_msg = f"Failed to save {filename}. Permission denied."
        logging.error(error_msg)
    except Exception as e:
        error_msg = f"Failed to save {filename}. An error occurred: {str(e)}"
        logging.error(error_msg)


async def process_csv_file(csv_file_path, save_folder):
    """
        Asynchronous function to read data from a CSV file, visit web pages, and save login pages.

        Args:
            csv_file_path (str): Path to the CSV file
            save_folder (str): Path to the folder to save files
        """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    async with semaphore:
        async with async_playwright() as playwright:
            try:
                browser = await playwright.chromium.launch(headless=False)
                context = await browser.new_context(ignore_https_errors=True)
                tasks = []
                batch_size = 10
                with open(csv_file_path, "r", encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    # next(csv_reader)
                    for row in csv_reader:
                        domain = row[1]
                        value = row[2]
                        if value != '1':
                            task = visit_and_save_login_page(row[0], domain, save_folder, context)
                            tasks.append(task)
                            if len(tasks) >= batch_size:
                                await asyncio.gather(*tasks)
                                tasks = []
                    if tasks:
                        await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"Encountered a problem while downloading {row[0]}:{domain}: {str(e)}")
            finally:
                if context:
                    try:
                        await context.close()
                    except Exception as e:
                        print(e)
                if browser:
                    try:
                        await browser.close()
                    except Exception as e:
                        print(e)


async def google_keyword_search(site, save_folder_path, browser):
    """
        Perform a Google keyword search for a specific site and process the results.

        Args:
            site (str): The site to search for.
            save_folder_path (str): The path to save any processed data.
            browser: The Playwright browser instance.
        """
    try:
        async with async_playwright() as p:
            context = await browser.new_context(user_agent=ua.random, ignore_https_errors=True)
            page = await context.new_page()
            cycle_index = 6
            while cycle_index > 0:
                cycle_index -= 1
                try:
                    random_domain = random.choice(constants.DOMAIN_LIST)
                    url = f'{random_domain}search?q=login+site:{site}'
                    await page.goto(url)
                    await page.wait_for_load_state('networkidle', timeout=4000)
                    page_source = await page.content()
                    if has_human_verification(page_source):
                        logging.info(f"Encountered human verification while scanning {site}!")
                        continue
                    link = await parse(site, page_source)
                    if link:
                        await process_link(site, save_folder_path, link, context)
                        cycle_index = 0
                except Exception as e:
                    logging.error(f"{e} : {site}")
    except Exception as e:
        logging.error(f"{e} : {site}")
    finally:
        if page:
            try:
                await page.close()
            except Exception as e:
                logging.error(e)
        if context:
            try:
                await context.close()
            except Exception as e:
                logging.error(e)


async def parse(site, page_source):
    """
        Extracts the link from the page source for a given site.
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    item = soup.find('div', attrs={'class': 'tF2Cxc'})
    link = ''
    if item is not None:
        try:
            link = item.find('a')['href']
        except Exception as e:
            logging.error(f"Error occurred while extracting link for site: {site}", e)
    logging.info(f"Site: {site}")
    logging.info(f"Link: {link}\n")
    return link


async def process_link(site, link, path, context):
    """
        Process the link associated with a site and save its content to a file.

        Args:
            site (str): The site being processed.
            save_folder_path (str): The path to save the content.
            link (str): The link to be processed.
            context: The Playwright browser context.

        Returns:
            None
        """
    async with async_playwright() as p:
        page = await context.new_page()
        loop_count = 4

        while loop_count > 0:
            try:
                await page.goto(link)
                # Wait for the page to load for a maximum of 10 seconds
                await page.wait_for_load_state('networkidle', timeout=10000)
                page_content = await page.content()

                if page_content:
                    await save_to_file(site, path, page_content)
                    break
                else:
                    loop_count -= 1
            except Exception as e:
                logging.error(f"Error processing link for site {site}: {e}")
            finally:
                loop_count -= 1
                try:
                    if page:
                        await page.close()
                except Exception as e:
                    logging.error(e)
        if loop_count == 0:
            logging.info(f"Network issues caused download failure for site: {site}, link: {link}")


def has_human_verification(page_source):
    """
        Check if the page source contains indications of human verification.

        Args:
            page_source (str): The source code of the web page.

        Returns:
            bool: True if human verification elements are found, False otherwise.
    """
    # 判断页面内容是否包含关键字
    if any(keyword in page_source for keyword in HUMAN_VERIFICATION_KEYWORDS):
        return True

    script_urls = re.findall(r'<script.*?src="(.*?)".*?>', page_source)
    for script_url in script_urls:
        if "recaptcha" in script_url:
            return True

    html_elements = re.findall(r'<[^>]*class="([^"]*g-recaptcha[^"]*)".*?>', page_source)
    for element in html_elements:
        if "g-recaptcha" in element:
            return True

    if any(hint in page_source for hint in HUMAN_VERIFICATION_HINTS):
        return True

    return False


def synchronization_down_html_data_source(csv_file, folder_path):
    """
        Synchronize downloaded HTML data with CSV data.

        Args:
            csv_file : Path to the CSV file.
            folder_path : Path to the folder containing HTML files.

    """
    # 读取CSV文件
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    filenames = []

    for filename in os.listdir(f'{folder_path}/html'):
        filename = filename.replace('_', '.').replace('.html', '')
        filenames.append(filename)

    for filename in os.listdir(f'{folder_path}/screemshot'):
        filename = filename.replace('_', '.').replace('.png', '')
        filenames.append(filename)

    for filename in filenames:
        for row in rows:
            if row[1] == filename:
                row[2] = '1'
                break

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def read_domains_from_csv(file_path):
    """
    Read and extract domains from a CSV file, ignoring empty domains and rows with a specific value.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of extracted domain names.
    """
    domains = []

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row

        for row in reader:
            domain = row[1].strip()
            if domain and row[2] != '1':
                domains.append(domain)

    return domains


async def main(workers):
    synchronization_down_html_data_source(WEBSITES_FILE_PATH, SAVE_FOLDER_PATH)
    await process_csv_file(WEBSITES_FILE_PATH, SAVE_FOLDER_PATH)

    # domains = read_domains_from_csv(csv_file_path)
    # with ThreadPoolExecutor(max_workers=workers) as executor:
    #     loop = asyncio.get_event_loop()
    #     tasks = []
    #     for domain in domains:
    #         task = loop.create_task(visit_and_save_login_page(domain, save_folder_path))
    #         tasks.append(task)
    #     await asyncio.wait(tasks)


def find_login_page():
    start = time.time()
    logging.info(f"Started at {start}, find_login_page")
    nest_asyncio.apply()
    asyncio.run(main(THREAD_COUNT), debug=True)
    elapsed_time = time.time() - start
    logging.info(f"Completed, total time taken: {elapsed_time} seconds")

# if __name__ == '__main__':
#     start = time.time()
#     logging.info(f"Started at {start}, find_login_page")
#     nest_asyncio.apply()
#     asyncio.run(main(THREAD_COUNT), debug=True)
#     end = time.time()
#     elapsed_time = end - start
#     logging.info(f"Completed, total time taken: {elapsed_time} seconds")
