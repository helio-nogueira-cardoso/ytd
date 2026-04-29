import streamlit as st
import yt_dlp
import os
import re
import time
import traceback
from tempfile import gettempdir
from yt_dlp.networking.impersonate import ImpersonateTarget

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    return name.strip()[:120] or 'video'

def download_video(url):
    out_dir = gettempdir()
    outtmpl = os.path.join(out_dir, 'ytd_%(id)s.%(ext)s')
    base_opts = {
        'noplaylist': True,
        'impersonate': ImpersonateTarget('chrome'),
        'extractor_args': {'youtube': {'player_client': ['web', 'mweb', 'ios', 'tv_embedded']}},
    }
    ydl_opts = {
        **base_opts,
        'format': 'bv*+ba/b/bv*/ba',
        'outtmpl': outtmpl,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
    except yt_dlp.utils.DownloadError as e:
        with yt_dlp.YoutubeDL(base_opts) as probe:
            probe_info = probe.extract_info(url, download=False)
        fmts = [(f.get('format_id'), f.get('ext'), f.get('vcodec'), f.get('acodec'), f.get('format_note')) for f in (probe_info.get('formats') or [])]
        raise RuntimeError(f'{e}\n\nAvailable formats ({len(fmts)}): {fmts[:25]}') from e
    if not os.path.exists(filepath):
        base, _ = os.path.splitext(filepath)
        for ext in ('.mp4', '.mkv', '.webm', '.m4a'):
            candidate = base + ext
            if os.path.exists(candidate):
                filepath = candidate
                break
        else:
            video_id = info.get('id', '') if isinstance(info, dict) else ''
            matches = [f for f in os.listdir(out_dir) if video_id and video_id in f]
            raise RuntimeError(f'expected file not found at {filepath}; matching id in temp dir: {matches}')
    return filepath, info if isinstance(info, dict) else {}

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

def format_duration(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return None
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'

def main():
    st.set_page_config(
        page_title='YTD — YouTube Downloader',
        page_icon='▶️',
        layout='centered',
    )

    st.markdown(
        """
        <div style="text-align:center; padding: 0.5rem 0 1rem;">
            <div style="font-size:2.4rem; font-weight:700; letter-spacing:-0.02em;">
                ▶️ YouTube Downloader
            </div>
            <div style="color:#8a8f98; margin-top:0.25rem;">
                Paste a YouTube URL and grab the best available MP4.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    with st.form('download_form', clear_on_submit=False):
        url = st.text_input(
            'YouTube URL',
            placeholder='https://www.youtube.com/watch?v=...',
            label_visibility='collapsed',
        )
        submitted = st.form_submit_button('Download', use_container_width=True)

    if submitted:
        if not url.strip():
            st.warning('Please enter a YouTube URL.')
            return
        cleanup_old_files(gettempdir())
        try:
            with st.spinner('Fetching video...'):
                filepath, info = download_video(url.strip())
        except Exception as e:
            st.error(f'Download failed: [{type(e).__name__}] {repr(e) or "(no message)"}')
            st.code(traceback.format_exc(), language='text')
            return

        if not (filepath and os.path.exists(filepath)):
            st.error('Download failed. Check the URL and try again.')
            return

        title = info.get('title') or 'video'
        uploader = info.get('uploader') or info.get('channel')
        duration = format_duration(info.get('duration'))
        thumbnail = info.get('thumbnail')

        st.success('Ready! Click below to save the video.')

        with st.container(border=True):
            cols = st.columns([1, 2])
            with cols[0]:
                if thumbnail:
                    st.image(thumbnail, use_container_width=True)
            with cols[1]:
                st.markdown(f'**{title}**')
                meta = ' · '.join(x for x in (uploader, duration) if x)
                if meta:
                    st.caption(meta)

            filename = sanitize_filename(title) + os.path.splitext(filepath)[1]
            with open(filepath, 'rb') as file:
                st.download_button(
                    label='⬇️  Save video',
                    data=file,
                    file_name=filename,
                    mime='video/mp4',
                    use_container_width=True,
                )

    st.markdown(
        """
        <div style="text-align:center; color:#8a8f98; font-size:0.8rem; margin-top:2rem;">
            by Helio Nogueira Cardoso
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == '__main__':
    main()
