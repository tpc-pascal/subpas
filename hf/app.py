import gradio as gr
import pandas as pd
from googleapiclient.discovery import build

from core.gemini_classify import GeminiClassifier
from core.youtube_api import get_auth_url, fetch_subscriptions, get_playlist_videos
from utils.file_manager import package_data

ai_handler = GeminiClassifier()

custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    block_radius="12px",
    button_large_radius="8px",
    button_small_radius="8px"
)

toggle_dark_js = "() => { document.querySelector('body').classList.toggle('dark'); }"
paste_js = """
async () => {
    try {
        const text = await navigator.clipboard.readText();
        return text;
    } catch (err) {
        alert("Trình duyệt từ chối quyền truy cập Clipboard hoặc bạn đang không dùng HTTPS.");
        return "";
    }
}
"""

css = """
.column-border { border-right: 1px solid #e2e8f0; padding-right: 25px; margin-right: 10px; }
h3 { border-left: 4px solid #3b82f6; padding-left: 12px; color: #2563eb !important; }
.dark .column-border { border-right: 1px solid #1e293b; }
.dark h3 { color: #60a5fa !important; }
.paste-container { border: 1px solid #cbd5e1 !important; border-radius: 10px !important; padding: 4px 10px !important; display: flex !important; align-items: center !important; }
.dark .paste-container { border-color: #334155 !important; background-color: #1e293b !important; }
.btn-inline-paste { border: none !important; background: #e2e8f0 !important; color: #2563eb !important; font-size: 12px !important; padding: 4px 12px !important; min-width: fit-content !important; border-radius: 8px !important; }
.dark .btn-inline-paste { background: #334155 !important; color: #60a5fa !important; }
@media (max-width: 768px) { .column-border { border-right: none; border-bottom: 2px solid #e2e8f0; padding-bottom: 25px; margin-bottom: 25px; } }
"""

def start_session_ui(auth_code, flow_state):
    if flow_state is None: 
        yield None, None, "⚠️ Lỗi cấu hình!", None, gr.update(visible=False), gr.update(visible=False)
        return

    try:
        yield None, None, "🔄 Đang xác thực tài khoản...", None, gr.update(value=20, visible=True), gr.update(visible=False)
        flow_state.fetch_token(code=auth_code)
        service = build("youtube", "v3", credentials=flow_state.credentials)
        
        yield None, None, "🤖 Đang thu thập và phân loại AI song song (vui lòng đợi)...", None, gr.update(value=50, visible=True), gr.update(visible=False)
        
        all_subs = fetch_subscriptions(service, ai_handler)
        
        yield None, None, "📂 Đang tải Playlists...", None, gr.update(value=80, visible=True), gr.update(visible=False)
        res_p = service.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50).execute()
        playlists = [{"Tên Playlist": i["snippet"]["title"], "Số Video": i["contentDetails"]["itemCount"], "ID Playlist": i["id"]} for i in res_p.get('items', [])]
        
        df = pd.DataFrame(all_subs)
        if not df.empty:
            df = df.sort_values(by=["Chủ đề", "Tên Kênh"]).reset_index(drop=True)
            df.insert(0, 'STT', range(1, len(df) + 1))
        
        yield df, flow_state.credentials, "✅ Hoàn tất!", pd.DataFrame(playlists), gr.update(value=100, visible=False), gr.update(visible=True)
    
    except Exception as e:
        yield None, None, f"❌ Lỗi: {str(e)}", None, gr.update(visible=False), gr.update(visible=False)

def on_table_select(evt: gr.SelectData, df):
    if df is None or evt.index[0] is None: return None, None
    row = df.iloc[evt.index[0]]
    return row['STT'], row['Hình Ảnh']

def on_playlist_select(evt: gr.SelectData, p_df, creds):
    if p_df is None or creds is None: return None, None
    playlist_id = p_df.iloc[evt.index[0]]["ID Playlist"]
    
    videos = get_playlist_videos(playlist_id, creds)
    df_v = pd.DataFrame(videos)
    
    if df_v.empty:
        return df_v, None
    display = df_v[["Tên Video", "Ngày Thêm", "Link"]].copy()
    display["Link"] = display["Link"].apply(
        lambda u: f'<a href="{u}" target="_blank">▶️ Xem Video</a>'
    )
    return df_v, display.values.tolist()

def on_video_select(evt: gr.SelectData, v_full_df):
    if v_full_df is None or evt.index[0] is None: return None
    return v_full_df.iloc[evt.index[0]]["Thumbnail"]

