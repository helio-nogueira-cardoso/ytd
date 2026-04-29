import os
import re
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tempfile import gettempdir

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    return name.strip()[:120] or 'video'


def format_duration(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return None
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def download_video(url, progress_hook=None):
    out_dir = gettempdir()
    outtmpl = os.path.join(out_dir, 'ytd_%(id)s.%(ext)s')
    ydl_opts = {
        'format': 'bv*+ba/b/bv*/ba',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'impersonate': ImpersonateTarget('chrome'),
    }
    if FFMPEG_PATH:
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH
    if progress_hook:
        ydl_opts['progress_hooks'] = [progress_hook]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
    if not os.path.exists(filepath):
        base, _ = os.path.splitext(filepath)
        for ext in ('.mp4', '.mkv', '.webm', '.m4a'):
            candidate = base + ext
            if os.path.exists(candidate):
                filepath = candidate
                break
    return filepath, info if isinstance(info, dict) else {}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('YouTube Downloader')
        self.geometry('560x300')
        self.minsize(560, 300)
        self.configure(padx=24, pady=20)

        self._tmp_filepath = None
        self._info = None

        title = tk.Label(self, text='YouTube Downloader', font=('Helvetica', 18, 'bold'))
        title.pack(anchor='w')

        sub = tk.Label(
            self,
            text='Cole uma URL do YouTube e baixe o melhor MP4 disponível.',
            fg='#666',
        )
        sub.pack(anchor='w', pady=(2, 16))

        row = tk.Frame(self)
        row.pack(fill='x')

        self._url_var = tk.StringVar()
        entry = tk.Entry(row, textvariable=self._url_var)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 8), ipady=6)
        entry.bind('<Return>', lambda _e: self._start_download())
        entry.focus_set()

        self._download_btn = tk.Button(row, text='Download', width=12, command=self._start_download)
        self._download_btn.pack(side='left')

        self._progress = ttk.Progressbar(self, mode='determinate', maximum=100)
        self._progress.pack(fill='x', pady=(16, 6))

        self._status_var = tk.StringVar(value='')
        self._status = tk.Label(self, textvariable=self._status_var, fg='#666', anchor='w', justify='left', wraplength=510)
        self._status.pack(fill='x')

        self._info_var = tk.StringVar(value='')
        self._info_label = tk.Label(self, textvariable=self._info_var, fg='#222', anchor='w', justify='left', wraplength=510)
        self._info_label.pack(fill='x', pady=(8, 0))

        self._save_btn = tk.Button(self, text='Salvar vídeo...', width=20, state='disabled', command=self._save_video)
        self._save_btn.pack(pady=(14, 0))

    def _set_status(self, text, color='#666'):
        self._status_var.set(text)
        self._status.config(fg=color)

    def _start_download(self):
        url = self._url_var.get().strip()
        if not url:
            self._set_status('Informe uma URL.', color='#a00')
            return
        self._tmp_filepath = None
        self._info = None
        self._info_var.set('')
        self._save_btn.config(state='disabled')
        self._download_btn.config(state='disabled')
        self._progress['value'] = 0
        self._set_status('Buscando vídeo...')
        threading.Thread(target=self._worker, args=(url,), daemon=True).start()

    def _worker(self, url):
        try:
            filepath, info = download_video(url, progress_hook=self._progress_hook)
        except Exception as e:
            self.after(0, self._on_error, e)
            return
        self.after(0, self._on_done, filepath, info)

    def _progress_hook(self, d):
        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            done = d.get('downloaded_bytes') or 0
            pct = (done / total * 100) if total else 0
            speed = d.get('speed') or 0
            speed_str = f'{speed / 1024 / 1024:.1f} MB/s' if speed else ''
            text = f'Baixando... {pct:.0f}%  {speed_str}'.strip()
            self.after(0, self._update_progress, pct, text)
        elif status == 'finished':
            self.after(0, self._update_progress, 100, 'Processando...')

    def _update_progress(self, pct, text):
        self._progress['value'] = pct
        self._set_status(text)

    def _on_error(self, e):
        self._download_btn.config(state='normal')
        self._progress['value'] = 0
        self._set_status(f'Falha: {e}', color='#a00')

    def _on_done(self, filepath, info):
        self._download_btn.config(state='normal')
        if not (filepath and os.path.exists(filepath)):
            self._set_status('O arquivo baixado não foi encontrado.', color='#a00')
            return
        self._tmp_filepath = filepath
        self._info = info
        title = info.get('title') or 'video'
        uploader = info.get('uploader') or info.get('channel') or ''
        duration = format_duration(info.get('duration')) or ''
        meta = ' · '.join(x for x in (uploader, duration) if x)
        self._info_var.set(f'{title}\n{meta}' if meta else title)
        self._set_status('Pronto. Clique em "Salvar vídeo" pra escolher o destino.', color='#070')
        self._save_btn.config(state='normal')

    def _save_video(self):
        if not self._tmp_filepath or not os.path.exists(self._tmp_filepath):
            self._set_status('O arquivo temporário não existe mais.', color='#a00')
            return
        title = (self._info or {}).get('title') or 'video'
        ext = os.path.splitext(self._tmp_filepath)[1] or '.mp4'
        suggested = sanitize_filename(title) + ext
        target = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=ext,
            initialfile=suggested,
            filetypes=[('MP4 video', '*.mp4'), ('All files', '*.*')],
        )
        if not target:
            return
        try:
            shutil.copyfile(self._tmp_filepath, target)
        except OSError as e:
            messagebox.showerror('Erro', f'Não foi possível salvar: {e}')
            return
        self._set_status(f'Salvo em {target}', color='#070')


def main():
    App().mainloop()


if __name__ == '__main__':
    main()
