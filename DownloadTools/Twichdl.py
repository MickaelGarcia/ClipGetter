# -*- coding: utf-8 -*-
import os
import requests
import re
import urllib
import unicodedata
import logging
import time

ERRORED = []
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
CHUNK_SIZE = 1024
CONNECT_TIMEOUT = 5
RETRY_COUNT = 5
CLIP_PATTERNS = [r"^https:\/\/(clips|www).twitch.tv\/([0-z\-]+)$"]
"""Request form and usage:
query { 
  game(name: "Apex Legends") {
    name
    followersCount
    viewersCount
    clips(criteria: { period: LAST_MONTH }) {
      edges {
        node {
          id
          title
          viewCount
          createdAt
          durationSeconds
          curator {
            login
          }
          broadcaster {
            login
          }
        }
      }
    }
    videos(sort: VIEWS) {
      edges {
        node {
          id
          creator {
            login
          }
          title
          viewCount
          createdAt
          lengthSeconds
          broadcastType
        }
      }
    }
  }
}
"""

def download(video, name="", **kwargs):
    for pattern in CLIP_PATTERNS:
        match = re.match(pattern, video)

        if match:
            try:
                clip_slug = match.group('slug')
                clip = get_clip(clip_slug)
                cliper = clip["curator"]["displayName"]
                date = clip["createdAt"].replace("T","_").replace("Z", "").replace(":", "-")
                url = clip["videoQualities"][0]["sourceURL"]
                title = slugify(clip["title"])
                broadcaster = clip["broadcaster"]["displayName"]
                video_name = "{}_{}_{}.mp4".format(date, cliper, title)

                if name == "":
                    if not os.path.isdir(broadcaster):
                        os.mkdir(broadcaster)
                    path = "{}/{}".format(broadcaster, video_name)
                else:
                    if not os.path.isdir("{}/{}".format(name, broadcaster)):
                        os.mkdir("{}/{}".format(name, broadcaster))
                    path = "{}/{}/{}".format(name, broadcaster, video_name)
                return _download(url, path, **kwargs)
            except:
                ERRORED.append(video.split("/")[-1])
                logging.warning("Downlaod Error lsit : ")
                for x in ERRORED:
                    logging.warning("\t%s" %(x))

def _download(url, path):
    tmp_path = path + ".tmp"
    response = requests.get(url, stream=True, timeout=CONNECT_TIMEOUT)
    size = 0
    if not os.path.isfile(path):
        with open(tmp_path, 'wb') as target:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                target.write(chunk)
                size += len(chunk)
        os.rename(tmp_path, path)
    else: return("The file {} allrady existy ".format(path.split("/")[-1]))


def get_clip(slug):
    url = "https://gql.twitch.tv/gql"

    query = """
    {{
        clip(slug: "{}") {{
            title
            game {{
                name
            }}
            broadcaster {{
                displayName
            }}
            videoQualities {{
                sourceURL
            }}
            curator {{
                displayName
            }}
            createdAt
        }}  
    }}
    """
    
    response = gql_query(query.format(slug))
    return response["data"]["clip"]

def gql_query(query):
    url = "https://gql.twitch.tv/gql"
    payload = {"query": query}
    response = authenticated_post(url, json={"query": query}).json()
    
    return response

def authenticated_post(url, data=None, json=None, headers={}):
    headers['Client-ID'] = CLIENT_ID

    response = requests.post(url, data=data, json=json, headers=headers)
    if response.status_code == 400:
        data = response.json()
        raise "Error !"

    response.raise_for_status()

    return response

def download_file(url, path, retries=RETRY_COUNT):
    if os.path.exists(path):
        return os.path.getsize(path)

    for _ in range(retries):
        try:
            return _download(url, path)
        except: pass

def slugify(value):
    re_pattern = re.compile(r'[^\w\s-]', flags=re.U)
    re_spaces = re.compile(r'[-\s]+', flags=re.U)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re_pattern.sub('', value).strip().lower()
    return re_spaces.sub('-', value)


get_clip("BovineScrumptiousClipzOSfrog-UNRfvpldJ2xXtx3_")