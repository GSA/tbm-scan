#!/usr/bin/env python3
from collections import Counter
from contextlib import closing
from datetime import datetime, timedelta
import json
import logging
import os
import re
import shutil
import sys
import urllib.request
import warnings

from bs4 import BeautifulSoup
import requests

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
logger = logging.getLogger(__name__)

def make_outpath(target_dir):
    """Make a directory in the root of the project for the downloaded notices.
    
    Returns:
        out_path -- a str containing the absolute path to the created directory
    """
    out_path = os.path.join(os.getcwd(), target_dir) 
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    return out_path  

def clean_line_text(line_text):
    '''
    Given a line of text from an FBO FTP file, clean it up using bs4
    Parameters:
        line_text (str): a line of text from the ftp file
    Returns:
        text (str): the sanitized text
    '''
    url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    m = re.match(url_regex, line_text)
    if m:
        #bs4 raises warnings when you try to parse a url
        return line_text
    soup = BeautifulSoup(line_text,'html.parser')
    try:
        href = soup.find('a',href=True)['href']
    except TypeError:
        href = None
    #windows-1252 is more expansive than latin1
    soup_text = f'{href} {soup.text}' if href else soup.text
    text = soup_text.encode('windows-1252', errors = 'ignore').decode("utf8", errors='ignore')
    text = text.replace('Link To Document','').strip()
    
    return text

def get_email_from_url(url):
    '''
    Given the url to an fbo page, extract the contact email
    Parameters:
        url (str): the url to an fbo page
    Returns:
        hrefs (list): a list of all of the hrefs scraped from the page
    '''
    try:
        r = requests.get(url, timeout=20)
    except:
        return
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')
    hrefs = []
    for link in soup.findAll('a', attrs={'href': re.compile("^mailto")}):
        hrefs.append(link.get('href'))
    
    return hrefs

def extract_emails(notice):
    '''
    Given a contact field from a notice, extract the email addresses and first contact name.
    
    Parameters:
        notice (dict): a dict representing a single fbo notice from their FTP
        
    Returns:
        emails (list): a list of unique email addresses
    '''
    email_re = re.compile(r'^([0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*@([0-9a-zA-Z][-\w]*[0-9a-zA-Z]\.)+[a-zA-Z]{2,9})$')
    emails = []
    #search the contact field first
    contact = notice.get('CONTACT')
    if contact:
        tokens = contact.split()
        for token in tokens:
            m = re.search(email_re, token)
            if m:
                emails.append(m.group())
    #If there's no email address, the notice might have an email field, even though 
    #the FBO docs say this field isn't to be used.
    try:
        #pop since we don't need this key in each notice anymore.
        email = notice.pop('EMAIL')
    except KeyError:
        email = None
    if not emails and email:
        tokens = email.split()
        for token in tokens:
            m = re.search(email_re, token)
            if m:
                emails.append(m.group())
    #if there's still no email in the contact field, move onto all of the other fields
    if not emails:
        notice_values = " ".join(notice.values())
        tokens = notice_values.split()
        for token in tokens:
            m = re.search(email_re, token)
            if m:
                emails.append(m.group())
    #if there's still no email address, try web-scraping the notice's fbo page
    if not emails:
        url = notice.get('URL')
        hrefs = get_email_from_url(url)
        hrefs = [x.replace("mailto:",'') for x in hrefs]
        if hrefs:
            matches = [re.search(email_re, href.strip()) for href in hrefs]
            emails = [m.group() for m in matches if m is not None]
    emails = [email.lower() for email in set(emails)] if emails else None
    
    return emails

        
def id_and_count_notice_tags(file_lines):
    '''
    Static method to count the number of notice tags within an FBO export.
    Attributes:
        file_lines (list): A list of lines from the nightly FBO file.
    Returns:
        tag_count (dict): An instance of a collections.Counter object
                           containing tags as keys and their counts as
                           values
    '''
    end_tag = re.compile(r'\</[A-Z]*>')
    alphas_re = re.compile('[^a-zA-Z]')
    tags = []   # instantiate empty list
    for line in file_lines:
        try:
            match = end_tag.search(line)
            m = match.group()
            tags.append(m)
        except AttributeError:
            # these are all of the non record-type tags
            pass 
    clean_tags = [alphas_re.sub('', x) for x in tags]
    tag_count = Counter(clean_tags)

    return tag_count


