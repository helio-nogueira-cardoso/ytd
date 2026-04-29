import json
import locale
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = None


def config_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    elif sys.platform == 'darwin':
        base = os.path.expanduser('~/Library/Application Support')
    else:
        base = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
    return os.path.join(base, 'ytd')


CONFIG_FILE = os.path.join(config_dir(), 'config.json')


def load_config():
    try:
        with open(CONFIG_FILE, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


TRANSLATIONS = {
    'en': {
        'app_title': 'YouTube Downloader',
        'subtitle': 'Paste one URL or many (one per line) and grab the best MP4.',
        'tab_single': 'Single',
        'tab_batch': 'Batch',
        'batch_hint': 'One URL per line:',
        'btn_download': 'Download',
        'btn_download_all': 'Download all',
        'menu_settings': 'Settings',
        'menu_folder': 'Download folder...',
        'menu_language': 'Language',
        'menu_quit': 'Quit',
        'lang_en': 'English',
        'lang_pt_br': 'Português',
        'lang_pt_pt': 'Português (Portugal)',
        'init_title': 'First-time setup',
        'init_body': 'Before downloading the first video, choose the folder where files will be saved.\n\nYou can change this later in Settings → Download folder...',
        'dialog_folder': 'Choose download folder',
        'err_create_folder': 'Could not create folder:\n{e}',
        'err_dialog_title': 'Error',
        'err_no_url': 'Enter a URL.',
        'err_no_urls_batch': 'Paste at least one URL.',
        'err_no_folder': 'Configure the download folder first.',
        'folder_saving_to': 'Saving to: {path}',
        'folder_unconfigured': 'Download folder not configured.',
        'status_starting': 'Starting...',
        'status_fetching': 'Fetching video...',
        'status_downloading_n': 'Downloading {i}/{total}: {url}',
        'status_downloading_pct': 'Downloading... {pct}%  {speed}',
        'status_processing': 'Processing...',
        'status_saved': 'Saved: {name}',
        'status_failed': 'Failed: {err}',
        'status_no_file': 'Download finished but the file was not found.',
        'status_batch_done': '{ok} of {total} videos downloaded.',
        'failed_header': 'Failed:',
        'reason_no_file': 'file not found after download',
    },
    'pt-BR': {
        'app_title': 'YouTube Downloader',
        'subtitle': 'Cole uma URL ou várias (uma por linha) e baixe o melhor MP4.',
        'tab_single': 'Único',
        'tab_batch': 'Lote',
        'batch_hint': 'Uma URL por linha:',
        'btn_download': 'Download',
        'btn_download_all': 'Baixar todos',
        'menu_settings': 'Configurações',
        'menu_folder': 'Pasta de download...',
        'menu_language': 'Idioma',
        'menu_quit': 'Sair',
        'lang_en': 'English',
        'lang_pt_br': 'Português',
        'lang_pt_pt': 'Português (Portugal)',
        'init_title': 'Configuração inicial',
        'init_body': 'Antes de baixar o primeiro vídeo, escolha a pasta onde os arquivos serão salvos.\n\nVocê pode mudar isso depois em Configurações → Pasta de download...',
        'dialog_folder': 'Escolha a pasta de download',
        'err_create_folder': 'Não foi possível criar a pasta:\n{e}',
        'err_dialog_title': 'Erro',
        'err_no_url': 'Informe uma URL.',
        'err_no_urls_batch': 'Cole pelo menos uma URL.',
        'err_no_folder': 'Configure a pasta de download primeiro.',
        'folder_saving_to': 'Salvando em: {path}',
        'folder_unconfigured': 'Pasta de download não configurada.',
        'status_starting': 'Iniciando...',
        'status_fetching': 'Buscando vídeo...',
        'status_downloading_n': 'Baixando {i}/{total}: {url}',
        'status_downloading_pct': 'Baixando... {pct}%  {speed}',
        'status_processing': 'Processando...',
        'status_saved': 'Salvo: {name}',
        'status_failed': 'Falha: {err}',
        'status_no_file': 'O download terminou mas o arquivo não foi encontrado.',
        'status_batch_done': '{ok} de {total} vídeos baixados.',
        'failed_header': 'Falharam:',
        'reason_no_file': 'arquivo não encontrado após download',
    },
    'pt-PT': {
        'app_title': 'YouTube Downloader',
        'subtitle': 'Cole um URL ou vários (um por linha) e descarregue o melhor MP4.',
        'tab_single': 'Único',
        'tab_batch': 'Lote',
        'batch_hint': 'Um URL por linha:',
        'btn_download': 'Descarregar',
        'btn_download_all': 'Descarregar todos',
        'menu_settings': 'Definições',
        'menu_folder': 'Pasta de transferências...',
        'menu_language': 'Idioma',
        'menu_quit': 'Sair',
        'lang_en': 'English',
        'lang_pt_br': 'Português',
        'lang_pt_pt': 'Português (Portugal)',
        'init_title': 'Configuração inicial',
        'init_body': 'Antes de descarregar o primeiro vídeo, escolha a pasta onde os ficheiros serão guardados.\n\nPode alterar isto mais tarde em Definições → Pasta de transferências...',
        'dialog_folder': 'Escolha a pasta de transferências',
        'err_create_folder': 'Não foi possível criar a pasta:\n{e}',
        'err_dialog_title': 'Erro',
        'err_no_url': 'Indique um URL.',
        'err_no_urls_batch': 'Cole pelo menos um URL.',
        'err_no_folder': 'Configure primeiro a pasta de transferências.',
        'folder_saving_to': 'A guardar em: {path}',
        'folder_unconfigured': 'Pasta de transferências não configurada.',
        'status_starting': 'A iniciar...',
        'status_fetching': 'A obter vídeo...',
        'status_downloading_n': 'A descarregar {i}/{total}: {url}',
        'status_downloading_pct': 'A descarregar... {pct}%  {speed}',
        'status_processing': 'A processar...',
        'status_saved': 'Guardado: {name}',
        'status_failed': 'Falhou: {err}',
        'status_no_file': 'A transferência terminou mas o ficheiro não foi encontrado.',
        'status_batch_done': '{ok} de {total} vídeos descarregados.',
        'failed_header': 'Falharam:',
        'reason_no_file': 'ficheiro não encontrado após transferência',
    },
}


def detect_language():
    candidates = []
    try:
        candidates.append((locale.getlocale()[0] or '').replace('-', '_'))
    except Exception:
        pass
    candidates.append((os.environ.get('LANG', '') or '').split('.')[0].replace('-', '_'))
    candidates.append((os.environ.get('LC_ALL', '') or '').split('.')[0].replace('-', '_'))
    for c in candidates:
        cu = c.upper()
        if cu.startswith('PT_BR'):
            return 'pt-BR'
        if cu.startswith('PT_PT'):
            return 'pt-PT'
        if cu.startswith('PT'):
            return 'pt-BR'
    return 'en'


def format_duration(seconds):
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return None
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def truncate(text, n=60):
    return text if len(text) <= n else text[: n - 1] + '…'


def download_video(url, target_dir, progress_hook=None):
    outtmpl = os.path.join(target_dir, '%(title).120s [%(id)s].%(ext)s')
    ydl_opts = {
        'format': 'bv*[vcodec^=avc1]+ba[acodec^=mp4a]/b[ext=mp4]/bv*+ba/b',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'impersonate': ImpersonateTarget('chrome'),
        'restrictfilenames': True,
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
        self.geometry('600x460')
        self.minsize(600, 440)
        self.configure(padx=24, pady=20)

        self.config_data = load_config()
        self._language = self.config_data.get('language') or detect_language()
        if self._language not in TRANSLATIONS:
            self._language = 'en'
        self._language_var = tk.StringVar(value=self._language)

        self._build_widgets()
        self._build_menu()
        self._apply_language()

        self.after(150, self._ensure_download_dir)

    def t(self, key, **kwargs):
        translations = TRANSLATIONS.get(self._language, TRANSLATIONS['en'])
        text = translations.get(key) or TRANSLATIONS['en'].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _build_menu(self):
        menubar = tk.Menu(self)

        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label=self.t('menu_folder'), command=self._configure_download_dir)

        language = tk.Menu(settings, tearoff=0)
        language.add_radiobutton(label=self.t('lang_en'), value='en', variable=self._language_var, command=lambda: self._set_language('en'))
        language.add_radiobutton(label=self.t('lang_pt_br'), value='pt-BR', variable=self._language_var, command=lambda: self._set_language('pt-BR'))
        language.add_radiobutton(label=self.t('lang_pt_pt'), value='pt-PT', variable=self._language_var, command=lambda: self._set_language('pt-PT'))
        settings.add_cascade(label=self.t('menu_language'), menu=language)

        settings.add_separator()
        settings.add_command(label=self.t('menu_quit'), command=self.destroy)

        menubar.add_cascade(label=self.t('menu_settings'), menu=settings)
        self.config(menu=menubar)

    def _build_widgets(self):
        self._title_label = tk.Label(self, font=('Helvetica', 18, 'bold'))
        self._title_label.pack(anchor='w')

        self._sub_label = tk.Label(self, fg='#666')
        self._sub_label.pack(anchor='w', pady=(2, 12))

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill='x')

        self._buttons = []
        self._build_single_tab()
        self._build_batch_tab()

        self._progress = ttk.Progressbar(self, mode='determinate', maximum=100)
        self._progress.pack(fill='x', pady=(14, 6))

        self._status_var = tk.StringVar(value='')
        self._status = tk.Label(self, textvariable=self._status_var, fg='#666', anchor='w', justify='left', wraplength=550)
        self._status.pack(fill='x')

        self._info_var = tk.StringVar(value='')
        self._info_label = tk.Label(self, textvariable=self._info_var, fg='#222', anchor='w', justify='left', wraplength=550)
        self._info_label.pack(fill='x', pady=(6, 0))

        self._folder_var = tk.StringVar(value='')
        folder = tk.Label(self, textvariable=self._folder_var, fg='#888', anchor='w', justify='left', wraplength=550)
        folder.pack(fill='x', side='bottom', pady=(8, 0))

    def _build_single_tab(self):
        self._tab_single = ttk.Frame(self._notebook, padding=10)
        self._notebook.add(self._tab_single, text='')

        row = tk.Frame(self._tab_single)
        row.pack(fill='x')

        self._url_var = tk.StringVar()
        entry = tk.Entry(row, textvariable=self._url_var)
        entry.pack(side='left', fill='x', expand=True, padx=(0, 8), ipady=6)
        entry.bind('<Return>', lambda _e: self._start_single())
        entry.focus_set()

        self._btn_single = tk.Button(row, width=12, command=self._start_single)
        self._btn_single.pack(side='left')
        self._buttons.append(self._btn_single)

    def _build_batch_tab(self):
        self._tab_batch = ttk.Frame(self._notebook, padding=10)
        self._notebook.add(self._tab_batch, text='')

        self._batch_hint = tk.Label(self._tab_batch, fg='#666', anchor='w')
        self._batch_hint.pack(fill='x', pady=(0, 4))

        text_frame = tk.Frame(self._tab_batch)
        text_frame.pack(fill='both', expand=True)

        self._batch_text = tk.Text(text_frame, height=6, wrap='none', undo=True)
        scroll = ttk.Scrollbar(text_frame, orient='vertical', command=self._batch_text.yview)
        self._batch_text.configure(yscrollcommand=scroll.set)
        self._batch_text.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        self._btn_batch = tk.Button(self._tab_batch, width=14, command=self._start_batch)
        self._btn_batch.pack(pady=(8, 0), anchor='e')
        self._buttons.append(self._btn_batch)

    def _apply_language(self):
        self.title(self.t('app_title'))
        self._title_label.config(text=self.t('app_title'))
        self._sub_label.config(text=self.t('subtitle'))
        self._notebook.tab(self._tab_single, text=self.t('tab_single'))
        self._notebook.tab(self._tab_batch, text=self.t('tab_batch'))
        self._batch_hint.config(text=self.t('batch_hint'))
        self._btn_single.config(text=self.t('btn_download'))
        self._btn_batch.config(text=self.t('btn_download_all'))
        self._build_menu()
        self._update_folder_label()

    def _set_language(self, lang):
        if lang not in TRANSLATIONS:
            return
        self._language = lang
        self._language_var.set(lang)
        self.config_data['language'] = lang
        save_config(self.config_data)
        self._apply_language()

    def _set_status(self, text, color='#666'):
        self._status_var.set(text)
        self._status.config(fg=color)

    def _update_folder_label(self):
        path = self.config_data.get('download_dir')
        self._folder_var.set(self.t('folder_saving_to', path=path) if path else self.t('folder_unconfigured'))

    def _current_dir_valid(self):
        path = self.config_data.get('download_dir')
        return bool(path) and os.path.isdir(path)

    def _ensure_download_dir(self):
        if self._current_dir_valid():
            return
        messagebox.showinfo(self.t('init_title'), self.t('init_body'), parent=self)
        self._configure_download_dir()

    def _configure_download_dir(self):
        current = self.config_data.get('download_dir') or os.path.expanduser('~')
        chosen = filedialog.askdirectory(
            parent=self,
            initialdir=current,
            title=self.t('dialog_folder'),
            mustexist=False,
        )
        if not chosen:
            return
        try:
            os.makedirs(chosen, exist_ok=True)
        except OSError as e:
            messagebox.showerror(self.t('err_dialog_title'), self.t('err_create_folder', e=e), parent=self)
            return
        self.config_data['download_dir'] = chosen
        save_config(self.config_data)
        self._update_folder_label()

    def _start_single(self):
        url = self._url_var.get().strip()
        if not url:
            self._set_status(self.t('err_no_url'), color='#a00')
            return
        self._dispatch([url])

    def _start_batch(self):
        text = self._batch_text.get('1.0', 'end').strip()
        urls = [line.strip() for line in text.split('\n') if line.strip()]
        if not urls:
            self._set_status(self.t('err_no_urls_batch'), color='#a00')
            return
        self._dispatch(urls)

    def _dispatch(self, urls):
        if not self._current_dir_valid():
            self._set_status(self.t('err_no_folder'), color='#a00')
            self._ensure_download_dir()
            if not self._current_dir_valid():
                return
        target_dir = self.config_data['download_dir']
        self._info_var.set('')
        for b in self._buttons:
            b.config(state='disabled')
        self._progress['value'] = 0
        self._set_status(self.t('status_starting'))
        threading.Thread(target=self._worker, args=(urls, target_dir), daemon=True).start()

    def _worker(self, urls, target_dir):
        succeeded = []
        failed = []
        total = len(urls)
        for i, url in enumerate(urls, 1):
            if total > 1:
                self.after(0, self._update_progress, 0, self.t('status_downloading_n', i=i, total=total, url=truncate(url, 70)))
            else:
                self.after(0, self._update_progress, 0, self.t('status_fetching'))
            try:
                filepath, info = download_video(url, target_dir, progress_hook=self._progress_hook)
                if filepath and os.path.exists(filepath):
                    succeeded.append((url, filepath, info or {}))
                else:
                    failed.append((url, self.t('reason_no_file')))
            except Exception as e:
                failed.append((url, truncate(str(e), 200)))
        self.after(0, self._on_done, succeeded, failed, total)

    def _progress_hook(self, d):
        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            done = d.get('downloaded_bytes') or 0
            pct = (done / total * 100) if total else 0
            speed = d.get('speed') or 0
            speed_str = f'{speed / 1024 / 1024:.1f} MB/s' if speed else ''
            text = self.t('status_downloading_pct', pct=int(pct), speed=speed_str).strip()
            self.after(0, self._update_progress, pct, text)
        elif status == 'finished':
            self.after(0, self._update_progress, 100, self.t('status_processing'))

    def _update_progress(self, pct, text):
        self._progress['value'] = pct
        self._set_status(text)

    def _on_done(self, succeeded, failed, total):
        for b in self._buttons:
            b.config(state='normal')

        if total == 1:
            if succeeded:
                _url, filepath, info = succeeded[0]
                title = info.get('title') or 'video'
                uploader = info.get('uploader') or info.get('channel') or ''
                duration = format_duration(info.get('duration')) or ''
                meta = ' · '.join(x for x in (uploader, duration) if x)
                self._info_var.set(f'{title}\n{meta}' if meta else title)
                self._progress['value'] = 100
                self._set_status(self.t('status_saved', name=os.path.basename(filepath)), color='#070')
            else:
                _url, err = failed[0]
                self._info_var.set('')
                self._progress['value'] = 0
                self._set_status(self.t('status_failed', err=err), color='#a00')
            return

        n_ok = len(succeeded)
        if not failed:
            self._progress['value'] = 100
            self._info_var.set('')
            self._set_status(self.t('status_batch_done', ok=n_ok, total=total), color='#070')
            return

        color = '#a00' if n_ok == 0 else '#aa6600'
        self._progress['value'] = (n_ok / total) * 100
        self._set_status(self.t('status_batch_done', ok=n_ok, total=total), color=color)
        lines = [f'• {url}\n   ({err})' for url, err in failed]
        self._info_var.set(self.t('failed_header') + '\n' + '\n'.join(lines))


def main():
    App().mainloop()


if __name__ == '__main__':
    main()
