# === TikTok User Sentiment (non-headless, local) ===
# Jalankan di .ipynb atau .py
# pip install TikTokApi playwright transformers torch
# python -m playwright install --with-deps chromium

import asyncio, json, torch, torch.nn.functional as F
from TikTokApi import TikTokApi
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---------- KONFIG ----------
MS_TOKEN = "87qMUIL1k_yq-h-nGj9TLj3sTAxIYI7aGmvKc3W7qQeXk5Xbg3ymHyCvXk2sX9RluEFdm_6CeAw_LzD-2Vaw660vX5ou36XHNhJUMkA8RTTPtMy1m9Y3b7gVbyKeSuLzC1596yz4SLg1vue__eUBbXMexS1SfQ=="   # ambil dari cookie TikTok (Chrome > DevTools > Application > Cookies)
BROWSER = "chromium"
HEADLESS = False                         # <<< non-headless sesuai permintaan
MODEL_NAME = "w11wo/indonesian-roberta-base-sentiment-classifier"

# default bisnis proses
DEFAULT_MAX_VIDEOS = 5
DEFAULT_MAX_COMMENTS = 10
OUTPUT_PATH = "user_sentiment.json"      # file ringkas: username + sentiment_score
INCLUDE_DETAILS = False                  # set True kalau mau simpan detail per video & komentar ke file terpisah

# ---------- MODEL ----------
print("🔹 Memuat model sentimen...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
id2label = model.config.id2label

def analyze_sentiment_sync(text: str):
    if not text:
        return {"label": "UNKNOWN", "score": 0.0}
    inputs = tokenizer(text, truncation=True, padding=True, max_length=256, return_tensors="pt").to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze(0).cpu().tolist()
    idx = int(torch.tensor(probs).argmax().item())
    return {"label": id2label.get(idx, f"LABEL_{idx}"), "score": float(probs[idx])}

def extract_comment_text(obj):
    t = getattr(obj, "text", None)
    if t: return t
    if isinstance(obj, dict): return obj.get("text") or obj.get("desc") or json.dumps(obj, ensure_ascii=False)
    return str(obj)

# ---------- LOGIKA UTAMA ----------
async def analyze_user(username: str,
                       max_videos: int = DEFAULT_MAX_VIDEOS,
                       max_comments: int = DEFAULT_MAX_COMMENTS,
                       include_details: bool = INCLUDE_DETAILS):
    """
    Ambil <= max_videos terbaru dari @username,
    ambil <= max_comments per video,
    hitung sentiment_score = (pos - neg)/total * 100.
    Simpan ringkasan ke OUTPUT_PATH.
    Jika include_details=True, simpan detail ke username_details.json.
    """
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
    details = []  # per-video details (opsional)

    async with TikTokApi() as api:
        # Non-headless session agar stabil
        await api.create_sessions(
            ms_tokens=[MS_TOKEN],
            num_sessions=1,
            sleep_after=3,
            browser=BROWSER,
            headless=HEADLESS,
        )

        user = api.user(username=username)
        vid_count = 0
        async for video in user.videos(count=max_videos):
            vid_count += 1
            video_info = {"video_id": video.id, "comments": []}

            async for c in video.comments(count=max_comments):
                text = extract_comment_text(c)
                s = await asyncio.to_thread(analyze_sentiment_sync, text)

                # akumulasi
                sentiment_counts["total"] += 1
                lab = s["label"].lower()
                if lab == "positive":
                    sentiment_counts["positive"] += 1
                elif lab == "negative":
                    sentiment_counts["negative"] += 1
                else:
                    sentiment_counts["neutral"] += 1

                if include_details:
                    video_info["comments"].append({
                        "text": text,
                        "label": s["label"],
                        "score": round(s["score"], 4),
                    })

            if include_details:
                details.append(video_info)

            if vid_count >= max_videos:
                break

    pos, neg, net, total = sentiment_counts["positive"], sentiment_counts["negative"], sentiment_counts["neutral"], sentiment_counts["total"]
    sentiment_score = (pos - neg) / total * 100 if total > 0 else 0.0

    # ---- simpan ringkas (sesuai requirement) ----
    out_summary = {"username": username, "positive": pos, "neutral": net, "negative": neg, "total": total, "sentiment_score": round(sentiment_score, 2)}
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out_summary, f, ensure_ascii=False, indent=2)
    print(f"✅ Ringkasan disimpan: {OUTPUT_PATH} -> {out_summary}")

    # ---- simpan detail opsional ----
    if include_details:
        detail_path = f"{username}_details.json"
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump({
                "username": username,
                "positive": pos,
                "neutral": net,
                "negative": neg,
                "total": total,
                "sentiment_score": round(sentiment_score, 2),
                "videos": details
            }, f, ensure_ascii=False, indent=2)
        print(f"📝 Detail disimpan: {detail_path}")

    return out_summary

# ---------- CONTOH PEMAKAIAN ----------
if __name__ == "__main__":
    asyncio.run(analyze_user("fadiljaidi", max_videos=5, max_comments=10, include_details=True))