def merge_dicts(dicts):
    '''
    Given a list of dictionaries, merge them into one dictionary, joining the str values
    where keys overlap.
    '''
    d = {}
    for dict in dicts:
        for key in dict:
            try:
                d[key].append(dict[key])
            except KeyError:
                d[key] = [dict[key]]
    return {k:" ".join(v) for k, v in d.items()}


def make_out_path(out_path):
    '''
    makes a directory in the current working directory if it doesn't already exist.
    '''
    if not os.path.exists(out_path):
        os.makedirs(out_path)


def download_from_ftp(date, fbo_ftp_url):
    '''
    Downloads a nightly FBO file, reads the lines, then removes file.
    Compare to read_from_ftp()
    
    Parameters:
        date (str): the date of the FTP file being downloaded
        fbo_ftp_url (str): the FBO FTP url
    Returns:
        file_lines (list): the lines of the nightly file
    '''
    file_name = f'fbo_nightly_{date}'
    out_path = os.path.join(os.getcwd(),"temp","nightly_files")
    make_out_path(out_path)
    try:
        with closing(urllib.request.urlopen(fbo_ftp_url, timeout=20)) as r:
            file_name = os.path.join(out_path,file_name)
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r, f)
    except Exception as err:
        logger.critical(f"Exception occurred trying to access {fbo_ftp_url}:  \
                          {err}", exc_info=True)
        return
    with open(file_name,'r', errors='ignore') as f:
        file_lines = f.readlines()
    os.remove(file_name)

    return file_lines


