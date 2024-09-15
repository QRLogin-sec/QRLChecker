import datetime
from http.cookies import SimpleCookie
import os
import re
from urllib.parse import urlparse, parse_qsl
import base64
import json
from urllib.parse import unquote
import chardet

import nltk
from nltk.corpus import words
import wordninja


def is_json(json_string):
    try:
        json.loads(json_string)
    except ValueError:
        return False
    return True


def parse_cookie(flow, flow_type):
    '''
    Parse cookie from flow
    '''
    if flow_type == "request":
        cookie_str = flow.request.headers.get('Cookie', '')
        if cookie_str == "":
            cookie_str = flow.request.headers.get('cookie', '')
    if flow_type == "response":
        cookie_str = flow.response.headers.get('Set-Cookie', '')
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    cookie_dict = {}
    for key, morsel in cookie.items():
        cookie_dict[key] = morsel.value
    return cookie_dict


def is_english_phrase(phrase):
    '''
    Check if a phrase is composed of English words
    '''
    if not nltk.data.find('corpora/words'):
        nltk.download('words')
    if not nltk.data.find('tokenizers/punkt'):
        nltk.download('punkt')

    words_set = set(words.words())
    split_phrase = wordninja.split(phrase)
    return all(word.lower() in words_set for word in split_phrase)


def flatten_nested_dict(nested_dict):
    """
    Flatten a nested dictionary
    """
    flattened_dict = {}
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            flattened_dict.update(flatten_nested_dict(value))
        else:
            flattened_dict[key] = value
    return flattened_dict


def remove_params_from_url(url):
    '''
    Remove parameters from URL
    '''
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path


def decode_content(content):
    if content is None:
        return ''
    encoding = chardet.detect(content)['encoding']
    if encoding is not None:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            pass
    encodings = ['utf-8', 'gbk', 'latin1', 'ascii'] 
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise ValueError('Unable to decode content' + str(content))


def parse_content(flow):    
    '''
    Parse content of request/response
    '''
    
    content_type = flow.headers.get('Content-Type', '')

    content = decode_content(flow.content)
    if not content:
        return dict()
    if 'application/x-www-form-urlencoded' in content_type:
        return dict(parse_qsl(content))
    
    elif 'application/json' in content_type and "({" not in content:        # smartedu.cn: content-type is json，but content is js
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"content": content}
        
    elif 'javascript' in content_type or "({" in content:
        if "({" in str(content):  
            content = remove_parenthesis(str(content))  
            try:
                return json.loads(content)   
            except json.JSONDecodeError:
                return {"content": content}
            
    else:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"content": content}
        

def remove_parenthesis(content):  
    result = re.search(r"\((.*?)\)", content, re.DOTALL)  
    if result:  
        return result.group(1)  
    else:
        return content
    

def search(flow, flow_type, keyword):
    '''
    Search keyword in flow (request/response)
        if found, return the parameter name/ "inBody"
    '''
    if flow_type == "request":
        for k, v in flow.request.query.items():
            if keyword == str(v):
                return k
        if keyword in str(flow.request.url):
            return "noName"
        
        if flow.request.content:
            content_dict = parse_content(flow.request)
            if isinstance(content_dict, dict):
                for k, v in content_dict.items():
                    if keyword in str(v):
                        return k
                    elif keyword in str(unquote(str(v))):
                        return k
                    
        for k, v in flow.request.headers.items():
            if k.lower() in ['cookie', 'set-cookie']:
                continue
            if keyword in str(v):
                return k
            
        cookie_dict = parse_cookie(flow, flow_type)
        for key, value in cookie_dict.items():
            if str(value) == str(keyword):
                return key

    if flow_type == "response":
        if flow.response.content:
            content_dict = parse_content(flow.response)

            if isinstance(content_dict, dict):
                flatten_dict = flatten_nested_dict(content_dict)
                for k, v in flatten_dict.items():
                    if keyword == str(v):
                        return k
                    elif keyword == str(unquote(str(v))):
                        return k
                for k, v in flatten_dict.items():
                    if keyword in str(v):
                        return k
                    elif keyword in str(unquote(str(v))):
                        return k
        
        for k, v in flow.response.headers.items():
            if keyword == str(v):
                return k
            
        for k, v in flow.response.headers.items():
            if keyword in str(v):
                cookie_dict = parse_cookie(flow, "response")
                for key, value in cookie_dict.items():
                    if keyword == str(value):
                        return key
                return k
    return ""

def is_timestamp(s):
        if s is None:
            return False
        try:
            pattern = r'\d{10,13}'  
            match = re.search(pattern, str(s))
            if match:
                match_t = match.group()  
                if len(str(match_t)) != 10 and len(str(match_t)) != 13:    
                    return False
                ts = int(str(match_t))
                if len(str(ts)) == 13:
                    ts = ts / 1000
                datetime.datetime.fromtimestamp(ts)
                return True
        except ValueError:
            return False
        

def is_login_done():
    if os.path.exists('./intermediate_files/done_flag.txt'):
        return True
    return False

