#!/usr/bin/env python3
"""
scripts/fetch_live_to_repo.py

YouTube kanallarını kontrol eder; eğer canlı yayın varsa repo çalışma dizinine
media.xml (root: <mediaList>) dosyası olarak yazar.

Kullanım (Action içinden çalıştırılacak veya yerelde test etmek için):
- YOUTUBE_API_KEY ortam değişkeni olmalı (repo secret olarak eklenir)
- channels.txt aynı dizinde olmalı

Gereksinim:
pip install requests
"""
import os
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
API_KEY = os.environ.get("YOUTUBE_API_KEY") or ""

def call_api(path, params):
    params = params.copy()
    params['key'] = API_KEY
    url = f"{YOUTUBE_API_BASE}/{path}"
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def extract_from_url(line):
    line = line.strip()
    if not line:
        return None, None
    try:
        parsed = urlparse(line)
    except Exception:
        parsed = None
    if parsed and parsed.netloc and "youtube.com" in parsed.netloc:
        parts = parsed.path.split('/')
        if 'channel' in parts:
            idx = parts.index('channel')
            if idx + 1 < len(parts):
                return 'channelId', parts[idx + 1]
        if 'user' in parts:
            idx = parts.index('user')
            if idx + 1 < len(parts):
                return 'userName', parts[idx + 1]
        if 'c' in parts:
            idx = parts.index('c')
            if idx + 1 < len(parts):
                return 'custom', parts[idx + 1]
    if line.startswith('UC'):
        return 'channelId', line
    return 'unknown', line

def resolve_channel_id(token_type, token):
    try:
        if token_type == 'channelId':
            return token
        if token_type == 'userName':
            resp = call_api('channels', {'part': 'id', 'forUsername': token})
            items = resp.get('items') or []
            if items:
                return items[0]['id']
            return None
        if token_type in ('custom', 'unknown'):
            resp = call_api('search', {'part': 'snippet', 'q': token, 'type': 'channel', 'maxResults': 1})
            items = resp.get('items') or []
            if items:
                return items[0]['snippet']['channelId']
            return None
    except Exception as e:
        print("Hata (resolve):", e)
        return None

def find_live_videos_for_channel(channel_id):
    try:
        resp = call_api('search', {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'eventType': 'live',
            'maxResults': 5
        })
        items = resp.get('items') or []
        results = []
        for it in items:
            vid = it['id'].get('videoId')
            title = it['snippet'].get('title') or ''
            results.append({'videoId': vid, 'title': title})
            time.sleep(0.05)
        return results
    except Exception as e:
        print("Hata (find_live):", e)
        return []

def build_media_xml(entries):
    root = ET.Element('mediaList')
    for e in entries:
        for v in e.get('videos', []):
            m = ET.SubElement(root, 'media')
            ET.SubElement(m, 'title').text = v.get('title','')
            ET.SubElement(m, 'thumb').text = f"https://img.youtube.com/vi/{v.get('videoId','')}/0.jpg"
            ET.SubElement(m, 'type').text = "youtube"
            ET.SubElement(m, 'src').text = v.get('videoId','')
    # pretty-printing (basic)
    indent(root)
    return ET.tostring(root, encoding='utf-8', method='xml')

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def main():
    if not API_KEY:
        print("YOUTUBE_API_KEY ortam değişkeni bulunamadı. Çıkılıyor.")
        return 2

    if not os.path.exists('channels.txt'):
        print("channels.txt bulunamadı. Çıkılıyor.")
        return 3

    inputs = []
    with open('channels.txt', 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith('#'):
                inputs.append(ln)

    all_entries = []
    for line in inputs:
        token_type, token = extract_from_url(line)
        if token is None:
            continue
        channel_id = resolve_channel_id(token_type, token)
        if not channel_id:
            print(f"Channel ID bulunamadı: {line}")
            continue
        videos = find_live_videos_for_channel(channel_id)
        if videos:
            all_entries.append({'channelId': channel_id, 'requestedName': line, 'videos': videos})
        time.sleep(0.12)

    xml_bytes = build_media_xml(all_entries)
    outpath = 'media.xml'
    with open(outpath, 'wb') as out:
        out.write(xml_bytes)
    print(f"media.xml yazıldı: {outpath}")
    return 0

if __name__ == "__main__":
    exit(main())
