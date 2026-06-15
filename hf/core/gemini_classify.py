import time
from google import genai
from concurrent.futures import ThreadPoolExecutor

class GeminiClassifier:
    def __init__(self):
        self.client = None
        self.available_models = []
        self.current_model_index = 0

    def load_key(self, file_obj):
        if file_obj is None:
            self.client = None
            self.available_models = []
            return "ℹ️ Chế độ không phân loại (Optional)"
        try:
            with open(file_obj.name, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
            if not api_key:
                self.client = None
                return "❌ File trống!"
            
            self.client = genai.Client(api_key=api_key)
            raw_models = self.client.models.list()
            self.available_models = []
            
            for m in raw_models:
                name_lower = m.name.lower()
                if "gemini" in name_lower:
                    supported = getattr(m, 'supported_generation_methods', []) or getattr(m, 'supported_methods', [])
                    if "generateContent" in supported or any(x in name_lower for x in ["flash", "pro"]):
                        self.available_models.append(m.name.split('/')[-1])
            
            self.available_models.sort(key=lambda x: ("flash" not in x.lower(), x))
            self.current_model_index = 0
            
            if self.available_models:
                return f"✅ Đã nhận API Key."
            return "⚠️ Không tìm thấy model hỗ trợ!"
        except Exception as e:
            self.client = None
            return f"❌ Lỗi: {str(e)}"

    def classify_batch(self, channel_names):
        if not channel_names or self.client is None or not self.available_models:
            return ["---"] * len(channel_names)

        prompt = (
            f"Classify {len(channel_names)} YouTube channels into these categories only: "
            "Code, Entertainment, News, AI/ML, Education, Music, Game, Tech, Other. "
            "\nOutput: CSV format only, no explanation, no channel names.\n"
            "Channels: " + ", ".join(channel_names)
        )

        attempts = 0
        max_attempts = len(self.available_models)
        
        while attempts < max_attempts:
            target_model = self.available_models[self.current_model_index]
            try:
                # LOG 1: Xem model nào đang được gọi và lô kênh gửi đi
                print(f"\n[DEBUG] Gọi model: {target_model}")
                print(f"[DEBUG] Danh sách gửi đi ({len(channel_names)} kênh): {channel_names[:3]}...")

                response = self.client.models.generate_content(
                    model=target_model, 
                    contents=prompt,
                    config={
                        "temperature": 0.0,
                        "max_output_tokens": 800,
                    }
                )
                
                if not response or not response.text:
                    print("[DEBUG] AI trả về rỗng (None hoặc Empty Text)")
                    return ["Other"] * len(channel_names)
                
                raw_text = response.text.strip()
                
                # LOG 2: Xem NGUYÊN VĂN câu trả lời của AI
                print(f"[DEBUG] AI Phản hồi nguyên bản: '{raw_text}'")
                
                clean_text = raw_text.replace('`', '').replace('python', '').strip()
                
                import re
                tags = [t.strip() for t in re.split(r'[,\n;]', clean_text) if t.strip()]
                
                # LOG 3: Xem danh sách nhãn sau khi cắt
                print(f"[DEBUG] Danh sách nhãn đã tách ({len(tags)} nhãn): {tags}")
                
                if len(tags) != len(channel_names):
                    print(f"[DEBUG] LỆCH SỐ LƯỢNG: Kênh={len(channel_names)}, Nhãn={len(tags)}")
                    if len(tags) < len(channel_names):
                        tags.extend(["Other"] * (len(channel_names) - len(tags)))
                    else:
                        tags = tags[:len(channel_names)]
                        
                return tags
            
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"[DEBUG] LỖI 429: Hết hạn mức API tại {target_model}. Cần chờ thêm.")
                else:
                    print(f"[DEBUG] LỖI KHÁC tại {target_model}: {error_msg}")
                
                self.current_model_index = (self.current_model_index + 1) % len(self.available_models)
                attempts += 1
                time.sleep(2)
        
        return ["Other"] * len(channel_names)

    def classify_parallel(self, all_channel_names, batch_size=40):
        if not all_channel_names: return []
        
        batches = [all_channel_names[i:i + batch_size] for i in range(0, len(all_channel_names), batch_size)]
        
        print(f"\n[SYSTEM] Tổng: {len(all_channel_names)} kênh | {len(batches)} lô.")
        
        final_results = []
        for i, batch in enumerate(batches):
            print(f"[SYSTEM] Đang xử lý lô {i+1}/{len(batches)}...")
            res = self.classify_batch(batch)
            final_results.extend(res)
            
            if i < len(batches) - 1:
                print("[DEBUG] Nghỉ 6s để tránh Rate Limit...")
                time.sleep(6) 
                
        print("[SYSTEM] Hoàn tất phân loại.")
        return final_results