with gr.Blocks(theme=custom_theme, css=css) as demo:
    auth_flow_state = gr.State()
    user_creds = gr.State()
    current_df = gr.State()
    playlist_df = gr.State()
    v_full_df = gr.State()

    with gr.Row():
        gr.Markdown("# 📺 subpas")
        dark_btn = gr.Button("🌓", variant="secondary", scale=0)

    with gr.Row():
        with gr.Column(scale=1, elem_classes="column-border"):
            gr.Markdown("### 🔑 1. Gemini API")
            key_txt_file = gr.File(label="Upload API Key (.txt)", file_types=[".txt"])
            key_status = gr.Markdown("Chế độ không phân loại")

            gr.Markdown("### 🔑 2. YouTube API")
            file_input = gr.File(label="Upload Client Secret (.json)", file_types=[".json"])
            
            gr.Markdown("### 🔑 3. Xác thực")
            btn_gen_link = gr.Button("Tạo link xác thực Google")
            auth_link_html = gr.HTML("<i>Chờ file JSON...</i>")
            
            with gr.Group(visible=False) as paste_group:
                with gr.Row(elem_classes="paste-container"):
                    auth_code = gr.Textbox(show_label=False, placeholder="Dán mã tại đây...", container=False, scale=8, type="password")
                    btn_paste = gr.Button("📋 Dán", elem_classes="btn-inline-paste", scale=2)
            
            btn_login = gr.Button("🚀 Chạy Hệ Thống", variant="primary")
            progress_bar = gr.Slider(label="Tiến trình", minimum=0, maximum=100, value=0, interactive=False, visible=False)
            status = gr.Markdown("Trạng thái: Sẵn sàng")

        with gr.Column(scale=3, visible=False) as right_panel:
            with gr.Tabs():
                with gr.TabItem("👥 Subscriptions"):
                    table = gr.DataFrame(
                        interactive=False, wrap=True,
                        headers=["STT", "Tên Kênh", "Chủ đề", "Ngày Đăng Ký", "Liên Kết"],
                        datatype=["str", "str", "str", "str", "html"]
                    )
                    with gr.Row():
                        with gr.Column(scale=1):
                            target_stt = gr.Textbox(label="STT đang chọn", interactive=False)
                            btn_zip = gr.Button("📦 Xuất dữ liệu ZIP")
                            download_file = gr.File(label="Tải về file đã xuất")
                        avatar_display = gr.Image(label="Preview Kênh", height=250)

                with gr.TabItem("📂 Playlists"):
                    with gr.Row():
                        p_table = gr.DataFrame(label="Danh sách Playlists", scale=1, interactive=False)
                        with gr.Column(scale=2):
                            v_table = gr.DataFrame(
                        label="Video trong Playlist", interactive=False,
                        headers=["Tên Video", "Ngày Thêm", "Link"],
                        datatype=["str", "str", "html"]
                    )
                            v_preview = gr.Image(label="Preview Video", height=200)
    
    key_txt_file.change(ai_handler.load_key, inputs=[key_txt_file], outputs=[key_status])
    
    dark_btn.click(None, None, None, js=toggle_dark_js)
    btn_paste.click(None, None, auth_code, js=paste_js)
    
    btn_gen_link.click(
        get_auth_url, 
        inputs=[file_input], 
        outputs=[auth_link_html, gr.State(), auth_flow_state, paste_group]
    )
    
    btn_login.click(
        fn=start_session_ui, 
        inputs=[auth_code, auth_flow_state], 
        outputs=[current_df, user_creds, status, playlist_df, progress_bar, right_panel]
    ).then(
        fn=lambda full_df: (
            full_df[["STT", "Tên Kênh", "Chủ đề", "Ngày Đăng Ký", "Liên Kết"]]
            .assign(**{"Liên Kết": lambda x: x["Liên Kết"].apply(
                lambda u: f'<a href="{u}" target="_blank">🔗 YouTube</a>'
            )})
            .values.tolist()
        ) if full_df is not None else None, 
        inputs=[current_df], outputs=[table]
    ).then(
        fn=lambda d: (d[["Tên Playlist", "Số Video", "ID Playlist"]] if d is not None else None, gr.update(visible=True)), 
        inputs=[playlist_df], outputs=[p_table, right_panel]
    )

    table.select(on_table_select, [current_df], [target_stt, avatar_display])
    p_table.select(on_playlist_select, [playlist_df, user_creds], [v_full_df, v_table])
    v_table.select(on_video_select, [v_full_df], [v_preview])
    
    btn_zip.click(package_data, [current_df], [download_file])

if __name__ == "__main__":
    demo.launch(ssr_mode=False)