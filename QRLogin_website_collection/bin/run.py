from src.extract_text_from_html import extraxt_text_from_html
from src.find_login_page import find_login_page
from src.search_keywords_in_file import search_keywords_in_file
from src.translate_non_english_text import translate_non_english_text_main

'''
   During the data collection phase, websites may come from various countries globally. 
   Due to network stability factors, it is advised to perform this stage multiple times to ensure convergence of data.
'''
find_login_page()

'''
   Extract relevant text from the collected data.
'''
extraxt_text_from_html()

'''
   Translate the extracted relevant text appropriately.
'''
translate_non_english_text_main()

'''
   Identify.
'''
search_keywords_in_file()

# if __name__ == '__main__':
#     print('Start QRLogin Websites Collection ')
