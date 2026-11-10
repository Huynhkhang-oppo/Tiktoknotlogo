#!/usr/bin/env python3
"""
TikTok Downloader - tải video TikTok bằng yt-dlp.

Cài đặt:   pip install -U yt-dlp
Dùng GUI:  python tiktok_downloader.py
Dùng CLI:  python tiktok_downloader.py URL1 URL2 -o ./videos [--mp3]

Lưu ý: chỉ tải video của bạn hoặc video bạn được phép sử dụng.
"""
import argparse
import sys
import threading
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("Chưa cài yt-dlp. Chạy: pip install -U yt-dlp")


def build_opts(out_dir, audio_only=False):
    opts = {
        "outtmpl": str(Path(out_dir) / "%(uploader)s_%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 3,
    }
    if audio_only:
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })  # cần cài ffmpeg
    else:
        # Format "download" của TikTok thường dính watermark -> loại ra trước,
        # chỉ dùng lại nếu video không có lựa chọn nào khác.
        opts["format"] = (
            "best[format_id!=download][ext=mp4]/"
            "best[format_id!=download]/"
            "best"
        )
    return opts


def download(urls, out_dir, audio_only=False, log=print):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ok = 0
    with yt_dlp.YoutubeDL(build_opts(out_dir, audio_only)) as ydl:
        for url in urls:
            url = url.strip()
            if not url:
                continue
            try:
                log(f"⏳ Đang tải: {url}")
                info = ydl.extract_info(url, download=True)
                log(f"✅ Xong: {info.get('title') or info.get('id')}")
                ok += 1
            except Exception as e:
                log(f"❌ Lỗi: {url}\n   {str(e)[:200]}")
    log(f"--- Hoàn tất {ok} video. Thư mục: {Path(out_dir).resolve()}")


def run_gui():
    import tkinter as tk
    from tkinter import filedialog, scrolledtext

    root = tk.Tk()
    root.title("TikTok Downloader")
    root.geometry("620x520")

    tk.Label(root, text="Dán link TikTok (mỗi dòng một link):").pack(anchor="w", padx=10, pady=(10, 0))
    urls_box = scrolledtext.ScrolledText(root, height=8)
    urls_box.pack(fill="x", padx=10)

    row = tk.Frame(root)
    row.pack(fill="x", padx=10, pady=8)
    out_var = tk.StringVar(value=str(Path.home() / "Downloads" / "TikTok"))
    tk.Entry(row, textvariable=out_var).pack(side="left", fill="x", expand=True)
    tk.Button(row, text="Chọn thư mục",
              command=lambda: out_var.set(filedialog.askdirectory() or out_var.get())).pack(side="left", padx=5)

    mp3_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Chỉ tải âm thanh (MP3, cần ffmpeg)", variable=mp3_var).pack(anchor="w", padx=10)

    log_box = scrolledtext.ScrolledText(root, height=12, state="disabled")
    log_box.pack(fill="both", expand=True, padx=10, pady=8)

    def log(msg):
        def _w():
            log_box.config(state="normal")
            log_box.insert("end", msg + "\n")
            log_box.see("end")
            log_box.config(state="disabled")
        root.after(0, _w)

    def start():
        urls = urls_box.get("1.0", "end").splitlines()
        btn.config(state="disabled")

        def work():
            try:
                download(urls, out_var.get(), mp3_var.get(), log)
            finally:
                root.after(0, lambda: btn.config(state="normal"))

        threading.Thread(target=work, daemon=True).start()

    btn = tk.Button(root, text="Tải xuống", command=start, height=2)
    btn.pack(fill="x", padx=10, pady=(0, 10))
    root.mainloop()


def main():
    p = argparse.ArgumentParser(description="Tải video TikTok")
    p.add_argument("urls", nargs="*", help="Link video TikTok")
    p.add_argument("-o", "--out", default="downloads", help="Thư mục lưu")
    p.add_argument("--mp3", action="store_true", help="Chỉ tải âm thanh")
    args = p.parse_args()

    if not args.urls:
        run_gui()
    else:
        download(args.urls, args.out, args.mp3)


if __name__ == "__main__":
    main()
