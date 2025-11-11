# -*- coding: utf-8 -*-
"""
TikTok Sentiment Analyzer (Non-Headless, Lokal)
-----------------------------------------------
1. Membuka browser Chromium dengan Playwright (non-headless)
2. Mengambil komentar dari video TikTok
3. Menganalisis sentimen komentar menggunakan model Hugging Face
4. Menyimpan hasil ke file JSON
"""

import asyncio
import json
import torch
import torch.nn.functional as F
from TikTokApi import TikTokApi
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============ KONFIGURASI ============

# Ganti dengan token valid (ambil dari cookie TikTok di browser biasa)
ms_token = "6PZAmMO_JBFAth5sGjw1zCViKC4OnCTo5P1Dr7Wv1DXgJFTfVLELba_G0UMHL7sG4q7fTg1j7Yd0Wx8XSpir9tbKGHkq19DiEzenydWD74R8gy79mCgOzvgbpOINCXD_NFy4oeTuZ6VGNvU3YOkxWHjBXFx8Fw=="

browser = "chromium"
headless = False  # Non-headless agar TikTok tidak mendeteksi bot
video_url = "https://www.tiktok.com/@fadiljaidi/video/7551714049612958987"

MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"
OUTPUT_FILE = "sentiment_result.json"

# ====================================

# Load model Hugging Face (cached di ~/.cache/huggingface)
print("🔹 Memuat model sentimen...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
id2label = model.config.id2label


def analyze_sentiment_sync(text: str):
    """Analisis sentimen sinkron (dipanggil lewat asyncio.to_thread)."""
    if not text:
        return {"label": "UNKNOWN", "score": 0.0}

    inputs = tokenizer(
        text, truncation=True, padding=True, max_length=256, return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze(0).cpu().tolist()

    idx = int(torch.tensor(probs).argmax().item())
    return {"label": id2label.get(idx, f"LABEL_{idx}"), "score": float(probs[idx])}


def extract_comment_text(comment_obj):
    """Mengambil teks dari objek komentar (obj/dict)."""
    text = getattr(comment_obj, "text", None)
    if text:
        return text
    if isinstance(comment_obj, dict):
        return comment_obj.get("text") or comment_obj.get("desc") or json.dumps(comment_obj)
    return str(comment_obj)


async def analyze_video_comments(url: str, max_comments=50):
    """Ambil komentar video dan analisis sentimennya."""
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
    comments_data = []

    async with TikTokApi() as api:
        print("🧠 Membuka browser TikTok...")
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=browser,
            headless=headless,
        )

        video = api.video(url=url)
        async for comment in video.comments(count=max_comments):
            text = extract_comment_text(comment)
            sentiment = await asyncio.to_thread(analyze_sentiment_sync, text)

            comments_data.append(
                {
                    "text": text,
                    "label": sentiment["label"],
                    "score": round(sentiment["score"], 4),
                }
            )

            sentiment_counts["total"] += 1
            if sentiment["label"].lower() == "positive":
                sentiment_counts["positive"] += 1
            elif sentiment["label"].lower() == "negative":
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1

    # Hitung skor sentimen total
    pos, neg, total = sentiment_counts["positive"], sentiment_counts["negative"], sentiment_counts["total"]
    ss = (pos - neg) / total * 100 if total > 0 else 0

    print("\n========== SUMMARY ==========")
    print(f"Positive: {pos}")
    print(f"Negative: {neg}")
    print(f"Neutral : {sentiment_counts['neutral']}")
    print(f"Total   : {total}")
    print(f"Sentiment Score (SS): {ss:.2f}%")
    print("=============================\n")

    result = {
        "video_url": url,
        "summary": sentiment_counts,
        "sentiment_score": ss,
        "comments": comments_data,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ Hasil disimpan ke {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(analyze_video_comments(video_url, max_comments=20))
