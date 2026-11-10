name: TikTok Downloader

on:
  workflow_dispatch:
    inputs:
      urls:
        description: "Link TikTok (cách nhau bằng dấu cách)"
        required: true
      mp3:
        description: "Chỉ tải MP3?"
        type: boolean
        default: false

jobs:
  download:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cài đặt
        run: |
          pip install -U yt-dlp
          sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Tải
        env:
          URLS: ${{ inputs.urls }}
          MP3: ${{ inputs.mp3 }}
        run: |
          read -ra LINKS <<< "$URLS"
          if [ "$MP3" = "true" ]; then
            python tiktok_downloader.py "${LINKS[@]}" -o downloads --mp3
          else
            python tiktok_downloader.py "${LINKS[@]}" -o downloads
          fi

      - name: Lưu kết quả
        uses: actions/upload-artifact@v4
        with:
          name: tiktok-files
          path: downloads/