def pseudo_xml_to_json(file_lines):
    '''
    Open a nightly file and convert the pseudo-xml to a JSON compatible dictionary
    Arguments:
        file_name (str): the absolute path to the downloaded file
    Returns:
        merge_notices_dict (dict): a dictionary with keys for each notice type and arrays of notice
                                   dicts as values.
    '''
    html_tags = ['a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 
                 'bdi', 'bdo', 'bgsound', 'big', 'blink', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center',
                 'cite', 'code', 'col', 'colgroup', 'command', 'content', 'data', 'datalist', 'dd', 'del', 'details', 'dfn', 
                 'dialog', 'dir', 'div', 'dl', 'dt', 'element', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 
                 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 
                 'html', 'i', 'iframe', 'image', 'img', 'input', 'ins', 'isindex', 'kbd', 'keygen', 'label', 'legend', 'li', 
                 'link', 'listing', 'main', 'map', 'mark', 'marquee', 'math', 'menu', 'menuitem', 'meta', 'meter', 'multicol', 
                 'nav', 'nextid', 'nobr', 'noembed', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 
                 'p', 'param', 'picture', 'plaintext', 'pre', 'progress', 'q', 'rb', 'rbc', 'rp', 'rt', 'rtc', 'ruby', 's', 
                 'samp', 'script', 'section', 'select', 'shadow', 'slot', 'small', 'source', 'spacer', 'span', 'strike', 
                 'strong', 'style', 'sub', 'summary', 'sup', 'svg', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 
                 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr', 'xmp']
    html_tag_re = re.compile(r'|'.join('(?:</?{0}>)'.format(x) for x in html_tags), flags = re.I)
    alphas_re = re.compile('[^a-zA-Z]')
    notice_types = {'PRESOL','SRCSGT','SNOTE','SSALE','COMBINE','AMDCSS',
                    'MOD','AWARD','JA','FAIROPP','ARCHIVE','UNARCHIVE',
                    'ITB','FSTD','EPSUPLOAD','DELETE'}
    notice_type_start_tag_re = re.compile(r'|'.join('(?:<{0}>)'.\
                                          format(x) for x in notice_types))
    notice_type_end_tag_re = re.compile(r'|'.join('(?:</{0}>)'.\
                                        format(x) for x in notice_types))
    # returns two groups: the sub-tag as well as the text corresponding to it
    sub_tag_groups = re.compile(r'\<([A-Z]*)\>(.*)')
    notices_dict_incrementer = {k:0 for k in notice_types}
    tag_count = id_and_count_notice_tags(file_lines)
    matches_dict = {k:{k:[] for k in range(v)} for k,v in tag_count.items()}
    # Loop through each line searching for start-tags, then end-tags, then
    # sub-tags (after stripping html) and then ensuring that every line of
    # multi-line tag values is captured.
    last_clean_notice_start_tag = ''
    last_sub_tab = ''
    for line in file_lines:
        line = line.replace("<br />",' ')
        try:
            match = notice_type_start_tag_re.search(line)
            m = match.group()
            clean_notice_start_tag = alphas_re.sub('', m)
            last_clean_notice_start_tag = clean_notice_start_tag
        except AttributeError:
            try:
                match = notice_type_end_tag_re.search(line)
                m = match.group()
                notices_dict_incrementer[last_clean_notice_start_tag] += 1
                continue #continue since we found an ending notice tag
            except AttributeError:
                line_htmless = ' '.join(html_tag_re.sub(' ',
                                                        line.replace(u'\xa0', u' ')).split())
                try:
                    matches = sub_tag_groups.search(line_htmless)
                    groups  = matches.groups()
                    sub_tag = groups[0]
                    last_sub_tab = sub_tag
                    sub_tag_text = clean_line_text(groups[1])
                    current_tag_index = notices_dict_incrementer[last_clean_notice_start_tag]
                    matches_dict[last_clean_notice_start_tag][current_tag_index].append({sub_tag:sub_tag_text})
                except AttributeError:
                    record_index = 0
                    for i, record in enumerate(matches_dict[last_clean_notice_start_tag][current_tag_index]):
                        if last_sub_tab in record:
                            record_index = i
                    matches_dict[last_clean_notice_start_tag][current_tag_index][record_index][last_sub_tab] += " " + clean_line_text(line_htmless)
    notices_dict = {k:None for k in notice_types}
    for k in matches_dict:
        dict_list = [v for k,v in matches_dict[k].items()]
        notices_dict[k] = dict_list

    merge_notices_dict = {k:[] for k in notices_dict}
    for k in notices_dict:
        notices = notices_dict[k]
        if notices:
            for notice in notices:
                merged_dict = merge_dicts(notice)
                merge_notices_dict[k].append(merged_dict)
        else:
            pass
    merge_notices_dict

    return merge_notices_dict


def write_nightly_data(merge_notices_dict, date):
    '''
    Write a dict of notice data to json
    '''
    out_path = make_outpath('data')
    json_file = f"{date}-result.json"
    json_file = os.path.join(out_path, json_file)
    with open(json_file, 'w') as f:
        json.dump(merge_notices_dict, f)


def tbm_filter(merge_notices_dict):

    re_str = (
        r'(\btbm\b|'
        r'technology business management|'
        r'\btbma\b|'
        r'it spending transparency|'
        r'tbm framework|'
        r'it tower|'
        r'sub-towers)'
            )
    tbm_re = re.compile(re_str)
    tbm_notices = {k:[] for k in merge_notices_dict}
    for notice_type in merge_notices_dict:
        notices = merge_notices_dict[notice_type]
        for notice in notices:
            subject = notice.get('SUBJECT','')
            desc = notice.get('DESC','')
            notice_values = f'{subject} {desc}'.lower()
            is_tbm = tbm_re.search(notice_values)
            if is_tbm and 'tactical ballistic missile' not in notice_values:
                tbm_notices[notice_type].append(notice)
    
    return tbm_notices


def get_nightly_data(date = None, tbm_filtering = True):
    '''
    Exectutes methods in fbo_nightly_scraper module.
    Parameters:
        date (None or str): if a str, must be a date of th "%Y%m%d" format. If none, defaults to 
                            (datetime.now() - timedelta(2)).strftime("%Y%m%d")
        notice_types (list): notice types to scrape from fbo.
    Returns:
        nightly_data (list): list of dicts in JSON format.
    '''
    if not date:
        #get day before yesterday to give FBO time to update their FTP
        now_minus_two = datetime.utcnow() - timedelta(2)
        date = now_minus_two.strftime("%Y%m%d")
    fbo_ftp_url = f'ftp://ftp.fbo.gov/FBOFeed{date}'
    file_lines = download_from_ftp(date, fbo_ftp_url)
    if not file_lines:
        #exit program if download_from_ftp() failed (this is logged by the module)
        sys.exit(1)
    merge_notices_dict = pseudo_xml_to_json(file_lines)
    if tbm_filtering:
        tbm_notices = tbm_filter(merge_notices_dict)
        write_nightly_data(tbm_notices, date)
    else:
        write_nightly_data(merge_notices_dict, date)


if __name__ == '__main__':
    get_nightly_data()
    