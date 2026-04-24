import streamlit as st
import yt_dlp
import os
import re
import time
from tempfile import gettempdir

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    return name.strip()[:120] or 'video'

def download_video(url):
    out_dir = gettempdir()
    outtmpl = os.path.join(out_dir, 'ytd_%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
    if not os.path.exists(filepath):
        base, _ = os.path.splitext(filepath)
        for ext in ('.mp4', '.mkv', '.webm'):
            candidate = base + ext
            if os.path.exists(candidate):
                filepath = candidate
                break
    title = info.get('title') if isinstance(info, dict) else None
    return filepath, title

def cleanup_old_files(directory, prefix='ytd_', age_limit_seconds=600):
    current_time = time.time()
    try:
        entries = os.listdir(directory)
    except OSError:
        return
    for filename in entries:
        if not filename.startswith(prefix):
            continue
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > age_limit_seconds:
                os.remove(file_path)
        except OSError:
            pass

def main():
    st.title('YouTube Video Downloader')
    st.text('by Helio Nogueira Cardoso')
    url = st.text_input('Enter YouTube URL')
    if st.button('Download'):
        if not url:
            st.warning('Please enter a YouTube URL.')
            return
        cleanup_old_files(gettempdir())
        try:
            with st.spinner('Downloading...'):
                filepath, title = download_video(url)
        except Exception as e:
            st.error(f'Download failed: {e}')
            return
        if filepath and os.path.exists(filepath):
            st.success('Download successful! Click below to save the video to your device.')
            filename = sanitize_filename(title or 'video') + os.path.splitext(filepath)[1]
            with open(filepath, 'rb') as file:
                st.download_button(
                    label='Download Video',
                    data=file,
                    file_name=filename,
                    mime='video/mp4',
                )
        else:
            st.error('Download failed. Check the URL and try again.')

if __name__ == '__main__':
    main()
