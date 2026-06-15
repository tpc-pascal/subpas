import json
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import gradio as gr

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly", 
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def get_auth_url(json_file):
    if json_file is None:
        return "⚠️ Chưa đủ tệp cấu hình!", None, None, gr.update(visible=False)
    try:
        with open(json_file.name, 'r') as f:
            config = json.load(f)
        flow = InstalledAppFlow.from_client_config(config, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        url, _ = flow.authorization_url(prompt='consent')
        html = f'''<div style="padding:10px;border:1px solid #3b82f6;border-radius:8px;text-align:center">
                    <a href="{url}" target="_blank">
                        <button style="width:100%;background:#2563eb;color:white;padding:10px;border-radius:6px;font-weight:bold;cursor:pointer">🔗 Lấy mã Code</button>
                    </a>
                </div>'''
        return html, config, flow, gr.update(visible=True)
    except:
        return "❌ Lỗi file!", None, None, gr.update(visible=False)

def fetch_subscriptions(service, classifier_instance):
    raw_items = []
    next_token = None
    
    while True:
        res = service.subscriptions().list(
            part="snippet", 
            mine=True, 
            maxResults=50, 
            pageToken=next_token
        ).execute()
        
        raw_items.extend(res.get('items', []))
        next_token = res.get('nextPageToken')
        if not next_token: break

    channel_names = [item["snippet"]["title"] for item in raw_items]
    
    if classifier_instance and classifier_instance.client:
        all_tags = classifier_instance.classify_parallel(channel_names, batch_size=50)
    else:
        all_tags = ["---"] * len(channel_names)

    all_subs = []
    for idx, item in enumerate(raw_items):
        all_subs.append({
            "Tên Kênh": item["snippet"]["title"], 
            "Chủ đề": all_tags[idx] if idx < len(all_tags) else "Other",
            "Hình Ảnh": item["snippet"]["thumbnails"].get("high", {}).get("url"),
            "Ngày Đăng Ký": item["snippet"]["publishedAt"].split('T')[0],
            "Liên Kết": f"https://www.youtube.com/channel/{item['snippet']['resourceId']['channelId']}",
            "ID": item["id"]
        })
        
    return all_subs

def get_playlist_videos(playlist_id, creds):
    service = build("youtube", "v3", credentials=creds)
    videos = []
    next_token = None
    while True:
        res = service.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50, pageToken=next_token).execute()
        for item in res.get('items', []):
            videos.append({
                "Tên Video": item["snippet"]["title"],
                "Ngày Thêm": item["snippet"]["publishedAt"].split('T')[0],
                "Thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url"),
                "Link": f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
            })
        next_token = res.get('nextPageToken')
        if not next_token: break
    return videos