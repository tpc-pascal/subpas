## Hướng dẫn sử dụng

### Yêu cầu

- Python 3.10+
- Tài khoản Google (cho OAuth + YouTube Data API)
- (Tùy chọn) Gemini API Key để phân loại AI

### Chuẩn bị

#### 1. Gemini API Key (tùy chọn)

1. Truy cập [Google AI Studio](https://aistudio.google.com)
2. [Get API key](https://aistudio.google.com/api-keys) > Create API key > Name & Imported Project
3. Copy API Key vừa tạo vào một tệp `.txt`

#### 2. YouTube Data API v3 — OAuth 2.0 Client Secret (bắt buộc)

4. Truy cập [Google Cloud Console](https://console.cloud.google.com)
5. [Enabled APIs & services](https://console.cloud.google.com/apis/dashboard) > [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
6. [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) > Create branding > App information: Name > Audience: External > Save
7. Cập nhật Branding và bổ sung Audience: Test Users là email
8. [Clients](https://console.cloud.google.com/auth/clients/create) > OAuth 2.0 Client IDs > Create Client > Application type: Desktop app > Name > Create > Export JSON
9. Upload file TXT (Gemini key) và file JSON (OAuth client secret) vào ứng dụng

> 💢 Do at your own risk!

### Chạy local

```bash
git clone https://github.com/tpc-pascal/subpas.git
cd subpas/hf
pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại `http://localhost:7860`.

### Chạy trên Hugging Face Spaces

Truy cập: [huggingface.co/spaces/tpc-pascal/subpas](https://huggingface.co/spaces/tpc-pascal/subpas)

### Chạy trên Google Colab

Mở `colab.ipynb` và chạy lần lượt các cell.
