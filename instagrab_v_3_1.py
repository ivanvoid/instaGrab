#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 21:48:39 2019

@author: veax-void
"""
import requests, re, json
import urllib.request
import time
import os

# Variables
page_prefex = 'https://www.instagram.com/p/'
teg_prefex = 'https://www.instagram.com/explore/tags/'

data_expr = r"(?<=<script type=\"text/javascript\">window\._sharedData = )(.*)(?=;</script>)"
video_expr = r'<meta property="og:video" content="(.*)" />'

lastpage = 10 # How many pages you want to download?

top_save_dir = 'top_posts/'
jst_save_dir = 'posts/'

top_loaded = False # you wanto to download top posts?
# Links

tags = [ 'ahegao',
         'nekogirl',
         'catgirl',
         'schoolgirl',
         'cosplaygirl',
         'hentaygirls',
         'redlingerie',
         'senpai']


link = teg_prefex + tags[5] + '/'

#==============================================================================
# Functions
def initRequest(req):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req.headers = hdr
    
def getMedia(j):
    return j['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']

def getTopMedia(j):
    return j['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges']

def resp2json(resp):
    data = re.search(r'window._sharedData = (\{.+?});</script>', resp.text).group(1)        
    return json.loads(data)

def graphSidecarLoader(media_info):
    page_img_url = page_prefex + media_info['node']['shortcode']
                
    page = requests.get(page_img_url)

    page_text = re.search(r'window._sharedData = (\{.+?});</script>', page.text).group(1)

    page_j = json.loads(page_text)
    
    content_list = page_j['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']

    for content_info in content_list:
        if not content_info['node']['is_video']:
            # IMG
            img_id  = content_info['node']['id']
            img_url = content_info['node']['display_url']
            img_name = content_info['node']['shortcode']+'_'+img_id
            
            print('Graph Sidecar Image:\t',content_info['node']['shortcode'])

            urllib.request.urlretrieve(img_url, str(img_name)+".jpg")
        else:
            # VIDEO
            video_id        = content_info['node']['id']
            video_name = content_info['node']['shortcode']+'_'+video_id
            code            = content_info['node']['shortcode'] 
            page_vidio_url  = page_prefex + code
            
            print('Graph Sidecar Video:\t',content_info['node']['shortcode'])
            
#            r1 = s.get(page_vidio_url)
            
#            video_url = re.search(video_expr, r1.text).group(1)
            
            video_url = content_info['node']['video_url']

            urllib.request.urlretrieve(video_url, str(video_name)+".mp4")
        time.sleep(2)
    
#############
# Main part #
#############

with requests.session() as s:
    initRequest(s)
    
    end_cursor = ''
    
    for count in range(1, lastpage):
        
        resp = s.get(link, params={'max_id': end_cursor})
        
        j = resp2json(resp)       
        
        end_cursor = re.search(r'"end_cursor":"([^"]+)"', resp.text).group(1)
    
        topmedia = getTopMedia(j)
        topmediaSize = len(topmedia)
        
        media = getMedia(j)
        mediaSize = len(media)
        
        # Load  Top media
        if top_loaded:
            if not os.path.exists(top_save_dir):
                os.makedirs(top_save_dir)
            os.chdir(top_save_dir)
            
            for topmedia_info in topmedia:
                if topmedia_info['node']['__typename'] == 'GraphSidecar':
                    print('TOP')
                    graphSidecarLoader(topmedia_info)
                elif  topmedia_info['node']['__typename'] == 'GraphImage':
                    img_id  = topmedia_info['node']['id']
                    img_url = topmedia_info['node']['display_url']
                    img_name = topmedia_info['node']['shortcode']+'_'+img_id
                    
                    print('Top Image:\t', topmedia_info['node']['shortcode'])
                    
                    urllib.request.urlretrieve(img_url, str(img_name)+".jpg")
                elif  topmedia_info['node']['__typename'] == 'GraphVideo':
                    video_id  = topmedia_info['node']['id']
                    shortcode = topmedia_info['node']['shortcode'] 
                    video_name = shortcode+'_'+video_id
                    
                    print('Top Video:\t',shortcode)
                    
                    r2 = s.get(page_prefex + shortcode)
                    video_url = re.search(video_expr, r2.text).group(1)
                    
                    urllib.request.urlretrieve(video_url, str(video_name)+".mp4")
                else:
                    print('Type error')
                    
            os.chdir('..')
            top_loaded = 1
        
        # Load just media
        if not os.path.exists(jst_save_dir):
            os.makedirs(jst_save_dir)
        os.chdir(jst_save_dir)
        
        for media_info in media:
            if media_info['node']['__typename'] == 'GraphSidecar':
                graphSidecarLoader(media_info)
            elif  media_info['node']['__typename'] == 'GraphImage':
                img_id  = media_info['node']['id']
                img_url = media_info['node']['display_url']
                img_name = media_info['node']['shortcode']+'_'+img_id
                
                print('Image:\t', media_info['node']['shortcode'])
                
                urllib.request.urlretrieve(img_url, str(img_name)+".jpg")
            elif  media_info['node']['__typename'] == 'GraphVideo':
                video_id  = media_info['node']['id']
                shortcode = media_info['node']['shortcode']
                video_name = media_info['node']['shortcode']+'_'+img_id
                
                print('Video:\t',shortcode)
                
                r2 = s.get(page_prefex + shortcode)
                video_url = re.search(video_expr, r2.text).group(1)
                
                urllib.request.urlretrieve(video_url, str(video_name)+".mp4")
            else:
                print('Type error')
    
        os.chdir('..')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

