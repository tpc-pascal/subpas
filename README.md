# subpas
Lấy toàn bộ danh sách phát và kênh đăng ký để quản lý trực quan

<p align="center">
  <img src="assets/logo.svg" alt="subpas logo" width="400">
</p>

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tpc-pascal/subpas/blob/main/colab.ipynb)
[![Open in Hugging Face](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-md-dark.svg)](https://huggingface.co/spaces/tpc-pascal/subpas)

> Công cụ lấy danh sách YouTube subscriptions và playlists, phân loại bằng AI (Gemini), hiển thị qua giao diện Gradio.

**Lý do ra đời:** Bạn có quá nhiều kênh đăng ký trên YouTube và muốn dọn dẹp? Công cụ này giúp bạn xem tất cả subscriptions, playlists và video trong đó, được AI phân loại theo chủ đề, để dễ dàng quyết định unsubscribe hoặc xóa playlist.

---

## Tính năng

- Xác thực Google OAuth 2.0 (YouTube Data API v3) — an toàn, scope readonly
- Lấy **tất cả** subscriptions (tự động phân trang)
- Phân loại kênh theo chủ đề bằng **Google Gemini AI**: `Code`, `Entertainment`, `News`, `AI/ML`, `Education`, `Music`, `Game`, `Tech`, `Other`
- Lấy danh sách **playlists** và **video** trong từng playlist
- Giao diện web với Gradio (sort, filter, dark mode, xem thumbnail)
- Xuất danh sách subscriptions ra file ZIP (CSV)
- Chạy được trên: local, Hugging Face Spaces, Google Colab

---

## Cấu trúc thư mục

```
subpas/
├── hf/                          # Hugging Face Spaces deployment
│   ├── app.py                   # Entry point — Gradio UI
│   ├── requirements.txt         # Python dependencies
│   ├── packages.txt             # System packages (HF)
│   ├── core/
│   │   ├── youtube_api.py       # YouTube API wrapper (auth, fetch)
│   │   └── gemini_classify.py   # Gemini AI classifier
│   ├── utils/
│   │   └── file_manager.py      # Export ZIP/CSV
│   └── README.md                # HF Space metadata
├── colab.ipynb                  # Google Colab notebook
├── GUIDE.md                     # Hướng dẫn setup chi tiết
├── CONTRIBUTING.md              # Hướng dẫn đóng góp
├── CREDITS.md                   # Credits & tham khảo
└── LICENSE                      # MIT
```

---

## Tech Stack

| Layer | Công nghệ |
|---|---|
| Language | Python 3.10+ |
| Web UI | Gradio 6.13 |
| YouTube API | `google-api-python-client`, `google-auth-oauthlib` |
| AI Classification | `google-genai` (Gemini) |
| Data | pandas |
| CI/CD | GitHub Actions → Hugging Face Spaces |

---

## Tác giả

**tpc-pascal** — [GitHub](https://github.com/tpc-pascal)

---

## License

MIT — xem file [LICENSE](./LICENSE).
