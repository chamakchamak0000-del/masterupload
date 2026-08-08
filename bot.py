
from keep_alive import keep_alive
keep_alive()
from scrap import Scraper as _HAZScraper
_haz_scraper = _HAZScraper()

# ==========================================
# 🎌 ANIME AUTO DOWNLOADER v12.0 - MULTI-USER SAFE
# By Senpai - Production Ready
# ==========================================
import os
import json
import time
import asyncio
import aiohttp
import subprocess
import urllib.parse
import os, time, glob, asyncio, base64, re, requests, uuid, sys
import subprocess, json, pickle, psutil, shutil
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import nest_asyncio
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, MessageNotModified
from datetime import datetime, timedelta
from collections import deque
import warnings
import traceback

warnings.filterwarnings("ignore")
nest_asyncio.apply()

# ✅ FIX: Cache bot username
BOT_USERNAME = None

# ==========================================
# CONFIG
# ==========================================

# ==========================================
# 🔐 BOT CREDENTIALS
# ==========================================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_ID"])

# ==========================================
# 📁 DIRECTORY PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
THUMB_DIR = os.path.join(BASE_DIR, "thumbnails")
DB_DIR = os.path.join(BASE_DIR, "database")
WORKER_DIR = os.path.join(BASE_DIR, "workers")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

DB_FILE = os.path.join(DB_DIR, "main_db.pkl")

# ==========================================
# 🔢 LIMITS & WORKERS
# ==========================================
MAX_BATCH = 15                      # Max episodes per batch download
MAX_QUEUE = 100                     # Max tasks in queue
MIN_INTERVAL = 2                    # Min monitor check interval (minutes)
MAX_INTERVAL = 60                   # Max monitor check interval (minutes)

MAX_DOWNLOAD_WORKERS = 50           # Parallel download workers
MAX_UPLOAD_PARALLEL = 51           # Parallel upload slots
MAX_BATCH_WORKERS = 25               # Batch processing workers
TOTAL_WORKERS = MAX_DOWNLOAD_WORKERS + 1

MAX_FILE_SIZE = 1.9 * 1024 * 1024 * 1024    # 1.9GB - Telegram limit
MAX_ZIP_SIZE = 1.9 * 1024 * 1024 * 1024     # 1.9GB - Backup ZIP limit

# ==========================================
# ⏱️ TIMING SETTINGS
# ==========================================
COOLDOWN_TIME = 25                  # Seconds - User request cooldown
PROGRESS_UPDATE_INTERVAL = 5        # Seconds - Progress update frequency
FILE_CLEANUP_TIME = 50              # Seconds - Delete files after upload
THUMB_INACTIVE_DAYS = 30            # Days - Auto delete unused thumbnails
WORKER_STUCK_TIME = 9000            # Seconds - Kill stuck workers (2.5 hours)

# ==========================================
# 📦 BACKUP SETTINGS
# ==========================================
BACKUP_CHANNEL = -1002932260531
# 7:00 AM IST = 1:30 AM UTC | 7:00 PM IST = 1:30 PM UTC
BACKUP_TIMES = [
    {'hour': 1, 'minute': 30},    # 7:00 AM India Time
    {'hour': 13, 'minute': 30},   # 7:00 PM India Time
]

# ==========================================
# 🌐 SUPPORTED WEBSITES CONFIGURATION
# ==========================================
SUPPORTED_WEBSITES = {
    'toono': {
        'patterns': ['toono.in', 'toono.app', 'toono.me'],
        'name': '🎌 Toono',
        'type': 'codedew',
        'has_series': True,
        'has_episode': True
    },
    'rareanimes': {
        'patterns': ['rareanimes.app', 'raretoonsindia.me', 'raretoonsindia.in', 'raretoonsindia.com'],
        'name': '🎭 RareAnimes',
        'type': 'rareanimes',  # Different from toono
        'has_series': False,   # Direct episode page
        'has_episode': True
    },
    'animedubhindi': {
        'patterns': ['animedubhindi.me', 'animedubhindi.in', 'animedubhindi.link', 'animedubhindi.com', 'links.animedubhindi'],
        'name': '🎬 AnimeDubHindi', 
        'type': 'gdflix',
        'has_series': True,
        'has_episode': True
    },
    'gdflix': {
        'patterns': ['gdflix.io', 'gdflix.dev', 'gdflix.app', 'gdflix.lol', 'new3.gdflix', 'new2.gdflix', 'new.gdflix'],
        'name': '📦 GDFlix',
        'type': 'gdflix_direct',
        'has_series': False,
        'has_episode': False
    },
    'swift': {
        'patterns': ['swift.multiquality', 'multiquality.click', 'liptron'],
        'name': '⚡ Swift Player',
        'type': 'swift_direct',
        'has_series': False,
        'has_episode': False
    },
    'codedew': {
        'patterns': ['codedew.com'],
        'name': '🔗 Codedew',
        'type': 'codedew_direct',
        'has_series': False,
        'has_episode': False
    },
    'hindianimezone': {
        'patterns': ['hindianimezone.com', 'hindianimezone.in', 'hindianimezone.net',
                     'hindianimezone.org', 'hindianimezone.xyz', 'hindianimezone.me'],
        'name': '🇮🇳 HindiAnimeZone',
        'type': 'haz',
        'has_series': True,
        'has_episode': True
    },
    'toonworld4all': {
        'patterns': ['toonworld4all.me', 'toonworld4all.com', 'toonworld4all.in',
                     'archive.toonworld4all', 'toonworld4all'],
        'name': '🌏 ToonWorld4All',
        'type': 'toonworld4all',
        'has_series': True,
        'has_episode': True
    }
}

# Monitor delay after new episode detection (in seconds)
MONITOR_NEW_EP_DELAY = 420  # 7 minutes = 420 seconds

# GDFlix Specific Patterns (domain-agnostic — works with .dev, .app, .io, future domains)
GDFLIX_INTERMEDIATE_PATTERNS = [
    r"gdflix\.[a-z]+/zfile",        # any gdflix TLD zfile
    r"gdflix\.io/zfile",            # explicit .io
    r"instant\.busycdn\.xyz",
    r"busycdn\.xyz",
    r"fastcdn-dl\.pages\.dev",
]

GDFLIX_FINAL_PATTERNS = [
    r"aws-eu\.online",
    r"awscdn\.rest",
    r"video-downloads\.googleusercontent\.com",
    r"googleusercontent\.com/download",
    r"\.workers\.dev/[a-f0-9]{40,}",   # Cloudflare Workers (relaxed length)
    r"\.workers\.dev\?url=",
    r"pub-[a-f0-9]+\.r2\.dev",
    r"r2\.cloudflarestorage\.com",
    r"dl\.gdflix\.",                    # direct dl subdomain
]

def detect_website(url):
    """Detect website by NAME (domain-independent) with fuzzy matching"""
    from difflib import SequenceMatcher
    
    url_lower = url.lower()
    
    # Extract domain name (ignore TLD)
    # Example: toono.in, toono.app, toono.com -> "toono"
    try:
        # Remove protocol
        clean_url = url_lower.replace('http://', '').replace('https://', '')
        # Get domain part (before first /)
        domain_part = clean_url.split('/')[0]
        # Remove www.
        domain_part = domain_part.replace('www.', '')
        # Get base name (before first dot)
        base_name = domain_part.split('.')[0]
    except:
        base_name = url_lower
    
    # Try exact pattern match first (old method)
    for site_key, site_data in SUPPORTED_WEBSITES.items():
        for pattern in site_data['patterns']:
            # Remove TLD from pattern too
            pattern_base = pattern.split('.')[0]
            
            # Check if pattern matches
            if pattern in url_lower:
                return site_key, site_data
            
            # ✅ NEW: Check base name match (domain-independent)
            if pattern_base in base_name or base_name in pattern_base:
                return site_key, site_data
    
    # ✅ NEW: Fuzzy matching (70% similarity)
    best_match = None
    best_score = 0.0
    
    for site_key, site_data in SUPPORTED_WEBSITES.items():
        for pattern in site_data['patterns']:
            pattern_base = pattern.split('.')[0]
            
            # Calculate similarity
            similarity = SequenceMatcher(None, base_name, pattern_base).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = (site_key, site_data)
    
    # If 70% or more match, return it
    if best_score >= 0.70:
        print(f"   🔍 Fuzzy match: {base_name} → {best_match[0]} ({int(best_score*100)}%)")
        return best_match
    
    return None, None

def is_valid_url_for_site(url, site_key):
    """Check if URL is valid for given site"""
    if site_key == 'toono':
        return '/series/' in url or '/episode/' in url or '/movies/' in url
    elif site_key == 'rareanimes':
        return 'rareanimes.app/' in url or 'raretoonsindia' in url
    elif site_key == 'animedubhindi':
        return 'animedubhindi' in url
    elif site_key == 'gdflix':
        return '/file/' in url
    elif site_key == 'swift':
        return 'multiquality' in url or 'liptron' in url
    elif site_key == 'codedew':
        return 'codedew.com' in url
    elif site_key == 'hindianimezone':
        return 'hindianimezone' in url
    elif site_key == 'toonworld4all':
        return 'toonworld4all' in url
    return False

user_cooldowns = {}

for d in [DOWNLOAD_DIR, THUMB_DIR, DB_DIR, WORKER_DIR, BACKUP_DIR]:
    os.makedirs(d, exist_ok=True)

# ==========================================
# DATABASE
# ==========================================
db = {
    'owner_id': OWNER_ID,
    'admins': set(),
    'banned': set(),
    'users': {},
    'monitored': {},
    'thumbnails': {},
    'thumb_last_used': {},
    'settings': {'default_interval': 3},
    'premium_users': {},
    'captions': {},
    'rename_rules': {},
    'metadata': {},
    'channels': {}
}

task_queue = deque(maxlen=MAX_QUEUE)
active_tasks = {}
active_downloads = {}
worker_status = {}
download_semaphore = None
upload_semaphore = None
batch_semaphore = None
queue_lock = None

_sf = False
_rf = False

def load_db():
    global db
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'rb') as f:
                loaded = pickle.load(f)
                db.update(loaded)

        if db['owner_id'] is None:
            db['owner_id'] = OWNER_ID

        if 'thumb_last_used' not in db:
            db['thumb_last_used'] = {}
        if 'captions' not in db:
            db['captions'] = {}
        if 'premium_users' not in db:
            db['premium_users'] = {}

        if 'global_free_expiry' not in db:
            db['global_free_expiry'] = 0

        if isinstance(db.get('admins'), list):
            db['admins'] = set(db['admins'])
        if isinstance(db.get('banned'), list):
            db['banned'] = set(db['banned'])

    except Exception as e:
        print(f"DB Load Error: {e}")

def save_db():
    try:
        with open(DB_FILE, 'wb') as f:
            pickle.dump(db, f)
    except Exception as e:
        print(f"DB Save Error: {e}")

# ==========================================
# TASK MANAGER
# ==========================================
class Task:
    def __init__(self, user_id, chat_id, content_type, content_key, url):
        self.task_id = f"task_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        self.cancel_id = uuid.uuid4().hex[:6]  # Short ID for /cancel command
        self.user_id = user_id
        self.chat_id = chat_id
        self.content_type = content_type
        self.content_key = content_key
        self.url = url
        self.directory = os.path.join(WORKER_DIR, self.task_id)
        self.files = []
        self.status = "pending"
        self.created_at = time.time()
        self.subscribers = [{'user_id': user_id, 'chat_id': chat_id}]
        self.series_name = "Unknown"
        self.episode = 0
        self.is_movie = False

        # Batch & Progress tracking
        self.batch_mode = False
        self.current_episode = 0
        self.total_episodes = 0
        self.swift_url = None
        self.available_qualities = []

        # Cancel system
        self.cancelled = False
        self.active_process = None   # Store aria2/ffmpeg subprocess
        self.status_obj = None       # Store Status object for progress update

        os.makedirs(self.directory, exist_ok=True)

    def add_subscriber(self, user_id, chat_id):
        if not any(s['user_id'] == user_id for s in self.subscribers):
            self.subscribers.append({'user_id': user_id, 'chat_id': chat_id})

    def cancel(self):
        """Cancel this task - kill process and mark cancelled"""
        self.cancelled = True
        self.status = "cancelled"

        # Kill active download/ffmpeg process
        if self.active_process:
            try:
                self.active_process.terminate()
            except:
                pass
            try:
                self.active_process.kill()
            except:
                pass
            self.active_process = None

    def cleanup(self):
        try:
            if os.path.exists(self.directory):
                shutil.rmtree(self.directory)
        except:
            pass

def get_content_key(url, series_name=None, episode=None):
    if "/movies/" in url:
        match = re.search(r'/movies/([^/]+)', url)
        return f"movie_{match.group(1)}" if match else f"movie_{hash(url)}"
    elif "/episode/" in url:
        match = re.search(r'/episode/([^/]+)', url)
        return f"episode_{match.group(1)}" if match else f"ep_{hash(url)}"
    elif "/series/" in url and episode:
        match = re.search(r'/series/([^/]+)', url)
        key = match.group(1) if match else hash(url)
        return f"series_{key}_ep{episode}"
    elif "swift.multiquality" in url:
        return f"swift_{hash(url)}"
    return f"url_{hash(url)}"

def add_to_queue(task_type, task, status, episodes=None):
    if len(task_queue) >= MAX_QUEUE:
        return False, "Queue full"

    # Store status object on task for cancel reference
    task.status_obj = status

    item = {'type': task_type, 'task': task, 'status': status}
    if episodes:
        item['episodes'] = episodes

    task_queue.append(item)
    active_downloads[task.task_id] = task

    return True, f"Queued (Position: {len(task_queue)})"

# ==========================================
# COOLDOWN SYSTEM
# ==========================================
def check_cooldown(user_id):
    if user_id in user_cooldowns:
        elapsed = time.time() - user_cooldowns[user_id]
        if elapsed < COOLDOWN_TIME:
            return False, int(COOLDOWN_TIME - elapsed)
    return True, 0

def update_cooldown(user_id):
    user_cooldowns[user_id] = time.time()

async def cooldown_check(m):
    uid = m.from_user.id
    if is_owner(uid) or is_admin(uid):
        return True
    can_proceed, remaining = check_cooldown(uid)
    if not can_proceed:
        await m.reply(f"⏳ **Cooldown Active**\n\nPlease wait **{remaining} seconds**")
        return False
    return True

# ==========================================
# HELPERS
# ==========================================

# ✅ ADD THIS NEW FUNCTION (Pehle se existing helpers ke baad)
def safe_request(url, max_retries=3, timeout=20):
    """Safe request with retry mechanism for connection errors"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                verify=False
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError,
                ConnectionResetError) as e:
            print(f"⚠️ Request attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))  # 2s, 4s, 6s delay
                continue
            raise e
        except Exception as e:
            print(f"❌ Request error: {e}")
            raise e
    return None

def fmt_bytes(s):
    if s < 1024: return f"{s} B"
    elif s < 1024**2: return f"{s/1024:.2f} KB"
    elif s < 1024**3: return f"{s/1024**2:.2f} MB"
    return f"{s/1024**3:.2f} GB"

def fmt_time(s):
    if s < 0 or s > 86400: return "∞"
    elif s < 60: return f"{int(s)}s"
    elif s < 3600: return f"{int(s//60)}m {int(s%60)}s"
    return f"{int(s//3600)}h {int((s%3600)//60)}m"

def progress_bar(p, l=15):
    f = int(l * p / 100)
    return f"[{'█'*f}{'░'*(l-f)}]"

def clean_name(n):
    c = re.sub(r'\[.*?\]_?', '', n)
    return re.sub(r'\s+', ' ', c).strip()

# ===== YEH FUNCTION MILA =====
def get_quality(n):
    n = n.lower()
    if "1080" in n: return "1080P FHD"
    if "720" in n: return "720P HD"
    if "480" in n: return "480P SD"
    if "360" in n: return "360P SD"
    return "Unknown"
# ===== YEH FUNCTION get_quality KE BAAD ADD KARO =====

# ==========================================
# ✅ clean_anime_name - IMPROVED (Code 01)
# ==========================================
def clean_anime_name(filename):
    """Extract ONLY anime name - removes ALL junk"""
    name = str(filename)
    
    # Step 1: Remove file extension
    name = re.sub(r'\.(mp4|mkv|avi|webm|zip)$', '', name, flags=re.I)
    
    # Step 2: Remove meta prefix (meta_123_)
    name = re.sub(r'^meta_\d+_', '', name)
    
    # Step 3: Remove ALL bracket tags [anything]
    name = re.sub(r'\[.*?\]', '', name)
    
    # Step 4: Remove S01E03 and EVERYTHING after it
    cut = re.search(r'\s*S\d+\s*E\d+', name, re.I)
    if cut:
        name = name[:cut.start()]
    
    # Step 5: Remove "Season X" and everything after
    cut = re.search(r'\s*Season\s*\d+', name, re.I)
    if cut:
        name = name[:cut.start()]
    
    # Step 6: Remove "Episode X" and everything after
    cut = re.search(r'\s*Episode\s*\d+', name, re.I)
    if cut:
        name = name[:cut.start()]
    
    # Step 7: Remove "NxM" format (e.g. 3x7) and everything after
    cut = re.search(r'\s+\d+x\d+', name)
    if cut:
        name = name[:cut.start()]
    
    # Step 8: Remove quality (480p, 720p etc) and EVERYTHING after
    cut = re.search(r'\s+\d{3,4}[pP]', name)
    if cut:
        name = name[:cut.start()]
    
    # Step 9: Remove codec (x264, x265, HEVC) and EVERYTHING after
    cut = re.search(r'\s+(x264|x265|HEVC|AVC|AAC|WEB|BluRay|HDRip|10bit)', name, re.I)
    if cut:
        name = name[:cut.start()]
    
    # Step 10: Remove language words and EVERYTHING after
    cut = re.search(r'\s+(Hindi|English|Tamil|Telugu|Japanese|Korean|Multi|Dual|Dubbed|Esub|Sub)', name, re.I)
    if cut:
        name = name[:cut.start()]
    
    # Step 11: Remove known site names
    for tag in ['RareToonsIndia', 'Toono', 'AnimeDubHindi', 'RAI', 'RTI', 'HindiDub', 'toono.app']:
        name = re.sub(re.escape(tag), '', name, flags=re.I)
    
    # Step 12: Clean URL slugs (lowercase-hyphenated after underscore)
    if '_' in name:
        parts = name.split('_')
        clean_parts = []
        for i, part in enumerate(parts):
            part = part.strip()
            if i > 0 and re.match(r'^[a-z0-9\-]+$', part) and '-' in part:
                continue
            if part:
                clean_parts.append(part)
        name = ' '.join(clean_parts)
    
    # Step 13: Final cleanup
    name = re.sub(r'[\s_\-]+', ' ', name)
    name = re.sub(r'\[\s*\]', '', name)
    name = re.sub(r'\(\s*\)', '', name)
    name = name.strip(' _-.,')
    
    return name if name and len(name) > 1 else "Unknown"


def clean_anime_title_from_filename(filename):
    """Same as clean_anime_name"""
    return clean_anime_name(filename)
    
def extract_season_episode_from_filename(filename):
    """Extract season and episode number from filename"""
    season = None
    episode = None
    
    # Try S01E03 format
    se_match = re.search(r'S(\d+)\s*E(\d+)', filename, re.I)
    if se_match:
        season = int(se_match.group(1))
        episode = int(se_match.group(2))
        return season, episode
    
    # Try Season 1 Episode 3 format
    season_match = re.search(r'Season\s*(\d+)', filename, re.I)
    ep_match = re.search(r'Episode\s*(\d+)', filename, re.I)
    
    if season_match:
        season = int(season_match.group(1))
    if ep_match:
        episode = int(ep_match.group(1))
    
    # Try just E03 or Ep03
    if not episode:
        ep_only = re.search(r'(?:E|Ep)(\d+)', filename, re.I)
        if ep_only:
            episode = int(ep_only.group(1))
    
    return season, episode

def get_audio_language(video_path):
    """Get audio language from video file using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)

        languages = []
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                tags = stream.get('tags', {})
                lang = tags.get('language', tags.get('LANGUAGE', ''))
                title = tags.get('title', tags.get('TITLE', ''))

                title_lower = title.lower() if title else ''

                if lang:
                    lang_map = {
                        'hin': 'Hindi', 'hindi': 'Hindi', 'hi': 'Hindi',
                        'eng': 'English', 'english': 'English', 'en': 'English',
                        'jpn': 'Japanese', 'japanese': 'Japanese', 'ja': 'Japanese', 'jp': 'Japanese',
                        'tam': 'Tamil', 'tamil': 'Tamil', 'ta': 'Tamil',
                        'tel': 'Telugu', 'telugu': 'Telugu', 'te': 'Telugu',
                        'kor': 'Korean', 'korean': 'Korean', 'ko': 'Korean',
                        'chi': 'Chinese', 'chinese': 'Chinese', 'zh': 'Chinese',
                        'ben': 'Bengali', 'bengali': 'Bengali', 'bn': 'Bengali',
                        'mar': 'Marathi', 'marathi': 'Marathi', 'mr': 'Marathi',
                        'und': 'Unknown',
                    }
                    lang_name = lang_map.get(lang.lower(), lang.capitalize())
                    if lang_name not in languages and lang_name != 'Unknown':
                        languages.append(lang_name)

                if 'hindi' in title_lower and 'Hindi' not in languages:
                    languages.append('Hindi')
                elif 'english' in title_lower and 'English' not in languages:
                    languages.append('English')
                elif 'japanese' in title_lower and 'Japanese' not in languages:
                    languages.append('Japanese')

        if languages:
            return ', '.join(languages)

        filename = os.path.basename(video_path).lower()
        if 'hindi' in filename or 'hin' in filename:
            return 'Hindi'
        elif 'english' in filename or 'eng' in filename:
            return 'English'
        elif 'japanese' in filename or 'jpn' in filename:
            return 'Japanese'
        elif 'dual' in filename:
            return 'Dual Audio'
        elif 'multi' in filename:
            return 'Multi Audio'

        return "Unknown"

    except Exception as e:
        print(f"Language detection error: {e}")
        return "Unknown"

# ==========================================
# 🎧 LANGUAGE DETECTION - FIXED
# ==========================================
def get_audio_language_strict(video_path):
    """
    Get ACTUAL language names from audio streams
    Returns: "Hindi, Tamil, Telugu" (not "Audio Track (5)")
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)

        iso_to_name = {
            'hin': 'Hindi', 'hindi': 'Hindi', 'hi': 'Hindi',
            'eng': 'English', 'english': 'English', 'en': 'English',
            'jpn': 'Japanese', 'japanese': 'Japanese', 'ja': 'Japanese', 'jp': 'Japanese',
            'tam': 'Tamil', 'tamil': 'Tamil', 'ta': 'Tamil',
            'tel': 'Telugu', 'telugu': 'Telugu', 'te': 'Telugu',
            'kor': 'Korean', 'korean': 'Korean', 'ko': 'Korean',
            'chi': 'Chinese', 'chinese': 'Chinese', 'zh': 'Chinese',
            'ben': 'Bengali', 'bengali': 'Bengali', 'bn': 'Bengali',
            'mar': 'Marathi', 'marathi': 'Marathi', 'mr': 'Marathi',
        }

        detected = []
        seen = set()
        audio_count = 0

        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_count += 1
                tags = stream.get('tags', {})
                lang = tags.get('language', tags.get('LANGUAGE', '')).lower().strip()
                title = tags.get('title', tags.get('TITLE', '')).lower().strip()

                name = None

                # Method 1: ISO code lookup (PRIMARY)
                if lang and lang != 'und':
                    name = iso_to_name.get(lang)

                # Method 2: Title word search (FALLBACK, strict)
                if not name and title:
                    for lang_name in ['Hindi', 'English', 'Tamil', 'Telugu', 'Japanese', 'Korean', 'Chinese']:
                        if re.search(r'\b' + lang_name + r'\b', title, re.I):
                            name = lang_name
                            break

                if name and name not in seen:
                    detected.append(name)
                    seen.add(name)

        if detected:
            return ', '.join(detected)

        # Fallback: If language tags exist but couldn't map
        if audio_count > 1:
            return f"Multi Audio ({audio_count} tracks)"
        elif audio_count == 1:
            return "Audio"

        return "No Audio"

    except Exception as e:
        print(f"Language detection error: {e}")
        return None

def clean_unwanted_tags(filename, user_id=None):
    """Remove unwanted tags from filename - includes user's custom rules"""
    result = filename

    # Default patterns to remove
    default_patterns = [
        r'\[RTI\]',
        r'\[RareToonsIndia\]',
        r'RareToonsIndia',
        r'\[Toono\]',
        r'\[toono\]',
        r'Toono\.in',
        r'toono\.in',
        r'Toono',
        r'toono',
        r'\[HindiDub\]',
        r'\[Hindi\s*Dub\]',
        r'\[Dubbed\]',
        r'\[RAI\]',
        r'\[rai\]',
        r'RAI',
    ]

    # Apply default patterns
    for pattern in default_patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    # Apply user's custom rename rules
    if user_id and user_id in db.get('rename_rules', {}):
        for rule in db['rename_rules'][user_id]:
            try:
                # Escape special regex characters
                escaped_rule = re.escape(rule)
                result = re.sub(escaped_rule, '', result, flags=re.IGNORECASE)
            except Exception as e:
                print(f"Rename rule error: {e}")
                # Simple replace as fallback
                result = result.replace(rule, '')

    # Clean up formatting
    result = re.sub(r'_+', '_', result)
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'_\s', '_', result)
    result = re.sub(r'\s_', '_', result)
    result = re.sub(r'\[\s*\]', '', result)
    result = re.sub(r'-\s*-', '-', result)
    result = re.sub(r'\s*-\s*-\s*', ' - ', result)
    result = result.strip('_ -')

    return result


# ==========================================
# STYLISH SYSTEM
# ==========================================

def auto_correct_tags(text):
    """Auto-correct common tag mistakes"""
    
    # 1. Lowercase to uppercase: [b] → [B], [t] → [T], etc.
    def uppercase_single_tag(match):
        return '[' + match.group(1).upper() + ']'
    
    text = re.sub(r'\[([btmqsn])\]', uppercase_single_tag, text, flags=re.IGNORECASE)
    
    # 2. Fix [sp] → [SP]
    text = re.sub(r'\[sp\]', '[SP]', text, flags=re.IGNORECASE)
    
    # 3. Fix URL tag: [u:url] → [U:url]
    def fix_url_tag(match):
        return f"[U:{match.group(1)}]"
    text = re.sub(r'\[u:([^\]]+)\]', fix_url_tag, text, flags=re.IGNORECASE)
    
    # 4. Fix combinations without +: [BT] → [B+T], [bt] → [B+T], [BTM] → [B+T+M]
    def fix_combo_no_plus(match):
        inner = match.group(1).upper()
        # Check if it's valid single chars without + or :
        if '+' not in inner and ':' not in inner:
            valid_chars = ['B', 'T', 'M', 'Q', 'S']
            chars = list(inner)
            if all(c in valid_chars for c in chars) and len(chars) >= 2:
                return '[' + '+'.join(chars) + ']'
        return '[' + inner + ']'
    
    text = re.sub(r'\[([BTMQSbtmqs]{2,})\]', fix_combo_no_plus, text, flags=re.IGNORECASE)
    
    # 5. Fix [BSP] → [B+SP], [SPB] → [SP+B], etc.
    def fix_sp_combo(match):
        before = match.group(1).upper() if match.group(1) else ''
        after = match.group(2).upper() if match.group(2) else ''
        parts = []
        if before:
            parts.extend(list(before))
        parts.append('SP')
        if after:
            parts.extend(list(after))
        return '[' + '+'.join(parts) + ']'
    
    text = re.sub(r'\[([BTMQS]*)SP([BTMQS]*)\]', fix_sp_combo, text, flags=re.IGNORECASE)
    
    # 6. Fix URL combos: [BU:url] → [B+U:url], [BTU:url] → [B+T+U:url]
    def fix_url_combo(match):
        prefix = match.group(1).upper()
        url = match.group(2)
        if prefix:
            parts = list(prefix)
            return '[' + '+'.join(parts) + '+U:' + url + ']'
        return '[U:' + url + ']'
    
    text = re.sub(r'\[([BTMQS]*)U:([^\]]+)\]', fix_url_combo, text, flags=re.IGNORECASE)
    
    # 7. Normalize spacing around +: [B + T] → [B+T], [ B+T ] → [B+T]
    def normalize_tag_spacing(match):
        inner = match.group(1)
        # Remove spaces around +
        inner = re.sub(r'\s*\+\s*', '+', inner)
        # Remove leading/trailing spaces
        inner = inner.strip()
        return '[' + inner + ']'
    
    text = re.sub(r'\[\s*([^\]]+?)\s*\]', normalize_tag_spacing, text)
    
    # 8. Fix lowercase in combos: [b+t] → [B+T]
    def uppercase_combo(match):
        inner = match.group(1)
        parts = inner.split('+')
        fixed_parts = []
        for p in parts:
            p = p.strip()
            if p.lower() in ['b', 't', 'm', 'q', 's', 'sp']:
                fixed_parts.append(p.upper())
            elif p.lower().startswith('u:'):
                fixed_parts.append('U:' + p[2:])
            else:
                fixed_parts.append(p.upper())
        return '[' + '+'.join(fixed_parts) + ']'
    
    text = re.sub(r'\[([^\]]*\+[^\]]*)\]', uppercase_combo, text)
    
    return text


def parse_styled_caption(template):
    """Parse caption template with style tags and return HTML formatted text"""
    
    try:
        # Auto-correct first
        template = auto_correct_tags(template)
        
        # Tag to HTML mapping
        tag_map = {
            'B': ('<b>', '</b>'),
            'T': ('<i>', '</i>'),
            'M': ('<code>', '</code>'),
            'Q': ('<blockquote>', '</blockquote>'),
            'S': ('<s>', '</s>'),
            'SP': ('<tg-spoiler>', '</tg-spoiler>'),
        }
        
        # Pattern to match tags
        tag_pattern = r'\[((?:[BTMQS]|SP)(?:\+(?:[BTMQS]|SP))*(?:\+U:[^\]]+)?|U:[^\]]+)\]'
        
        matches = list(re.finditer(tag_pattern, template, re.IGNORECASE))
        
        if not matches:
            # No tags found, return as-is
            return template
        
        result = []
        
        # Check if first tag is at position 0
        first_match = matches[0]
        if first_match.start() > 0:
            # Text before first tag - no styling
            result.append(template[:first_match.start()])
        
        for i, match in enumerate(matches):
            tag_start = match.start()
            tag_end = match.end()
            tag_content = match.group(1).upper()
            
            # Determine where this tag's text ends (next tag or end of string)
            if i + 1 < len(matches):
                text_end = matches[i + 1].start()
            else:
                text_end = len(template)
            
            # Get the text for this tag
            text = template[tag_end:text_end]
            
            if not text:
                continue
            
            # Parse the tag for styles and URL
            styles = []
            url = None
            
            # Extract URL if present: U:something
            url_match = re.search(r'U:([^\+\]]+)', tag_content)
            if url_match:
                url = url_match.group(1).strip()
                # Remove URL part from tag_content for further parsing
                tag_content = re.sub(r'\+?U:[^\+\]]+', '', tag_content)
                tag_content = tag_content.strip('+')
            
            # Parse remaining style tags
            if tag_content:
                for style in tag_content.split('+'):
                    style = style.strip().upper()
                    if style in tag_map:
                        styles.append(style)
            
            # Build styled text
            styled_text = text
            
            # Apply URL first (innermost)
            if url:
                # Ensure URL has protocol
                if not url.startswith('http://') and not url.startswith('https://') and not url.startswith('tg://'):
                    url = 'https://' + url
                styled_text = f'<a href="{url}">{styled_text}</a>'
            
            # Apply other styles (wrap around)
            for style in styles:
                if style in tag_map:
                    open_tag, close_tag = tag_map[style]
                    styled_text = f'{open_tag}{styled_text}{close_tag}'
            
            result.append(styled_text)
        
        # ✅ FIXED: return OUTSIDE for loop
        return ''.join(result)
        
    except Exception as e:
        print(f"Parse error: {e}")
        # Return template without tags as fallback
        return re.sub(r'\[.*?\]', '', template)


def apply_caption_variables(template, file_name, season, episode, language, quality, size_str, duration_str):
    """Replace variables in caption template"""
    caption = template
    
    # Replace variables (case insensitive)
    caption = re.sub(r'\{f\}', file_name, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{s\}(?!z)', str(season) if season else 'N/A', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{e\}', str(episode) if episode else 'N/A', caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{l\}', language, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{q\}', quality, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{sz\}', size_str, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{d\}', duration_str, caption, flags=re.IGNORECASE)
    
    return caption


def apply_caption_variables(template, file_name, season, episode, language, quality, size_str, duration_str):
    """Replace variables in caption template"""
    caption = template
    
    # ✅ FIX: Convert all to string to avoid errors
    file_name = str(file_name) if file_name else "Unknown"
    season = str(season) if season else "N/A"
    episode = str(episode) if episode else "N/A"
    language = str(language) if language else "Unknown"
    quality = str(quality) if quality else "Unknown"
    size_str = str(size_str) if size_str else "Unknown"
    duration_str = str(duration_str) if duration_str else "Unknown"
    
    # Replace variables (case insensitive)
    caption = re.sub(r'\{f\}', file_name, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{s\}(?!z)', season, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{e\}', episode, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{l\}', language, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{q\}', quality, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{sz\}', size_str, caption, flags=re.IGNORECASE)
    caption = re.sub(r'\{d\}', duration_str, caption, flags=re.IGNORECASE)
    
    return caption


def apply_custom_caption(template, file_name, season, episode, language, quality, size_str, duration_str):
    """Full caption processing: variables + styling"""
    
    try:
        # Step 1: Replace variables first
        caption = apply_caption_variables(
            template, file_name, season, episode, 
            language, quality, size_str, duration_str
        )
        
        # Step 2: Apply styling tags
        caption = parse_styled_caption(caption)
        
        return caption
    except Exception as e:
        print(f"Caption error: {e}")
        # Return plain text as fallback
        caption = template
        caption = re.sub(r'\{f\}', str(file_name), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{s\}(?!z)', str(season), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{e\}', str(episode), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{l\}', str(language), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{q\}', str(quality), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{sz\}', str(size_str), caption, flags=re.IGNORECASE)
        caption = re.sub(r'\{d\}', str(duration_str), caption, flags=re.IGNORECASE)
        # Remove all tags
        caption = re.sub(r'\[.*?\]', '', caption)
        return caption

# ==========================================
# BACKUP SYSTEM HELPERS
# ==========================================
async def create_backup():
    """Create backup of premium users data"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Collect premium user IDs
        premium_uids = set(db.get('premium_users', {}).keys())
        admin_uids = db.get('admins', set())
        owner_uid = {db.get('owner_id')} if db.get('owner_id') else set()
            # Sabko set bana kar merge kiya
        all_important_uids = set(premium_uids) | set(admin_uids) | (owner_uid if isinstance(owner_uid, set) else {owner_uid})


        
        # Prepare backup data
        backup_data = {
            'backup_time': timestamp,
            'bot_version': '12.0',
            'owner_id': db.get('owner_id'),
            'admins': list(db.get('admins', set())),
            'banned': list(db.get('banned', set())),
            'premium_users': db.get('premium_users', {}),
            'monitored': {},
            'thumbnails': {},
            'captions': {},
            'users': {}
        }
        
        # Filter monitored for premium users
        for key, data in db.get('monitored', {}).items():
            premium_subs = [s for s in data['subscribers'] if s['user_id'] in all_important_uids]
            if premium_subs:
                backup_data['monitored'][key] = data.copy()
                backup_data['monitored'][key]['subscribers'] = premium_subs
        
        # Filter thumbnails for premium users
        for uid, thumbs in db.get('thumbnails', {}).items():
            if uid in all_important_uids:
                backup_data['thumbnails'][uid] = thumbs
        
        # Filter captions for premium users
        for uid, caption in db.get('captions', {}).items():
            if uid in all_important_uids:
                backup_data['captions'][uid] = caption
        
        # Filter users for premium users
        for uid, udata in db.get('users', {}).items():
            if uid in all_important_uids:
                backup_data['users'][uid] = udata
        
        # Calculate stats
        stats = {
            'premium_users': len(premium_uids),
            'total_monitored': len(backup_data['monitored']),
            'total_thumbnails': sum(len(t) for t in backup_data['thumbnails'].values()),
            'total_captions': len(backup_data['captions']),
        }
        
        # Create backup files
        backup_files = []
        
        # Main database pickle
        main_pkl = os.path.join(BACKUP_DIR, f"backup_{timestamp}_data.pkl")
        with open(main_pkl, 'wb') as f:
            pickle.dump(backup_data, f)
        backup_files.append(main_pkl)
        
        # Stats JSON (human readable)
        stats_json = os.path.join(BACKUP_DIR, f"backup_{timestamp}_stats.json")
        with open(stats_json, 'w') as f:
            json.dump({
                'backup_time': timestamp,
                'stats': stats,
                'premium_user_ids': list(premium_uids),
                'admin_ids': list(admin_uids)
            }, f, indent=2)
        backup_files.append(stats_json)
        
        # Info text
        info_txt = os.path.join(BACKUP_DIR, f"backup_{timestamp}_info.txt")
        with open(info_txt, 'w') as f:
            f.write(f"Anime Bot Backup\n")
            f.write(f"================\n")
            f.write(f"Time: {timestamp}\n")
            f.write(f"Premium Users: {stats['premium_users']}\n")
            f.write(f"Monitored: {stats['total_monitored']}\n")
            f.write(f"Thumbnails: {stats['total_thumbnails']}\n")
            f.write(f"Captions: {stats['total_captions']}\n")
        backup_files.append(info_txt)
        
        # Create ZIP files (max 1.9GB each)
        zip_files = await create_split_zips(backup_files, timestamp)
        
        # Cleanup temp files
        for f in backup_files:
            try:
                os.remove(f)
            except:
                pass
        
        return zip_files, stats
        
    except Exception as e:
        print(f"Backup error: {e}")
        traceback.print_exc()
        return [], {}


async def create_split_zips(files, timestamp):
    """Create ZIP files with max 1.9GB each"""
    import zipfile
    
    zip_files = []
    part = 1
    current_zip = None
    current_size = 0
    current_zip_path = None
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        file_size = os.path.getsize(file_path)
        
        # Check if need new ZIP
        if current_zip is None or (current_size + file_size > MAX_ZIP_SIZE):
            # Close current ZIP
            if current_zip:
                current_zip.close()
                zip_files.append(current_zip_path)
            
            # Start new ZIP
            current_zip_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}_part{part}.zip")
            current_zip = zipfile.ZipFile(current_zip_path, 'w', zipfile.ZIP_DEFLATED)
            current_size = 0
            part += 1
        
        # Add file to ZIP
        current_zip.write(file_path, os.path.basename(file_path))
        current_size += file_size
    
    # Close last ZIP
    if current_zip:
        current_zip.close()
        zip_files.append(current_zip_path)
    
    return zip_files


async def send_backup_to_channel(zip_files, stats):
    """Send backup files to channel"""
    try:
        total_size = sum(os.path.getsize(f) for f in zip_files if os.path.exists(f))
        
        # Build message
        msg = f"""📦 **DAILY BACKUP**
━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {datetime.now().strftime('%d %b %Y, %I:%M %p')}

━━━━━━━━━━━━━━━━━━━━━━
📊 **BACKUP STATS**
━━━━━━━━━━━━━━━━━━━━━━
💎 Premium Users: {stats.get('premium_users', 0)}
📺 Monitored Series: {stats.get('total_monitored', 0)}
🖼️ Thumbnails: {stats.get('total_thumbnails', 0)}
📝 Custom Captions: {stats.get('total_captions', 0)}

━━━━━━━━━━━━━━━━━━━━━━
📦 **FILES**
━━━━━━━━━━━━━━━━━━━━━━"""
        
        for i, zf in enumerate(zip_files, 1):
            size = os.path.getsize(zf) if os.path.exists(zf) else 0
            msg += f"\nPart {i}/{len(zip_files)} → {fmt_bytes(size)}"
        
        msg += f"""

💾 Total Size: {fmt_bytes(total_size)}
━━━━━━━━━━━━━━━━━━━━━━"""
        
        # Send message first
        await bot.send_message(BACKUP_CHANNEL, msg)
        
        # Send each ZIP file
        for zf in zip_files:
            if os.path.exists(zf):
                await bot.send_document(
                    BACKUP_CHANNEL,
                    zf,
                    caption=f"📦 {os.path.basename(zf)}"
                )
                await asyncio.sleep(2)
        
        # Cleanup ZIP files
        for zf in zip_files:
            try:
                os.remove(zf)
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"Send backup error: {e}")
        traceback.print_exc()
        return False


async def cleanup_old_backups():
    """Delete backups older than 2 days from channel"""
    try:
        two_days_ago = time.time() - (2 * 24 * 60 * 60)
        
        async for message in bot.get_chat_history(BACKUP_CHANNEL, limit=100):
            if message.document and message.date.timestamp() < two_days_ago:
                try:
                    await message.delete()
                except:
                    pass
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Cleanup old backups error: {e}")

# ===== IS FUNCTION KE BILKUL NEECHE YEH PASTE KARO =====
def clean_page_title(title):
    """Clean page title for better file naming"""
    if not title:
        return "Unknown"
    
    # Remove common prefixes
    title = re.sub(r'^(DOWNLOAD|Download|Watch|WATCH):\s*', '', title, flags=re.I)
    title = re.sub(r'^(Hindi|English|Tamil|Telugu|Dubbed)\s*-\s*', '', title, flags=re.I)
    
    # Remove extra quality info at end
    title = re.sub(r'\s*(360|480|720|1080)[pP]?\s*(WEB-DL|BluRay|HDRip|WEBRip).*$', '', title, flags=re.I)
    
    # Clean up spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def get_key(url):
    m = re.search(r'/series/([^/]+)', url)
    return m.group(1) if m else None

def fuzzy(n, lst, t=0.68):
    best, r = None, 0
    for x in lst:
        s = SequenceMatcher(None, n.lower(), x.lower()).ratio()
        if s > r: best, r = x, s
    return (best, int(r*100)) if r >= t else (None, 0)

def parse_filename(filename):
    name = clean_name(filename)
    name = re.sub(r'\.(mp4|mkv|avi|webm)$', '', name, flags=re.I)
    original_name = name

    name = re.sub(r'\s*(360|480|720|1080)[pP]?\s*(SD|HD|FHD)?\s*', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    info = {
        'name': name,
        'season': None,
        'episode': None,
        'is_movie': False,
        'year': None
    }

    se_match = re.search(r'S(\d+)\s*E(\d+)', original_name, re.I)
    if se_match:
        info['season'] = int(se_match.group(1))
        info['episode'] = int(se_match.group(2))
        info['name'] = re.sub(r'\s*S\d+\s*E\d+.*', '', name, flags=re.I).strip()

    if not info['episode']:
        ep_match = re.search(r'[\s\-_](\d{1,4})\s*(?:360|480|720|1080|$)', original_name)
        if ep_match:
            info['episode'] = int(ep_match.group(1))
            info['name'] = re.sub(r'\s*[\-_]?\s*\d{1,4}\s*$', '', info['name']).strip()

    year_match = re.search(r'\((\d{4})\)', original_name)
    if year_match:
        info['year'] = int(year_match.group(1))
        info['is_movie'] = True
        info['name'] = re.sub(r'\s*\(\d{4}\)', '', info['name']).strip()

    if not info['episode'] and not info['season']:
        if info['year'] or 'movie' in original_name.lower():
            info['is_movie'] = True

    info['name'] = re.sub(r'\s+', ' ', info['name']).strip()
    if not info['name']:
        info['name'] = clean_name(filename.rsplit('.', 1)[0])

    return info

def make_caption(anime_name, filepath, size, duration, user_id=None, clean_filename=None):
    """Generate caption with clean anime name"""

    # Get all info from file
    info = parse_filename(os.path.basename(filepath))
    quality = get_real_quality(filepath)
    language = get_audio_language(filepath)

    # ✅ CLEAN ANIME NAME - Remove all metadata
    raw_name = clean_filename if clean_filename else os.path.basename(filepath)
    display_name = clean_anime_title_from_filename(raw_name)
    
    # Fallback if cleaning failed
    if not display_name or display_name in ["Unknown", "Direct Download", "Download", ""]:
        display_name = clean_anime_title_from_filename(anime_name)
    
    # Still empty? Use provided name
    if not display_name or display_name in ["Unknown", ""]:
        display_name = anime_name

    # Get season/episode from filename
    file_season, file_ep = extract_season_episode_from_filename(raw_name)
    
    season = file_season or info.get('season') or 'N/A'
    episode = file_ep or info.get('episode') or 'N/A'
    size_str = fmt_bytes(size)
    duration_str = fmt_dur(duration)

    # Custom caption check
    if user_id and user_id in db.get('captions', {}):
        template = db['captions'][user_id]
        styled_caption = apply_custom_caption(
            template, display_name, season, episode,
            language, quality, size_str, duration_str
        )
        return styled_caption

    # Default caption
    if info.get('is_movie'):
        cap = f"""🎬 {display_name}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🍿 Type: Movie
│ 🌐 Language: {language}
│ 📊 Quality: {quality}
│ 📦 Size: {size_str}
│ ⏱️ Duration: {duration_str}
╰━━━━━━━━━━━━━━━━━━━╯"""
    else:
        cap = f"""🎬 {display_name}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🏝️ Season: {season}
│ 📺 Episode: {episode}
│ 🌐 Language: {language}
│ 📊 Quality: {quality}
│ 📦 Size: {size_str}
│ ⏱️ Duration: {duration_str}
╰━━━━━━━━━━━━━━━━━━━╯"""

    return cap

def smart_thumb_match(anime_name, user_thumbs):
    if not user_thumbs:
        return None

    if anime_name in user_thumbs:
        return user_thumbs[anime_name]

    best_match, similarity = fuzzy(anime_name, user_thumbs.keys(), t=0.68)
    if best_match:
        return user_thumbs[best_match]

    name_parts = anime_name.lower().split()[:2]
    for thumb_name in user_thumbs.keys():
        thumb_parts = thumb_name.lower().split()[:2]
        if name_parts and thumb_parts and name_parts[0] == thumb_parts[0]:
            return user_thumbs[thumb_name]

    return None

def role(uid):
    if db['owner_id'] == uid: return "👑 Owner"
    if uid in db['admins']: return "⚔️ Admin"
    if uid in db['banned']: return "🚫 Banned"
    return "👤 User"

def is_admin(uid): return uid == db['owner_id'] or uid in db['admins']
def is_owner(uid): return uid == db['owner_id']
def is_master(uid): return uid == db['owner_id']  # Master = Owner (full access)

# ==========================================
# BUTTON SYSTEM HELPERS
# ==========================================
def get_help_buttons(user_id):
    """Create role-based help buttons"""
    buttons = []

    # Row 1: Commands + My List
    buttons.append([
        InlineKeyboardButton("📋 Commands", callback_data="help_user"),
        InlineKeyboardButton("📂 My List", callback_data="refresh_list"),
    ])

    # Row 2: Status + Full Guide (always visible)
    buttons.append([
        InlineKeyboardButton("📊 My Status", callback_data="refresh_status"),
        InlineKeyboardButton("📚 Guide", url="https://t.me/Animex_Studio/14"),
    ])

    # Admin row - Admin/Owner only
    if is_admin(user_id) or is_owner(user_id):
        buttons.append([
            InlineKeyboardButton("⚔️ Admin Panel", callback_data="help_admin"),
            InlineKeyboardButton("🌐 Global Stats", callback_data="refresh_gstatus"),
        ])

    # Owner row - Owner only
    if is_owner(user_id):
        buttons.append([
            InlineKeyboardButton("👑 Owner Panel", callback_data="help_owner"),
        ])

    return InlineKeyboardMarkup(buttons)

# Button content messages
HELP_USER = """
📋 **COMMANDS GUIDE**
━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **MONITOR & DOWNLOAD**
├ `/set` URL — Monitor anime (auto-alert)
├ `/batch` URL S01 Ep 1-7 — Batch download
├ `/list` — View all monitored anime
├ `/del` NUM — Remove from list
├ `/website` — Detailed monitor view
└ `/cancel` — Cancel running task

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 **DIRECT LEECH**
├ `/l0` URL — Download & upload to TG
├ `/l0` URL -e — Download & extract ZIP
└ `/l0` URL -e PASS — Extract with password

━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼️ **THUMBNAILS**
├ `/thum NAME` — Set thumb (reply to image)
├ `/seethum` — View all saved thumbs
└ `/delthum` NAME — Delete a thumb

━━━━━━━━━━━━━━━━━━━━━━━━━━
✍️ **CUSTOM CAPTION**
├ `/setcaption` — Set your caption template
├ `/seecaption` — Preview your caption
└ `/delcaption` — Reset to default

━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 **CHANNEL AUTO-UPLOAD**
├ `/addchannel` ID ANIME — Link a channel
├ `/seechannel` — View linked channels
└ `/delchannel` NUM — Unlink & leave

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 **TOOLS**
├ `/status` — Your usage stats
└ `/cleanup` — Clear your data

💡 **Tip:** Just send any anime URL directly — no command needed!
"""

HELP_ADMIN = """
⚔️ **ADMIN PANEL**

━━━━━━━━━━━━━━━━━━━━━━
👮 **USER MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━
• **/ban** ID - Ban user
• **/unban** ID - Unban user
• **/seeban** - View banned

━━━━━━━━━━━━━━━━━━━━━━
🍱 **BHANDARA CAMMAND**
━━━━━━━━━━━━━━━━━━━━━━
• **/free** day - Bhandara karane ke liye
• **/unfree** - Bhandara khatm karane ke liye

━━━━━━━━━━━━━━━━━━━━━━
💎 **PREMIUM CONTROL**
━━━━━━━━━━━━━━━━━━━━━━
• **/pm** ID DAYS - Grant premium
• **/repm** ID - Remove premium
• **/pmlist** - View premium users
• **/npcleanup** - Clean non-premium data

━━━━━━━━━━━━━━━━━━━━━━
📊 **SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━
• **/gstatus** - Global status
• **/time MIN** - Check interval
• **/cleanupspace** - Clean temp files
• **/broadcast** - Message all users
• **/domain** OLD to NEW - Change domain

━━━━━━━━━━━━━━━━━━━━━━
"""

HELP_OWNER = """
👑 **OWNER PANEL**

━━━━━━━━━━━━━━━━━━━━━━
👥 **ADMIN MANAGEMENT**
━━━━━━━━━━━━━━━━━━━━━━
• **/admin** ID - Add admin
• **/radmin** ID - Remove admin
• **/seeadmin** - View admins

━━━━━━━━━━━━━━━━━━━━━━
📦 **BACKUP & RESTORE**
━━━━━━━━━━━━━━━━━━━━━━
• **/backup** - Manual backup
• **/update** - Start restore mode
• **/restore** confirm - Apply restore

━━━━━━━━━━━━━━━━━━━━━━
📊 **SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━
• **/dashboard** - Full dashboard
• **/reset** - Reset database

━━━━━━━━━━━━━━━━━━━━━━
"""

# ==========================================
# FORCE SUBSCRIPTION SYSTEM
# ==========================================
FORCE_SUB_CHANNELS = [
    -1003684316624,  # Your channel ID
]
FORCE_SUB_ENABLED = False  # False = Disable & True = Enable 

async def check_force_sub(client, user_id):
    """Check if user joined required channels"""
    if not FORCE_SUB_ENABLED:
        return True, None
    
    # Owner/Admin bypass
    if is_owner(user_id) or is_admin(user_id):
        return True, None
    
    from pyrogram.errors import UserNotParticipant
    
    not_joined = []
    
    for channel_id in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ["left", "banned", "restricted"]:
                not_joined.append(channel_id)
        except UserNotParticipant:
            not_joined.append(channel_id)
        except Exception as e:
            print(f"Force sub error: {e}")
            not_joined.append(channel_id)
    
    if not_joined:
        buttons = []
        for i, ch_id in enumerate(not_joined, 1):
            try:
                chat = await client.get_chat(ch_id)
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    link = await client.export_chat_invite_link(ch_id)
                buttons.append([InlineKeyboardButton(f"📢 Join Channel {i}", url=link)])
            except:
                pass
        
        buttons.append([InlineKeyboardButton("🔄 Joined? Click Here", callback_data="check_fsub")])
        return False, InlineKeyboardMarkup(buttons)
    
    return True, None
# ==========================================
# PREMIUM SYSTEM HELPERS
# ==========================================
def is_premium(uid):
    """Check if user has active premium"""
    if is_owner(uid) or is_admin(uid):
        return True
    # ✅ 1. Pehle Global Free Expiry Check karo
    global_expiry = db.get('global_free_expiry', 0)
    if time.time() < global_expiry:
        return True
    
    if uid not in db.get('premium_users', {}):
        return False

    expiry = db['premium_users'][uid].get('expires', 0)
    if time.time() > expiry:
        del db['premium_users'][uid]
        save_db()
        return False

    return True

def get_premium_days_left(uid):
    """Get remaining premium days"""
    if uid not in db.get('premium_users', {}):
        return 0

    expiry = db['premium_users'][uid].get('expires', 0)
    remaining = expiry - time.time()
    if remaining <= 0:
        return 0

    return int(remaining / 86400)

def add_premium(uid, days, granted_by):
    """Grant premium to user"""
    if 'premium_users' not in db:
        db['premium_users'] = {}

    expiry = time.time() + (days * 86400)
    db['premium_users'][uid] = {
        'expires': expiry,
        'granted_by': granted_by,
        'granted_on': time.time(),
        'notified_2h': False,       # ✅ NEW LINE
        'notified_expiry': False,   # ✅ NEW LINE
        'notified_cleanup': False   # ✅ NEW LINE
    }
    save_db()

def remove_premium(uid):
    """Remove premium from user"""
    if uid in db.get('premium_users', {}):
        del db['premium_users'][uid]
        save_db()
        return True
    return False

async def premium_check(m):
    """Check if user has premium access"""
    uid = m.from_user.id

    if is_owner(uid) or is_admin(uid):
        return True

    if not is_premium(uid):
        await m.reply(f"""
🚫 **Premium Required!**

━━━━━━━━━━━━━━━━━━━━━━
⚠️ This bot is **Premium Only**

💎 **Get Premium Access:**
Contact owner to purchase premium

👤 **Owner Contact:**
👉 @Wejdufjcjcjc_bot
💪**Support Channel**
👉 https://t.me/Animex_Studio

━━━━━━━━━━━━━━━━━━━━━━
💰 **Premium Benefits:**
✅ Auto anime monitoring
✅ Batch downloads (15 eps)
✅ Custom Caption
✅ Custom thumbnails
✅ Auto Channel Uploading
✅ All qualities (360p to 1080p)
✅ Priority support

━━━━━━━━━━━━━━━━━━━━━━
📞 Contact now! **@Dark_isekai**
""")
        return False

    return True

def is_banned(uid): return uid in db['banned']

def validate_file(path):
    if not os.path.exists(path):
        return False, "Not found"
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return False, "Too small"
        if not path.lower().endswith(('.mp4', '.mkv', '.avi', '.webm')):
            return False, "Invalid format"
        return True, "OK"
    except Exception as e:
        return False, str(e)

def get_system_stats():
    try:
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        return {
            'ram_used': ram.used / (1024**3),
            'ram_total': ram.total / (1024**3),
            'ram_percent': ram.percent,
            'disk_used': disk.used / (1024**3),
            'disk_total': disk.total / (1024**3),
            'disk_percent': disk.percent,
            'cpu_percent': cpu
        }
    except:
        return None

# ==========================================
# VIDEO HELPERS
# ==========================================
def video_info(p):
    try:
        r = subprocess.run(
            ['ffprobe','-v','quiet','-print_format','json','-show_format','-show_streams',p],
            capture_output=True, text=True, timeout=30
        )
        d = json.loads(r.stdout)
        dur = int(float(d.get('format',{}).get('duration',0)))
        w, h = 1280, 720
        for s in d.get('streams',[]):
            if s.get('codec_type') == 'video':
                w, h = s.get('width',1280), s.get('height',720)
                break
        return dur, w, h
    except:
        return 0, 1280, 720


def make_thumb(v, o):
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-ss', '00:00:05', '-i', v, '-vframes', '1', '-vf', 'scale=320:-1', '-q:v', '2', o],
            capture_output=True, timeout=30
        )
        if os.path.exists(o) and os.path.getsize(o) > 0:
            return o
    except Exception as e:
        print(f"Thumbnail error: {e}")
    return None


def fmt_dur(s):
    if s <= 0:
        return "00:00"
    h, m, sec = int(s // 3600), int((s % 3600) // 60), int(s % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"

# ==========================================
# 🎧 AUDIO FILTER - PERMANENT FIX (ISO Code Only)
# ==========================================
async def filter_audio(input_path, languages, output_dir):
    """
    PERMANENT FIX - Uses ONLY ISO 639-2 language codes
    No title matching = No false positives
    """
    try:
        print(f"   🎧 Audio Filter: {languages}")

        # Step 1: Probe file
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_path],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)

        # Step 2: Get all audio tracks with EXACT info
        audio_tracks = []
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                tags = stream.get('tags', {})
                lang_code = tags.get('language', tags.get('LANGUAGE', 'und')).lower().strip()
                title = tags.get('title', tags.get('TITLE', '')).strip()
                audio_tracks.append({
                    'index': stream['index'],
                    'lang': lang_code,
                    'title': title
                })

        if not audio_tracks:
            print(f"   ⚠️ No audio tracks found!")
            return input_path

        # Step 3: Log EVERY track (debugging)
        iso_to_name = {
            'hin': 'Hindi', 'eng': 'English', 'tam': 'Tamil',
            'tel': 'Telugu', 'jpn': 'Japanese', 'kor': 'Korean',
            'chi': 'Chinese', 'ben': 'Bengali', 'mar': 'Marathi',
            'und': 'Undefined'
        }

        print(f"   📊 Audio tracks: {len(audio_tracks)}")
        for t in audio_tracks:
            name = iso_to_name.get(t['lang'], t['lang'])
            print(f"      Stream {t['index']}: [{t['lang']}] = {name}")

        # Step 4: Convert user input to ISO codes
        lang_to_iso = {
            'hindi': 'hin', 'english': 'eng', 'tamil': 'tam',
            'telugu': 'tel', 'japanese': 'jpn', 'korean': 'kor',
            'chinese': 'chi', 'bengali': 'ben', 'marathi': 'mar',
            # Accept ISO codes directly too
            'hin': 'hin', 'eng': 'eng', 'tam': 'tam', 'tel': 'tel',
            'jpn': 'jpn', 'kor': 'kor', 'chi': 'chi', 'ben': 'ben',
            'mar': 'mar'
        }

        req_langs = [l.strip().lower() for l in languages.replace('+', ',').split(',')]

        if 'all' in req_langs:
            print(f"   ℹ️ 'All' requested, no filtering needed")
            return input_path

        # Convert to ISO set
        req_iso = set()
        for req in req_langs:
            if req in lang_to_iso:
                req_iso.add(lang_to_iso[req])
            else:
                req_iso.add(req)

        print(f"   🎯 Looking for ISO codes: {req_iso}")

        # Step 5: EXACT match only (no substring, no title)
        keep_indices = []
        for track in audio_tracks:
            track_name = iso_to_name.get(track['lang'], track['lang'])

            if track['lang'] in req_iso:
                keep_indices.append(track['index'])
                print(f"   ✅ KEEP  stream {track['index']}: {track_name} ({track['lang']})")
            else:
                print(f"   ❌ SKIP  stream {track['index']}: {track_name} ({track['lang']})")

        # Step 6: Fallback if nothing matched
        if not keep_indices:
            print(f"   ⚠️ No exact match! Trying title-based fallback...")

            # ONLY now try title (word boundary, strict)
            for track in audio_tracks:
                for req in req_langs:
                    # Strict word boundary match in title
                    if re.search(r'\b' + re.escape(req) + r'\b', track['title'], re.I):
                        if track['index'] not in keep_indices:
                            keep_indices.append(track['index'])
                            print(f"   ✅ KEEP (title match) stream {track['index']}: '{track['title']}'")

        # Still nothing? Keep first track
        if not keep_indices:
            keep_indices = [audio_tracks[0]['index']]
            print(f"   ⚠️ No match at all! Keeping first audio track")

        # Step 7: Check if filtering is needed
        if len(keep_indices) >= len(audio_tracks):
            print(f"   ℹ️ All {len(audio_tracks)} tracks match, no filtering needed")
            return input_path

        # Step 8: Build FFmpeg command
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"af_{int(time.time())}_{base_name}.mkv")

        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-map', '0:v:0'
        ]

        for idx in keep_indices:
            cmd.extend(['-map', f'0:{idx}'])

        cmd.extend([
            '-map', '0:s?',
            '-c', 'copy',
            '-max_muxing_queue_size', '1024',
            output_path
        ])

        print(f"   🔧 Running FFmpeg: keeping {len(keep_indices)}/{len(audio_tracks)} tracks")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Step 9: Validate output
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1024 * 1024:
            orig_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            print(f"   ✅ Filter SUCCESS: {fmt_bytes(orig_size)} → {fmt_bytes(new_size)}")
            print(f"   ✅ Kept {len(keep_indices)} tracks, removed {len(audio_tracks) - len(keep_indices)} tracks")
            return output_path
        else:
            error_msg = stderr.decode()[-200:] if stderr else "Unknown error"
            print(f"   ❌ FFmpeg failed: {error_msg}")
            # Cleanup failed output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            return input_path

    except Exception as e:
        print(f"   ❌ Filter error: {e}")
        traceback.print_exc()
        return input_path

# ==========================================
# FILE SPLITTING SYSTEM (2GB+ files)
# ==========================================
async def split_video(input_path, output_dir, st=None):
    """Split video into parts if larger than 1.9GB for Telegram"""
    
    try:
        file_size = os.path.getsize(input_path)
        
        # If file is smaller than limit, no need to split
        if file_size <= MAX_FILE_SIZE:
            return [input_path]
        
        if st:
            await st.update(f"✂️ **File too large ({fmt_bytes(file_size)})**\n\n📦 Splitting into parts...", force=True)
        
        print(f"✂️ Splitting file: {fmt_bytes(file_size)}")
        
        # Get video duration
        duration, _, _ = video_info(input_path)
        if duration <= 0:
            print("❌ Can't get duration, skipping split")
            return [input_path]
        
        # Calculate number of parts needed
        num_parts = int(file_size / MAX_FILE_SIZE) + 1
        part_duration = duration / num_parts
        
        # Get base filename
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        ext = os.path.splitext(input_path)[1] or ".mp4"
        
        split_files = []
        
        for i in range(num_parts):
            start_time = i * part_duration
            part_file = os.path.join(output_dir, f"{base_name}_Part{i+1:02d}{ext}")
            
            if st:
                await st.update(f"""
✂️ **Splitting Large File...**

📦 Original: {fmt_bytes(file_size)}
🗂️ Parts: {num_parts}

⏳ **Creating Part {i+1}/{num_parts}...**
""", force=True)
            
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(int(start_time)),
                '-i', input_path,
                '-t', str(int(part_duration) + 1),
                '-c', 'copy',
                '-avoid_negative_ts', 'make_zero',
                part_file
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
                
                if os.path.exists(part_file):
                    part_size = os.path.getsize(part_file)
                    if part_size > 1024:
                        split_files.append(part_file)
                        print(f"   ✅ Part {i+1}: {fmt_bytes(part_size)}")
            except Exception as e:
                print(f"   ❌ Split error part {i+1}: {e}")
        
        # Verify all parts created
        if len(split_files) >= num_parts - 1:
            # ✅ DON'T delete original yet - will delete after upload success
            print(f"✅ Split complete: {len(split_files)} parts (original kept as backup)")
            return split_files
        
        # Split failed, cleanup and return original
        print("❌ Split failed, using original file")
        for f in split_files:
            try:
                os.remove(f)
            except:
                pass
        return [input_path]
        
    except Exception as e:
        print(f"❌ Split error: {e}")
        traceback.print_exc()
        return [input_path]
    
def get_real_quality(video_path):
    """Get actual video quality from file using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                width = stream.get('width', 0)
                height = stream.get('height', 0)
                
                # Detect quality based on height
                if height >= 1080:
                    return "1080P FHD"
                elif height >= 720:
                    return "720P HD"
                elif height >= 480:
                    return "480P SD"
                elif height >= 360:
                    return "360P SD"
                else:
                    return f"{height}P"
        
        return "Unknown Quality"
    except Exception as e:
        print(f"Quality detection error: {e}")
        return "Unknown Quality"

async def apply_metadata(input_path, tag, filename, season=None, episode=None, quality=None):
    """Apply metadata to ALL streams with user's tag + Smart filename"""
    process = None
    
    try:
        if not os.path.exists(input_path):
            print(f"❌ Input file not found")
            return input_path
        
        file_size = os.path.getsize(input_path)
        if file_size < 1024 * 1024:
            print(f"⚠️ File too small for metadata")
            return input_path
        
        # Get stream info first
        probe_result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_path],
            capture_output=True, text=True, timeout=60
        )
        
        if probe_result.returncode != 0:
            print(f"⚠️ FFprobe failed, skipping metadata")
            return input_path
        
        streams_data = json.loads(probe_result.stdout)
        streams = streams_data.get('streams', [])
        
        output_dir = os.path.dirname(input_path)
        
        # ==========================================
        # SMART FILENAME BUILDING
        # ==========================================
        # Clean the base name first
        base_name = os.path.splitext(filename)[0]
        base_name = re.sub(r'^meta_\d+_', '', base_name)
        base_name = re.sub(r'^\[@?\w+\]\s*', '', base_name)
        
        # Extract anime name (clean version for title)
        anime_name = clean_anime_name(base_name)
        
        # Try to extract season/episode from filename if not provided
        if season is None or episode is None:
            file_season, file_episode = extract_season_episode_from_filename(filename)
            if season is None:
                season = file_season
            if episode is None:
                episode = file_episode
        
        # Get quality from filename or detect
        if quality is None:
            quality = get_real_quality(input_path)
        
        # Extract just the resolution number (480, 720, 1080)
        quality_short = None
        if quality:
            qual_match = re.search(r'(\d{3,4})', str(quality))
            if qual_match:
                quality_short = qual_match.group(1) + 'p'
        
        # Build smart filename: AnimeName S1 Ep3 480p.mp4
        smart_filename = anime_name
        
        if season is not None and episode is not None:
            smart_filename += f" S{season} Ep{episode}"
        elif episode is not None:
            smart_filename += f" Ep{episode}"
        
        if quality_short:
            smart_filename += f" {quality_short}"
        
        # Clean up the filename
        smart_filename = re.sub(r'\s+', ' ', smart_filename).strip()
        
        # Output path with tag and smart filename
        output_path = os.path.join(output_dir, f"meta_{int(time.time())}_{tag}_{smart_filename}.mkv")
        
        # Title for metadata (with tag)
        meta_title = f"[{tag}] {smart_filename}"
        
        # ==========================================
        # BUILD FFMPEG COMMAND
        # ==========================================
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-map', '0',
            '-c', 'copy',
            # Global metadata
            '-metadata', f'title={meta_title}',
            '-metadata', f'artist={tag}',
            '-metadata', f'author={tag}',
            '-metadata', f'album={tag}',
            '-metadata', f'comment={tag}',
            '-metadata', f'description={tag}',
            '-metadata', f'show={tag}',
            '-metadata', f'encoder={tag}',
        ]
        
        # Add metadata for EACH stream
        video_idx = 0
        audio_idx = 0
        sub_idx = 0
        
        for stream in streams:
            stream_type = stream.get('codec_type', '')
            
            if stream_type == 'video':
                stream_title = f"{tag} [{quality_short or 'Video'}]"
                cmd.extend([
                    f'-metadata:s:v:{video_idx}', f'title={stream_title}',
                    f'-metadata:s:v:{video_idx}', f'handler_name={tag}',
                ])
                video_idx += 1
                
            elif stream_type == 'audio':
                # Get this stream's language
                tags = stream.get('tags', {})
                lang = tags.get('language', tags.get('LANGUAGE', '')).lower()
                lang_map = {'hin': 'Hindi', 'eng': 'English', 'tam': 'Tamil', 
                           'tel': 'Telugu', 'jpn': 'Japanese', 'kor': 'Korean'}
                lang_name = lang_map.get(lang, lang.capitalize() if lang else 'Audio')
                
                stream_title = f"{tag} [{lang_name}]"
                cmd.extend([
                    f'-metadata:s:a:{audio_idx}', f'title={stream_title}',
                    f'-metadata:s:a:{audio_idx}', f'handler_name={tag}',
                ])
                audio_idx += 1
                
            elif stream_type == 'subtitle':
                cmd.extend([
                    f'-metadata:s:s:{sub_idx}', f'title={tag}',
                    f'-metadata:s:s:{sub_idx}', f'handler_name={tag}',
                ])
                sub_idx += 1
        
        cmd.append(output_path)
        
        print(f"   🏷️ Applying [{tag}] to {video_idx} video, {audio_idx} audio, {sub_idx} subtitle streams")
        print(f"   📁 Smart filename: {smart_filename}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        except asyncio.TimeoutError:
            print(f"❌ Metadata timeout")
            if process:
                try:
                    process.kill()
                except:
                    pass
            return input_path
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1024:
            print(f"✅ Metadata applied: [{tag}] {smart_filename}")
            return output_path
        else:
            print(f"❌ Metadata failed")
            return input_path
    
    except Exception as e:
        print(f"❌ Metadata error: {e}")
        if process:
            try:
                process.kill()
            except:
                pass
        return input_path

# ==========================================
# 📦 ZIP FILE EXTRACTION
# ==========================================
async def extract_zip_file(zip_path, extract_dir):
    """Extract ZIP file and return list of video files"""
    import zipfile
    
    extracted_videos = []
    
    try:
        print(f"📦 Extracting ZIP: {os.path.basename(zip_path)}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List files in ZIP
            file_list = zip_ref.namelist()
            print(f"   📁 Files in ZIP: {len(file_list)}")
            
            # Extract all
            zip_ref.extractall(extract_dir)
        
        # Find video files
        video_extensions = ('.mp4', '.mkv', '.avi', '.webm', '.mov', '.wmv')
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Only include files > 10MB
                    if file_size > 10 * 1024 * 1024:
                        extracted_videos.append(file_path)
                        print(f"   ✅ Found: {file} ({fmt_bytes(file_size)})")
        
        # Delete original ZIP
        try:
            os.remove(zip_path)
            print(f"   🗑️ Deleted ZIP file")
        except:
            pass
        
        print(f"📦 Extracted {len(extracted_videos)} video(s)")
        return extracted_videos
        
    except zipfile.BadZipFile:
        print(f"   ❌ Not a valid ZIP file")
        return []
    except Exception as e:
        print(f"   ❌ Extraction error: {e}")
        return []


def is_zip_file(filepath):
    """Check if file is a ZIP archive - STRICT CHECK"""
    if not os.path.exists(filepath):
        return False
    
    # Reject known video files
    video_exts = ('.mp4', '.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv', '.m4v', '.ts')
    if filepath.lower().endswith(video_exts):
        return False
    
    # Check magic bytes (ZIP signature)
    try:
        with open(filepath, 'rb') as f:
            magic = f.read(4)
            # ZIP files start with PK\x03\x04 or PK\x05\x06 or PK\x07\x08
            if magic[:2] != b'PK':
                return False
    except:
        return False
    
    # Verify with zipfile module
    import zipfile
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            # Test if it can list files (valid ZIP)
            _ = z.namelist()
        return True
    except (zipfile.BadZipFile, Exception):
        return False

# ==========================================
# 🔄 FILE RENAME TO MP4 SYSTEM
# ==========================================
def ensure_mp4_extension(filepath):
    """Rename file to .mp4 extension if not already"""
    if not os.path.exists(filepath):
        return filepath
    
    # Get directory and filename
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    # Check if already .mp4
    if filename.lower().endswith('.mp4'):
        return filepath
    
    # Remove old extension and add .mp4
    # Handles: .mkv, .avi, .webm, .mov, .wmv, .flv, etc.
    video_extensions = ['.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv', '.m4v', '.ts', '.mts']
    
    new_filename = filename
    for ext in video_extensions:
        if filename.lower().endswith(ext):
            new_filename = filename[:-len(ext)] + '.mp4'
            break
    
    # If no known extension found, just add .mp4
    if new_filename == filename:
        new_filename = filename + '.mp4'
    
    new_filepath = os.path.join(directory, new_filename)
    
    try:
        os.rename(filepath, new_filepath)
        print(f"   🔄 Renamed: {filename} → {new_filename}")
        return new_filepath
    except Exception as e:
        print(f"   ⚠️ Rename failed: {e}")
        return filepath

# ==========================================
# 🔄 SMART FILE PROCESSOR (ZIP + ENCRYPTED DETECTION)
# ==========================================
def check_video_valid_ffmpeg(filepath):
    """Check if video is valid using FFmpeg - returns True if readable"""
    try:
        if not os.path.exists(filepath):
            return False
        
        # Try to read streams with ffprobe
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0', 
             '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', filepath],
            capture_output=True, text=True, timeout=30
        )
        
        # If audio stream found, video is valid
        if 'audio' in result.stdout.lower():
            return True
        
        # Also check video stream
        result2 = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
             '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', filepath],
            capture_output=True, text=True, timeout=30
        )
        
        if 'video' in result2.stdout.lower():
            return True
        
        # Check for any error in stderr (EBML error = encrypted/corrupt)
        if 'EBML' in result.stderr or 'Invalid' in result.stderr or 'error' in result.stderr.lower():
            print(f"   ⚠️ FFmpeg error detected: File might be encrypted/ZIP")
            return False
        
        return False
        
    except subprocess.TimeoutExpired:
        print(f"   ⚠️ FFprobe timeout")
        return False
    except Exception as e:
        print(f"   ⚠️ FFprobe check error: {e}")
        return False

def try_unzip_file(filepath, extract_dir, attempt=1):
    """Try to unzip a file - returns list of extracted files or empty list"""
    import zipfile
    
    print(f"   📦 Unzip attempt {attempt}/3...")
    
    try:
        # First, check if it's actually a ZIP
        if not zipfile.is_zipfile(filepath):
            print(f"   ❌ Not a valid ZIP file")
            return []
        
        extracted_files = []
        
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            # Get list of files
            file_list = zip_ref.namelist()
            print(f"   📁 Files in ZIP: {len(file_list)}")
            
            # Extract all
            zip_ref.extractall(extract_dir)
            
            # Find video files
            for fname in file_list:
                fpath = os.path.join(extract_dir, fname)
                if os.path.exists(fpath) and is_video_file(fpath):
                    extracted_files.append(fpath)
                    print(f"   ✅ Extracted: {fname}")
        
        # Delete original ZIP after successful extraction
        if extracted_files:
            try:
                os.remove(filepath)
                print(f"   🗑️ Deleted original ZIP")
            except:
                pass
        
        return extracted_files
        
    except zipfile.BadZipFile:
        print(f"   ❌ Bad/Corrupt ZIP file")
        return []
    except Exception as e:
        print(f"   ❌ Unzip error: {e}")
        return []

async def process_downloaded_file(filepath, extract_dir=None):
    """
    Smart file processor:
    1. Check if valid video with FFmpeg
    2. If FFmpeg fails → Try as ZIP (might be encrypted)
    3. Retry up to 3 times
    4. Rename to .mp4
    """
    if not os.path.exists(filepath):
        return []
    
    directory = extract_dir or os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    final_files = []
    
    print(f"\n   🔍 Processing: {filename}")
    print(f"   📦 Size: {fmt_bytes(os.path.getsize(filepath))}")
    
    # ==========================================
    # STEP 1: Check if file is already a ZIP (by extension)
    # ==========================================
    if filepath.lower().endswith('.zip'):
        print(f"   📦 ZIP extension detected")
        
        for attempt in range(1, 4):  # 3 attempts
            extracted = try_unzip_file(filepath, directory, attempt)
            if extracted:
                # Process extracted files (rename to .mp4)
                for f in extracted:
                    if is_video_file(f):
                        renamed = ensure_mp4_extension(f)
                        final_files.append(renamed)
                break
            else:
                if attempt < 3:
                    print(f"   🔄 Retrying in 2 seconds...")
                    await asyncio.sleep(2)
        
        if final_files:
            return final_files
        else:
            print(f"   ❌ All unzip attempts failed")
            return [filepath]  # Return original if all attempts fail
    
    # ==========================================
    # STEP 2: Check with FFmpeg if video is valid
    # ==========================================
    print(f"   🎬 Checking video with FFmpeg...")
    
    is_valid_video = check_video_valid_ffmpeg(filepath)
    
    if is_valid_video:
        print(f"   ✅ Valid video file")
        # Rename to .mp4 and return
        renamed = ensure_mp4_extension(filepath)
        return [renamed]
    
    # ==========================================
    # STEP 3: FFmpeg failed → File might be encrypted/ZIP
    # ==========================================
    print(f"   ⚠️ FFmpeg can't read file - Trying as ZIP...")
    
    # Rename file to .zip
    zip_path = filepath
    if not filepath.lower().endswith('.zip'):
        zip_path = filepath + '.zip'
        try:
            os.rename(filepath, zip_path)
            print(f"   🔄 Renamed to: {os.path.basename(zip_path)}")
        except Exception as e:
            print(f"   ❌ Rename failed: {e}")
            return [filepath]
    
    # Try to unzip (3 attempts)
    for attempt in range(1, 4):
        extracted = try_unzip_file(zip_path, directory, attempt)
        
        if extracted:
            print(f"   ✅ Extraction successful!")
            
            # Now validate and process extracted files
            for f in extracted:
                # Check if extracted file is valid
                if check_video_valid_ffmpeg(f):
                    print(f"   ✅ Valid: {os.path.basename(f)}")
                    renamed = ensure_mp4_extension(f)
                    final_files.append(renamed)
                else:
                    # Extracted file also not valid? Maybe nested ZIP
                    print(f"   ⚠️ Extracted file also invalid, checking if nested ZIP...")
                    
                    # Try as nested ZIP
                    nested_zip = f + '.zip'
                    try:
                        os.rename(f, nested_zip)
                        nested_extracted = try_unzip_file(nested_zip, directory, 1)
                        if nested_extracted:
                            for nf in nested_extracted:
                                if is_video_file(nf):
                                    renamed = ensure_mp4_extension(nf)
                                    final_files.append(renamed)
                        else:
                            # Not a nested ZIP, rename back
                            os.rename(nested_zip, f)
                            renamed = ensure_mp4_extension(f)
                            final_files.append(renamed)
                    except:
                        renamed = ensure_mp4_extension(f)
                        final_files.append(renamed)
            
            break  # Success, exit retry loop
        
        else:
            if attempt < 3:
                print(f"   🔄 Attempt {attempt} failed, retrying in 2 seconds...")
                await asyncio.sleep(2)
            else:
                print(f"   ❌ All 3 attempts failed")
    
    # ==========================================
    # STEP 4: If nothing extracted, return original
    # ==========================================
    if not final_files:
        print(f"   ⚠️ Could not process file, using original")
        # Rename back if we renamed to .zip
        if zip_path != filepath and os.path.exists(zip_path):
            try:
                os.rename(zip_path, filepath)
            except:
                pass
        
        # Still try to rename to .mp4
        if os.path.exists(filepath):
            renamed = ensure_mp4_extension(filepath)
            return [renamed]
        elif os.path.exists(zip_path):
            return [zip_path]
        
        return []
    
    print(f"   ✅ Processing complete: {len(final_files)} file(s)")
    return final_files

def is_video_file(filepath):
    """Check if file is a video by extension"""
    if not os.path.exists(filepath):
        return False
    
    video_extensions = ('.mp4', '.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv', '.m4v', '.ts', '.mts')
    return filepath.lower().endswith(video_extensions)

def ensure_mp4_extension(filepath):
    """Rename file to .mp4 extension if not already"""
    if not os.path.exists(filepath):
        return filepath
    
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    
    # Already .mp4
    if filename.lower().endswith('.mp4'):
        return filepath
    
    # Remove old extension
    video_extensions = ['.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv', '.m4v', '.ts', '.mts', '.zip']
    
    new_filename = filename
    for ext in video_extensions:
        if filename.lower().endswith(ext):
            new_filename = filename[:-len(ext)] + '.mp4'
            break
    
    # If no known extension, just add .mp4
    if new_filename == filename and not filename.lower().endswith('.mp4'):
        new_filename = filename + '.mp4'
    
    new_filepath = os.path.join(directory, new_filename)
    
    try:
        os.rename(filepath, new_filepath)
        print(f"   🔄 Renamed: {filename} → {new_filename}")
        return new_filepath
    except Exception as e:
        print(f"   ⚠️ Rename failed: {e}")
        return filepath

def ensure_all_mp4(files_list):
    """Ensure all files in list have .mp4 extension - Final check"""
    result = []
    
    for filepath in files_list:
        if not os.path.exists(filepath):
            continue
        
        renamed = ensure_mp4_extension(filepath)
        result.append(renamed)
    
    return result
 
# ==========================================
# CHROME DRIVER FOR VPS
# ==========================================
CHROMEDRIVER_PATH = shutil.which("chromedriver") or "/nix/store/8zj50jw4w0hby47167kqqsaqw4mm5bkd-chromedriver-unwrapped-138.0.7204.100/bin/chromedriver"
CHROMIUM_PATH = shutil.which("chromium") or shutil.which("chromium-browser") or "/nix/store/qa9cnw4v5xkxyip6mb9kxqfq1z4x2dx1-chromium-138.0.7204.100/bin/chromium"

def get_chrome_options():
    opts = Options()
    opts.binary_location = CHROMIUM_PATH
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return opts

def get_driver():
    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=get_chrome_options())

def get_driver_with_download(download_dir):
    opts = get_chrome_options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    opts.add_experimental_option("prefs", prefs)
    service = Service(CHROMEDRIVER_PATH)
    d = webdriver.Chrome(service=service, options=opts)
    d.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": download_dir})
    return d

# ==========================================
#  CLIENT (OPTIMIZED FOR 8-CORE VPS)
# ==========================================
bot = Client(
    "anime",  # <--- YAHAN CHANGE KAREIN (Pehle "anime_" tha)
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    # ipv6=True ko hata diya hai kyunki error aa raha tha
    sleep_threshold=60,
    workdir=BASE_DIR
)

# ==========================================
# 🎬 ANIMEDUBHINDI FINDER
# ==========================================
class AnimeDubHindiFinder:
    """Find episodes from AnimeDubHindi website"""
    
    def __init__(self, st=None):
        self.st = st
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    
    async def get_soup(self, url): # ✅ 'async' add kiya
        try:
            # ✅ Yahan requests.get ko thread mein bheja
            resp = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=15, verify=False)
            if resp.status_code == 200:
                return await asyncio.to_thread(BeautifulSoup, resp.text, 'html.parser')
        except Exception as e:
            print(f"❌ AnimeDubHindi connection error: {e}")
        return None
    
    def clean_title(self, raw_title):
        """Clean anime title - remove all metadata"""
        title = raw_title
        
        # Remove site name
        title = re.sub(r'\s*[-|]\s*(Anime\s*Dub\s*Hindi|AnimeDubHindi).*$', '', title, flags=re.I)
        
        # Remove quality info
        title = re.sub(r'\s*(Hindi|Tamil|Telugu|English|Japanese|Multi\s*Audio).*$', '', title, flags=re.I)
        
        # Remove "Season X" but keep the number
        season_match = re.search(r'Season\s*(\d+)', title, re.I)
        season_num = season_match.group(1) if season_match else None
        
        # Clean up the title
        title = re.sub(r'\s*Season\s*\d+.*$', '', title, flags=re.I)
        title = title.strip()
        
        return title, season_num
    
    async def get_info(self, url):
        """Get series info and all episodes"""
        try:
            if self.st:
                await self.st.update("🔍 **Scanning AnimeDubHindi...**")

            print(f"\n{'='*50}")
            print(f"🎬 AnimeDubHindi Finder")
            print(f"🔗 URL: {url}")
            print(f"{'='*50}")

            soup = await self.get_soup(url)
            if not soup:
                return None, None, None, None, {}

            # Get title
            title = "Unknown"
            season_num = 1
            if soup.title:
                raw_title = soup.title.string.strip()
                title, detected_season = self.clean_title(raw_title)
                if detected_season:
                    season_num = int(detected_season)

            print(f"🎬 Title: {title}")
            print(f"🏝️ Season: {season_num}")

            # ── Priority 1: new.adhlinks.com/adhlinks.com (current structure) ──
            redirect_url = None
            redirect_type = "old"

            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'adhlinks.com' in href and '/episode/' in href:
                    redirect_url = href
                    redirect_type = "adhlinks"
                    print(f"✅ Found adhlinks episode page: {redirect_url}")
                    break

            # ── Priority 2: old links.animedubhindi.* structure ──
            if not redirect_url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if "links.animedubhindi" in href or ("animedubhindi" in href and "/episode" in href):
                        redirect_url = href
                        redirect_type = "old"
                        print(f"✅ Found old episode page: {redirect_url}")
                        break

            # ── Priority 3: any adhlinks subdomain ──
            if not redirect_url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'adhlinks.com' in href and href.startswith('http'):
                        redirect_url = href
                        redirect_type = "adhlinks"
                        break

            if not redirect_url:
                print("❌ Episode page link not found on this page!")
                return title, season_num, None, None, {}

            print(f"✅ Episode Page ({redirect_type}): {redirect_url}")

            if self.st:
                await self.st.update(f"📺 **{title}**\n\n🔗 **Fetching episodes...**")

            # Parse episodes using the correct parser for the site
            if redirect_type == "adhlinks":
                episodes = await self.parse_episodes_adhlinks(redirect_url)
            else:
                episodes = await self.parse_episodes(redirect_url)

            if not episodes:
                return title, season_num, None, redirect_url, {}

            latest_ep = max(episodes.keys()) if episodes else 0
            print(f"📺 Latest Episode: {latest_ep}")
            print(f"{'='*50}\n")

            return title, season_num, latest_ep, redirect_url, episodes

        except Exception as e:
            print(f"❌ AnimeDubHindiFinder error: {e}")
            traceback.print_exc()
            return None, None, None, None, {}
    
    async def parse_episodes_adhlinks(self, adhlinks_url):
        """Parse episodes from new.adhlinks.com page structure.
        
        Page structure:
          <h2>Series Title — Episodes Download</h2>
            <div>Episode: 01 ... [links]</div>
          <h2>Episode: 02</h2>
            <h4>[links for ep 02]</h4>
          ...
        Each episode has quality groups (480P, 720P, 1080P, 1080P x265, 1080P HQ),
        each group has: Hcloud | Multi | MEGA | GDF | Fprs links in that order.
        """
        soup = await self.get_soup(adhlinks_url)
        if not soup:
            return {}

        episodes = {}
        ep_num_re = re.compile(r'Episode[:\s]*0*(\d+)', re.I)

        def _extract_quality_links(element, element_text=None):
            """From a soup element, extract {quality: {gdf, fprs}} mapping."""
            text = element_text or element.get_text(strip=True)

            # Collect GDF and Fprs links in document order
            gdf_links, fprs_links = [], []
            for a in element.find_all('a', href=True):
                href = a['href']
                if 'gdflix' in href.lower() and '/file/' in href:
                    gdf_links.append(href)
                elif 'fpgo.xyz' in href or 'filepress' in href:
                    fprs_links.append(href)

            if not gdf_links and not fprs_links:
                return {}

            # Extract quality labels in order from the text
            # e.g. "480P x264 [Size: 150mb]...720P x264 [Size: 249mb]...1080P x265 10bit..."
            qualities = []
            seen_q = set()
            for m in re.finditer(r'(480|720|1080)[Pp]', text):
                res = m.group(1)
                ahead = text[m.start(): m.start() + 50].upper()
                if 'HQ' in ahead:
                    q = f"{res}P_HQ"
                elif '265' in ahead or '10BIT' in ahead:
                    q = f"{res}P_265"
                else:
                    q = f"{res}P"
                if q not in seen_q:
                    seen_q.add(q)
                    qualities.append(q)

            result = {}
            max_i = max(len(gdf_links), len(fprs_links))
            for i in range(max_i):
                q = qualities[i] if i < len(qualities) else f"Q{i+1}"
                if 'HQ' in q:
                    continue  # skip HQ — too large (1.5GB+)
                entry = {}
                if i < len(gdf_links):
                    entry['gdf'] = gdf_links[i]
                if i < len(fprs_links):
                    entry['fprs'] = fprs_links[i]
                if entry:
                    result[q] = entry
            return result

        # ── Scan every h2 on the page ─────────────────────────────────────
        for h2 in soup.find_all('h2'):
            h2_text = h2.get_text(strip=True)

            # Case A: h2 says "Episode: 02" → links are in next sibling(s)
            m = ep_num_re.search(h2_text)
            if m and ep_num_re.match(h2_text):
                ep_num = int(m.group(1))
                if ep_num > 500:
                    continue
                # Collect links from next siblings until next h2/hr
                combined_links = {'gdf': [], 'fprs': []}
                combined_text = ""
                sib = h2.find_next_sibling()
                while sib and sib.name not in ('h2', 'h3'):
                    if sib.name in ('h4', 'div', 'p'):
                        combined_text += sib.get_text(strip=True)
                        for a in sib.find_all('a', href=True):
                            href = a['href']
                            if 'gdflix' in href.lower() and '/file/' in href:
                                combined_links['gdf'].append(href)
                            elif 'fpgo.xyz' in href:
                                combined_links['fprs'].append(href)
                    sib = sib.find_next_sibling()

                if combined_links['gdf'] or combined_links['fprs']:
                    qmap = _extract_quality_links.__func__(self,
                        type('_E', (), {'find_all': lambda s, *a, **k: []})(),
                        combined_text) if False else None
                    # Simpler: build quality map manually
                    qualities = []
                    seen_q = set()
                    for mm in re.finditer(r'(480|720|1080)[Pp]', combined_text):
                        res = mm.group(1)
                        ahead = combined_text[mm.start(): mm.start() + 50].upper()
                        q = (f"{res}P_HQ" if 'HQ' in ahead
                             else f"{res}P_265" if ('265' in ahead or '10BIT' in ahead)
                             else f"{res}P")
                        if q not in seen_q:
                            seen_q.add(q)
                            qualities.append(q)

                    ep_data = {'qualities': {}, 'multi_links': {}}
                    for i, gdf in enumerate(combined_links['gdf']):
                        q = qualities[i] if i < len(qualities) else f"Q{i+1}"
                        if 'HQ' not in q:
                            ep_data['qualities'][q] = gdf
                    for i, fprs in enumerate(combined_links['fprs']):
                        q = qualities[i] if i < len(qualities) else f"Q{i+1}"
                        if 'HQ' not in q:
                            ep_data['multi_links'][q] = fprs

                    if ep_data['qualities'] or ep_data['multi_links']:
                        episodes[ep_num] = ep_data
                        print(f"   Ep {ep_num}: {list(ep_data['qualities'].keys())} GDF, {list(ep_data['multi_links'].keys())} Fprs")
                continue

            # Case B: main series title h2 → Episode 01 is inside the next <div>
            # The div text starts with "Episode: 01..."
            sib = h2.find_next_sibling()
            while sib and sib.name not in ('h2',):
                sib_text = sib.get_text(strip=True)
                mm = ep_num_re.match(sib_text)
                if mm and sib.name == 'div':
                    ep_num = int(mm.group(1))
                    if ep_num <= 500:
                        qmap = _extract_quality_links(sib, sib_text)
                        if qmap:
                            ep_data = {'qualities': {}, 'multi_links': {}}
                            for q, links in qmap.items():
                                if 'gdf' in links:
                                    ep_data['qualities'][q] = links['gdf']
                                if 'fprs' in links:
                                    ep_data['multi_links'][q] = links['fprs']
                            episodes[ep_num] = ep_data
                            print(f"   Ep {ep_num}: {list(ep_data['qualities'].keys())} GDF, {list(ep_data['multi_links'].keys())} Fprs")
                sib = sib.find_next_sibling()

        print(f"\n📊 adhlinks: Found {len(episodes)} episodes")
        for ep, data in sorted(episodes.items()):
            print(f"   Ep {ep}: GDF={list(data['qualities'].keys())}, Fprs={list(data['multi_links'].keys())}")
        return episodes

    async def parse_episodes(self, redirect_url):
        """Parse episodes from OLD redirect page (links.animedubhindi.*) - CAPTURE MULTI AND GDFLIX LINKS"""
        soup = await self.get_soup(redirect_url)
        if not soup:
            return {}
        
        episodes = {}
        current_ep = 0
        ep_pattern = re.compile(r'Episode\s*[:\-\s]*0?(\d+)', re.I)
        
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'li', 'a', 'strong', 'span']):
            text = tag.get_text(" ", strip=True)
            
            # Detect episode number from text
            if tag.name != 'a':
                ep_match = ep_pattern.search(text)
                if ep_match and len(text) < 50:
                    current_ep = int(ep_match.group(1))
                    if current_ep not in episodes:
                        episodes[current_ep] = {'qualities': {}, 'multi_links': {}}
            
            # Find links
            if tag.name == 'a':
                href = tag.get('href', '')
                link_text = tag.get_text(strip=True).lower()
                
                if not href:
                    continue
                
                if current_ep == 0:
                    current_ep = 1  # Default to ep 1 for movies
                
                if current_ep not in episodes:
                    episodes[current_ep] = {'qualities': {}, 'multi_links': {}}
                
                # ✅ NEW: Check for Multi/Direct links
                # Support both .me and .link and any animedubhindi sub-domain
                is_animedub_link = "links.animedubhindi" in href or "re.php" in href or (
                    "animedubhindi" in href and any(x in href for x in ['/dl', '/download', '/file', '/get', '/stream'])
                )
                if is_animedub_link:
                    quality = None
                    if "1080" in link_text:
                        quality = "1080P"
                    elif "720" in link_text:
                        quality = "720P"
                    elif "480" in link_text:
                        quality = "480P"
                    elif "360" in link_text:
                        quality = "360P"
                    elif "multi" in link_text:
                        parent_text = tag.parent.get_text() if tag.parent else ""
                        if "1080" in parent_text:
                            quality = "1080P"
                        elif "720" in parent_text:
                            quality = "720P"
                        elif "480" in parent_text:
                            quality = "480P"
                        elif "360" in parent_text:
                            quality = "360P"
                    
                    if quality and quality not in episodes[current_ep]['multi_links']:
                        # ✅ FIX: Convert relative URL to absolute using redirect_url's base
                        if not href.startswith('http'):
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(redirect_url)
                                base_url = f"{parsed.scheme}://{parsed.netloc}"
                            except:
                                base_url = 'https://links.animedubhindi.me'
                            if href.startswith('/'):
                                href = base_url + href
                            else:
                                href = base_url + '/' + href
                        
                        episodes[current_ep]['multi_links'][quality] = href
                        print(f"   Episode {current_ep}: {quality} Multi ✓")
                
                # Check for GDFlix links (FALLBACK METHOD)
                elif "gdflix" in href.lower() and "/file/" in href:
                    # Skip HQ versions
                    quality = await self.get_quality_from_gdflix(href)
                    if quality and quality not in episodes[current_ep]['qualities']:
                        episodes[current_ep]['qualities'][quality] = href
                        print(f"   Episode {current_ep}: {quality} GDFlix ✓")
        
        print(f"\n📊 Total Episodes: {len(episodes)}")
        for ep, data in episodes.items():
            multi_count = len(data.get('multi_links', {}))
            gdflix_count = len(data.get('qualities', {}))
            print(f"   Ep {ep}: {multi_count} Multi links, {gdflix_count} GDFlix links")
        
        return episodes
    
    async def get_quality_from_gdflix(self, gdflix_url):
        """Get quality by visiting GDFlix page"""
        try:
            soup = await self.get_soup(gdflix_url)
            if soup and soup.title:
                title = soup.title.string.strip()
                
                # Skip HQ versions
                if " HQ " in title.upper():
                    return None
                
                # Extract quality
                qual_match = re.search(r'\b(360p|480p|720p|1080p)\b', title, re.I)
                if qual_match:
                    q = qual_match.group(1).upper()
                    if not q.endswith('P'):
                        q += 'P'
                    return q
        except:
            pass
        return None
    
    async def check_new_episodes(self, redirect_url, last_known_ep):
        """Check for new episodes on the redirect page"""
        episodes = await self.parse_episodes(redirect_url)
        
        if not episodes:
            return None, None
        
        latest = max(episodes.keys())
        
        if latest > last_known_ep:
            return latest, episodes.get(latest, {})
        
        return None, None

# ==========================================
# 🎬 ANIMEDUBHINDI DIRECT DOWNLOADER (PRIMARY METHOD)
# ==========================================
class AnimeDubHindiDirectDownloader:
    """Direct download from AnimeDubHindi Multi links - PRIMARY METHOD"""
    
    def __init__(self, task, st=None):
        self.task = task
        self.st = st
        self.dir = task.directory
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_real_filename(self, response, url):
        """Extract real filename from response headers or URL"""
        try:
            # Method 1: Content-Disposition header
            if "content-disposition" in response.headers:
                cd = response.headers["content-disposition"]
                fname = re.findall(r"filename\*?=([^;]+)", cd, re.IGNORECASE)
                if fname:
                    clean_name = fname[0].strip().strip('"').strip("'")
                    if "UTF-8''" in clean_name:
                        clean_name = clean_name.split("UTF-8''")[-1]
                    return urllib.parse.unquote(clean_name)
            
            # Method 2: From URL
            if url:
                name = urllib.parse.unquote(url.split("/")[-1].split("?")[0])
                if name and len(name) > 3:
                    return name
        except:
            pass
        
        return f"video_{int(time.time())}.mkv"
    
# ==========================================
# ✅ In get_final_link_from_multi() - ADD at very start of function
# ==========================================
    async def get_final_link_from_multi(self, multi_url):
        """Get final download link from Multi/redirect page"""
        driver = None
        final_url = None
        
        try:
            # ✅ FIX: Convert relative URL to absolute (domain-agnostic)
            if not multi_url.startswith('http'):
                # Use task URL to infer correct base domain
                try:
                    from urllib.parse import urlparse
                    task_parsed = urlparse(getattr(self.task, 'url', ''))
                    task_host = task_parsed.netloc or 'animedubhindi.link'
                    # Use links. subdomain on same TLD
                    tld = task_host.rsplit('.', 1)[-1] if '.' in task_host else 'link'
                    links_base = f"https://links.animedubhindi.{tld}"
                except:
                    links_base = 'https://links.animedubhindi.link'
                if multi_url.startswith('/'):
                    multi_url = links_base + multi_url
                else:
                    multi_url = links_base + '/' + multi_url
                print(f"   🔗 Fixed relative URL: {multi_url[:60]}...")
            
            if self.st:
                await self.st.update("🔍 **Finding direct download link...**")
            
            # ... REST OF FUNCTION STAYS SAME ...
            
            print(f"   🌐 Opening Multi page: {multi_url[:60]}...")
            
            driver = get_driver()
            driver.set_page_load_timeout(60)
            driver.get(multi_url)
            await asyncio.sleep(8)
            
            # STEP 1: Try to click "Cloud Download" button
            cloud_clicked = False
            try:
                # Multiple XPath patterns for Cloud Download button
                xpath_patterns = [
                    "//*[contains(translate(text(), 'CLOUDWNDA', 'cloudwnda'), 'cloud download')]",
                    "//button[contains(text(), 'Cloud')]",
                    "//a[contains(text(), 'Cloud')]",
                    "//*[contains(@class, 'cloud')]",
                    "//button[contains(@onclick, 'cloud')]",
                ]
                
                for xpath in xpath_patterns:
                    try:
                        cloud_btn = driver.find_element(By.XPATH, xpath)
                        driver.execute_script("arguments[0].click();", cloud_btn)
                        print(f"   ✅ Clicked Cloud Download button")
                        cloud_clicked = True
                        await asyncio.sleep(10)
                        break
                    except:
                        continue
                
                if not cloud_clicked:
                    print(f"   ⚠️ Cloud Download button not found, trying direct link...")
                    
            except Exception as e:
                print(f"   ⚠️ Cloud button error: {e}")
            
            # STEP 2: Get Final Download URL
            final_url = None
            
            # Try multiple patterns to find download link
            link_patterns = [
                "//a[contains(text(), 'Download File')]",
                "//a[contains(text(), 'Download')]",
                "//a[contains(@href, '.mkv')]",
                "//a[contains(@href, '.mp4')]",
                "//a[contains(@href, 'download')]",
                "//a[contains(@class, 'download')]",
                "//button[contains(text(), 'Download')]",
            ]
            
            for pattern in link_patterns:
                try:
                    download_link = driver.find_element(By.XPATH, pattern)
                    href = download_link.get_attribute("href")
                    
                    if href and "http" in href and "javascript" not in href.lower():
                        # Skip if it's just the same page
                        if "links.animedubhindi" not in href and "re.php" not in href:
                            final_url = href
                            print(f"   ✅ Found download link: {final_url[:60]}...")
                            break
                except:
                    continue
            
            # STEP 3: If still no link, check page source
            if not final_url:
                page_source = driver.page_source
                # Find direct download URLs in page
                url_patterns = [
                    r'(https?://[^\s<>"\']+\.mkv[^\s<>"\']*)',
                    r'(https?://[^\s<>"\']+\.mp4[^\s<>"\']*)',
                    r'(https?://[^\s<>"\']+/download[^\s<>"\']*)',
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, page_source)
                    for match in matches:
                        if "links.animedubhindi" not in match:
                            final_url = match
                            print(f"   ✅ Found URL in source: {final_url[:60]}...")
                            break
                    if final_url:
                        break
            
            driver.quit()
            driver = None
            
            return final_url
            
        except Exception as e:
            print(f"   ❌ Get final link error: {e}")
            traceback.print_exc()
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def download_file(self, url, quality="720P"):
        """Download file with progress using AIOHTTP (Non-Blocking)"""
        try:
            if self.st:
                await self.st.update(f"📥 **Direct Download Starting...**\n\n⚡ Quality: {quality}\n⏳ Connecting...")
            
            print(f"   📥 Downloading: {url[:60]}...")
            
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=600, connect=30)
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=timeout, allow_redirects=True) as response:
                    response.raise_for_status()

                    # Get real filename
                    filename = f"video_{int(time.time())}.mkv"
                    if "content-disposition" in response.headers:
                        cd = response.headers["content-disposition"]
                        fname = re.findall(r"filename\*?=([^;]+)", cd, re.IGNORECASE)
                        if fname:
                            clean_name = fname[0].strip().strip('"').strip("'")
                            if "UTF-8''" in clean_name:
                                clean_name = clean_name.split("UTF-8''")[-1]
                            filename = urllib.parse.unquote(clean_name)
                    
                    filename = clean_unwanted_tags(filename, self.task.user_id)
                    if not filename.endswith(('.mkv', '.mp4', '.avi', '.webm')):
                        filename += '.mkv'
                    
                    save_path = os.path.join(self.dir, filename)
                    total_size = int(response.headers.get('content-length', 0))
                    
                    # Only skip if server says the file is definitely tiny (< 1MB)
                    if 0 < total_size < 1 * 1024 * 1024:
                        print(f"      ⚠️ Content-Length too small ({total_size} bytes), skipping")
                        return None
                    
                    downloaded = 0
                    start_time = time.time()
                    last_update = start_time
                    
                    with open(save_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 👇 YEH LINE  KO FREEZE HONE SE ROKEGI
                            await asyncio.sleep(0) 
                            
                            now = time.time()
                            if now - last_update >= PROGRESS_UPDATE_INTERVAL and self.st:
                                elapsed = now - start_time
                                speed = downloaded / elapsed if elapsed > 0 else 0
                                pct = (downloaded / total_size * 100) if total_size > 0 else 0
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                bar = progress_bar(pct)
                                await self.st.update(f"""
📥 **Direct Downloading...**

🎬 **{self.task.series_name}**
📔 **Episode:** {self.task.episode or 'N/A'}
🎥 **Quality:** {quality}

{bar} **{pct:.1f}%**

📦 {fmt_bytes(downloaded)} / {fmt_bytes(total_size) if total_size > 0 else '???'}
⚡ {fmt_bytes(speed)}/s | ⏱️ {fmt_time(eta)}

🚀 Method: Direct (Primary)
""")
                                last_update = now
            
            actual_size = os.path.getsize(save_path)
            if actual_size < 5 * 1024 * 1024:
                print(f"      ⚠️ Downloaded file too small ({actual_size} bytes), skipping")
                try: os.remove(save_path)
                except: pass
                return None
            
            return save_path
            
        except Exception as e:
            print(f"   ❌ Direct download error: {e}")
            return None
    
    async def download_from_multi(self, multi_url, quality="720P"):
        """Main method - Download from Multi link"""
        try:
            print(f"\n   🚀 PRIMARY METHOD: Direct Download")
            print(f"   🔗 Multi URL: {multi_url[:60]}...")
            
            # Step 1: Get final download link
            final_url = await self.get_final_link_from_multi(multi_url)
            
            if not final_url:
                print(f"   ❌ Direct method failed - No final link found")
                return None
            
            # Step 2: Download file
            result = await self.download_file(final_url, quality)
            
            return result
            
        except Exception as e:
            print(f"   ❌ Direct download error: {e}")
            return None

# ==========================================
# 📦 GDFLIX RESOLVER
# ==========================================
class GDFlixResolver:
    """Resolve GDFlix URLs to final download links"""
    
    def __init__(self, st=None):
        self.st = st
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://new3.gdflix.io/",
            "DNT": "1",
        }
    
    def _resolve_gdflix_url(self, url):
        """Follow redirects on gdflix.dev/gdflix.app → gdflix.io"""
        try:
            resp = requests.head(url, headers=self.headers, timeout=10,
                                 verify=False, allow_redirects=True)
            return resp.url
        except:
            return url

    def _get_soup_selenium_sync(self, url):
        """Synchronous Selenium loader — run via asyncio.to_thread to avoid blocking."""
        driver = None
        try:
            print(f"      🌐 Selenium loading: {url[:60]}...")
            driver = get_driver()
            driver.set_page_load_timeout(30)
            driver.get(url)
            # Wait for Cloudflare JS challenge to clear (usually 5s)
            time.sleep(6)
            if 'Just a moment' in driver.title or 'challenge' in driver.current_url:
                print(f"      ⏳ CF challenge still active, waiting 5s more...")
                time.sleep(5)
            html = driver.page_source
            driver.quit()
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"      ❌ Selenium error: {e}")
            if driver:
                try: driver.quit()
                except: pass
            return None

    async def get_soup_async(self, url):
        """Async soup fetcher: tries requests first, falls back to Selenium."""
        # Try fast requests path first
        try:
            resp = await asyncio.to_thread(
                requests.get, url, headers=self.headers,
                timeout=20, verify=False, allow_redirects=True
            )
            if resp.status_code == 200 and 'Just a moment' not in resp.text[:500]:
                return BeautifulSoup(resp.text, 'html.parser')
            print(f"      ⚠️ requests got {resp.status_code} / CF page — switching to Selenium")
        except Exception as e:
            print(f"      ⚠️ requests failed ({e}) — switching to Selenium")
        # Selenium fallback (in thread so event loop stays free)
        return await asyncio.to_thread(self._get_soup_selenium_sync, url)

    def get_soup(self, url):
        """Sync version kept for backward compat — prefer get_soup_async in async ctx."""
        try:
            resp = requests.get(url, headers=self.headers, timeout=20,
                                verify=False, allow_redirects=True)
            if resp.status_code == 200 and 'Just a moment' not in resp.text[:500]:
                return BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            print(f"      ❌ GDFlix fetch error: {e}")
        # Sync Selenium fallback
        return self._get_soup_selenium_sync(url)
    
    async def extract_all_methods(self, gdflix_url):
        """Extract ALL download methods from GDFlix page"""
        if self.st:
            await self.st.update("🔗 **Extracting download links...**")

        # Follow any gdflix.dev/app redirect to the live domain first
        gdflix_url = self._resolve_gdflix_url(gdflix_url)
        print(f"   🔍 Extracting from: {gdflix_url[:60]}...")

        all_links = []

        try:
            soup = await self.get_soup_async(gdflix_url)
            if not soup:
                return []

            intermediate_links = []
            direct_links = []

            def _classify_href(href):
                """Return (is_intermediate, link_type) or (False, '') for direct/skip."""
                for pattern in GDFLIX_INTERMEDIATE_PATTERNS:
                    if re.search(pattern, href):
                        if "zfile" in href or "zfile" in pattern:
                            return True, "Zfile"
                        elif "fastcdn" in href:
                            return True, "FastCDN"
                        else:
                            return True, "BusyCDN"
                for pattern in GDFLIX_FINAL_PATTERNS:
                    if re.search(pattern, href):
                        return False, "direct"
                return False, ""

            # ── Scan <a> tags ──────────────────────────────────────────────
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if not href or href.startswith('#') or href.startswith('javascript'):
                    continue
                if not href.startswith('http'):
                    href = urllib.parse.urljoin(gdflix_url, href)

                is_mid, ltype = _classify_href(href)
                if is_mid:
                    intermediate_links.append({'url': href, 'type': ltype})
                elif ltype == "direct":
                    direct_links.append(href)

            # ── Scan <script> tags for embedded URLs ───────────────────────
            for script in soup.find_all('script'):
                text = script.string or ''
                # extract all https:// URLs from inline JS
                for m in re.finditer(r'https?://[^\s\'"<>]+', text):
                    href = m.group(0).rstrip('",;)')
                    is_mid, ltype = _classify_href(href)
                    if is_mid:
                        if not any(x['url'] == href for x in intermediate_links):
                            intermediate_links.append({'url': href, 'type': ltype})
                    elif ltype == "direct":
                        if href not in direct_links:
                            direct_links.append(href)

            # ── Scan iframe src ────────────────────────────────────────────
            for iframe in soup.find_all('iframe', src=True):
                href = iframe['src'].strip()
                if not href.startswith('http'):
                    href = urllib.parse.urljoin(gdflix_url, href)
                is_mid, ltype = _classify_href(href)
                if is_mid:
                    if not any(x['url'] == href for x in intermediate_links):
                        intermediate_links.append({'url': href, 'type': ltype})

            print(f"      📊 Found: {len(intermediate_links)} Intermediate | {len(direct_links)} Direct")

            # Process intermediate links
            for item in intermediate_links:
                url = item['url']
                link_type = item['type']
                print(f"      🔎 Processing {link_type}: {url[:60]}...")

                if link_type == "Zfile":
                    extracted = self.extract_from_zfile(url)
                    all_links.extend(extracted)
                elif link_type == "FastCDN":
                    extracted = self._extract_from_fastcdn(url)
                    if extracted:
                        all_links.append(extracted)
                elif link_type == "BusyCDN":
                    extracted = await self.extract_from_busycdn(url)
                    if extracted:
                        all_links.append(extracted)

            # Add direct links
            all_links.extend(direct_links)
            all_links = list(dict.fromkeys(all_links))  # dedup, preserve order

            return all_links

        except Exception as e:
            print(f"      ❌ Extract error: {e}")
            import traceback; traceback.print_exc()
            return []
    
    def extract_from_zfile(self, zfile_url):
        """Extract final URLs from Zfile page (domain-agnostic)"""
        found = []
        try:
            soup = self.get_soup(zfile_url)
            if not soup:
                return found
            # Scan <a> tags
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if not href.startswith('http'):
                    href = urllib.parse.urljoin(zfile_url, href)
                for pattern in GDFLIX_FINAL_PATTERNS:
                    if re.search(pattern, href):
                        if href not in found:
                            found.append(href)
                            print(f"         ✅ Zfile link: {href[:60]}...")
                        break
            # Also scan script tags for embedded download URLs
            for script in soup.find_all('script'):
                text = script.string or ''
                for m in re.finditer(r'https?://[^\s\'"<>]+', text):
                    href = m.group(0).rstrip('",;)')
                    for pattern in GDFLIX_FINAL_PATTERNS:
                        if re.search(pattern, href) and href not in found:
                            found.append(href)
                            print(f"         ✅ Zfile(script): {href[:60]}...")
                            break
        except Exception as e:
            print(f"         ❌ Zfile error: {e}")
        return found

    def _extract_from_fastcdn(self, fastcdn_url):
        """Extract final URL from fastcdn-dl redirect (no JS needed)"""
        try:
            parsed = urllib.parse.urlparse(fastcdn_url)
            params = urllib.parse.parse_qs(parsed.query)
            if 'url' in params:
                url = params['url'][0]
                print(f"         ✅ FastCDN param: {url[:60]}...")
                return url
            # Follow the redirect with requests
            resp = requests.get(fastcdn_url, headers=self.headers, timeout=15,
                                verify=False, allow_redirects=True)
            final = resp.url
            for pattern in GDFLIX_FINAL_PATTERNS:
                if re.search(pattern, final):
                    print(f"         ✅ FastCDN redirect: {final[:60]}...")
                    return final
        except Exception as e:
            print(f"         ❌ FastCDN error: {e}")
        return None
    
    async def extract_from_busycdn(self, busycdn_url):
        """Extract final URL from BusyCDN using Selenium"""
        driver = None
        try:
            print(f"         🌐 Selenium: {busycdn_url[:60]}...")
            driver = get_driver()
            driver.get(busycdn_url)
            await asyncio.sleep(5)  # give JS time to resolve

            current_url = driver.current_url

            # Strategy 1: URL parameter in redirected URL
            if "url=" in current_url:
                parsed = urllib.parse.urlparse(current_url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'url' in params:
                    final = params['url'][0]
                    print(f"         ✅ BusyCDN param extracted!")
                    driver.quit()
                    return final

            # Strategy 2: Scan all anchor/source tags on the final page
            for link in driver.find_elements(By.TAG_NAME, 'a'):
                href = link.get_attribute('href') or ''
                if not href:
                    continue
                for pattern in GDFLIX_FINAL_PATTERNS:
                    if re.search(pattern, href):
                        print(f"         ✅ BusyCDN link match!")
                        driver.quit()
                        return href
                # fastcdn redirect embed
                if "fastcdn" in href and "url=" in href:
                    result = self._extract_from_fastcdn(href)
                    if result:
                        driver.quit()
                        return result

            # Strategy 3: Scan page source for direct URLs
            page_src = driver.page_source
            for pattern in GDFLIX_FINAL_PATTERNS:
                m = re.search(pattern, page_src)
                if m:
                    # Extract full URL around the match
                    start = max(0, m.start() - 50)
                    snippet = page_src[start:m.end() + 200]
                    url_match = re.search(r'https?://[^\s\'"<>]+', snippet)
                    if url_match:
                        final = url_match.group(0).rstrip('",;)')
                        print(f"         ✅ BusyCDN source scan: {final[:60]}...")
                        driver.quit()
                        return final

            driver.quit()
            return None

        except Exception as e:
            print(f"         ❌ BusyCDN error: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return None
    
    def categorize_links(self, links):
        """Categorize links by priority"""
        categories = {
            'workers': [],
            'google': [],
            'r2': [],
            'aws': [],
            'other': []
        }
        
        for link in links:
            if ".workers.dev" in link:
                categories['workers'].append(link)
            elif "googleusercontent.com" in link:
                categories['google'].append(link)
            elif ".r2.dev" in link:
                categories['r2'].append(link)
            elif "awscdn" in link or "aws-eu" in link:
                categories['aws'].append(link)
            else:
                categories['other'].append(link)
        
        return categories

# ==========================================
# 📥 GDFLIX DOWNLOADER
# ==========================================
class GDFlixDownloader:
    """Download from GDFlix with priority fallback"""
    
    def __init__(self, task, st=None):
        self.task = task
        self.st = st
        self.dir = task.directory
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://new3.gdflix.io/"
        }
    
    async def download_file(self, url, filename, source_name="Direct"):
        """Download single file with progress (AIOHTTP Non-Blocking)"""
        save_path = os.path.join(self.dir, filename)
        
        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=600, connect=30)  # 10 min total, 30s connect
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=timeout, allow_redirects=True) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get('content-length', 0))
                    
                    # Only reject if server explicitly says it's tiny (< 1MB)
                    if 0 < total < 1 * 1024 * 1024:
                        print(f"      ⚠️ Content-Length too small ({total} bytes), skipping")
                        return None
                    
                    downloaded = 0
                    last_update = time.time()
                    
                    with open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 👇 YEH LINE  KO FREEZE HONE SE ROKEGI
                            await asyncio.sleep(0)
                            
                            now = time.time()
                            if now - last_update >= PROGRESS_UPDATE_INTERVAL and self.st:
                                pct = (downloaded / total * 100) if total > 0 else 0
                                bar = progress_bar(pct)
                                speed = downloaded / max(1, now - last_update)
                                
                                await self.st.update(f"""
📥 **Downloading via {source_name}...**

🎬 **{self.task.series_name}**
📔 **Episode:** {self.task.episode or 'N/A'}

{bar} **{pct:.1f}%**

📦 {fmt_bytes(downloaded)} / {fmt_bytes(total)}
⚡ {fmt_bytes(speed)}/s
""")
                                last_update = now
                    
            actual_size = os.path.getsize(save_path)
            if actual_size < 5 * 1024 * 1024:
                print(f"      ⚠️ Downloaded file too small ({actual_size} bytes), skipping")
                os.remove(save_path)
                return None
            
            return save_path
                
        except Exception as e:
            print(f"      ❌ Download failed: {e}")
            if os.path.exists(save_path):
                try: os.remove(save_path)
                except: pass
            return None
    
    async def download_from_gdflix(self, gdflix_url, quality="720P"):
        """Download from GDFlix URL"""
        resolver = GDFlixResolver(self.st)

        # Get filename from page (uses Selenium/requests with CF bypass)
        soup = await resolver.get_soup_async(gdflix_url)
        filename = f"video_{quality}.mkv"
        if soup and soup.title:
            title = soup.title.string.strip()
            title = title.replace("GDFlix |", "").replace("| GDFlix", "").strip()
            filename = clean_unwanted_tags(title, self.task.user_id)
            if not filename.endswith(('.mkv', '.mp4')):
                filename += '.mkv'
        
        # Extract all methods
        all_links = await resolver.extract_all_methods(gdflix_url)
        
        if not all_links:
            print(f"      ❌ No download links found!")
            return None
        
        # Categorize by priority
        categories = resolver.categorize_links(all_links)
        
        print(f"      📊 Links: Workers={len(categories['workers'])}, Google={len(categories['google'])}, R2={len(categories['r2'])}")
        
        # Try in priority order
        priority_order = ['workers', 'google', 'r2', 'aws', 'other']
        source_names = {
            'workers': 'CFWorkers',
            'google': 'GoogleDirect', 
            'r2': 'CloudflareR2',
            'aws': 'AWS',
            'other': 'Other'
        }
        
        for category in priority_order:
            for link in categories[category]:
                source = source_names.get(category, 'Direct')
                print(f"      🔄 Trying {source}...")
                
                result = await self.download_file(link, filename, source)
                if result:
                    return result
                
                await asyncio.sleep(1)
        
        return None
    
    async def download_all_qualities(self, episode_data):
        """Download all available qualities - GDFLIX FIRST (quality-specific), MULTI FALLBACK"""
        files = []
        downloaded_qualities = set()  # Track actually downloaded qualities
        
        multi_links = episode_data.get('multi_links', {})
        gdflix_links = episode_data.get('qualities', {})
        
        # Combine all qualities
        all_qualities = set(list(multi_links.keys()) + list(gdflix_links.keys()))
        
        if not all_qualities:
            print(f"   ❌ No download links found!")
            return files
        
        total = len(all_qualities)
        print(f"   📊 Downloading {total} quality(s)...")
        print(f"   📦 GDFlix links: {list(gdflix_links.keys())} (Primary - Quality Specific)")
        print(f"   🔗 Multi links: {list(multi_links.keys())} (Fallback - May not be quality specific)")
        
        # Sort qualities: 360P, 480P, 720P, 1080P
        quality_order = {"360P": 1, "480P": 2, "720P": 3, "1080P": 4}
        sorted_qualities = sorted(all_qualities, key=lambda x: quality_order.get(x, 5))
        
        for i, quality in enumerate(sorted_qualities, 1):
            if self.st:
                await self.st.update(f"""
📥 **Downloading Quality {i}/{total}**

🎬 **{self.task.series_name}**
📔 **Episode:** {self.task.episode}

⚡ **Quality:** {quality}

🔍 Finding best download method...
""", force=True)
            
            print(f"\n   [{i}/{total}] {quality}")
            
            result = None
            quality_matched = False
            
            # ==========================================
            # 📦 PRIMARY METHOD: Try GDFlix FIRST (quality-specific, reliable)
            # ==========================================
            if quality in gdflix_links:
                print(f"   📦 Trying PRIMARY method (GDFlix - quality specific)...")
                
                try:
                    result = await self.download_from_gdflix(gdflix_links[quality], quality)
                    
                    if result and os.path.exists(result):
                        # Verify quality from filename
                        filename_lower = os.path.basename(result).lower()
                        quality_num = quality.replace('P', '').replace('p', '')
                        
                        if quality_num in filename_lower:
                            print(f"   ✅ PRIMARY method SUCCESS! Quality verified: {quality}")
                            files.append(result)
                            downloaded_qualities.add(quality)
                            await asyncio.sleep(2)
                            continue
                        else:
                            print(f"   ⚠️ Quality mismatch! Expected {quality}, got different")
                            # Still accept if no better option
                            files.append(result)
                            downloaded_qualities.add(quality)
                            await asyncio.sleep(2)
                            continue
                    else:
                        print(f"   ⚠️ PRIMARY method failed, trying fallback...")
                except Exception as e:
                    print(f"   ❌ PRIMARY method error: {e}")
            
            # ==========================================
            # 🔗 FALLBACK METHOD: Try Multi/Direct (NOT quality-specific!)
            # ==========================================
            if quality in multi_links and quality not in downloaded_qualities:
                print(f"   🔗 Trying FALLBACK method (Multi/Direct)...")
                print(f"   ⚠️ WARNING: Multi links may not be quality-specific!")
                
                try:
                    direct_downloader = AnimeDubHindiDirectDownloader(self.task, self.st)
                    result = await direct_downloader.download_from_multi(multi_links[quality], quality)
                    
                    if result and os.path.exists(result):
                        filename_lower = os.path.basename(result).lower()
                        quality_num = quality.replace('P', '').replace('p', '')
                        
                        # Check if downloaded file matches expected quality
                        if quality_num in filename_lower:
                            print(f"   ✅ FALLBACK method SUCCESS! Quality verified: {quality}")
                            files.append(result)
                            downloaded_qualities.add(quality)
                        else:
                            # Quality mismatch - check what quality we actually got
                            actual_quality = None
                            for q in ['1080', '720', '480', '360']:
                                if q in filename_lower:
                                    actual_quality = f"{q}P"
                                    break
                            
                            if actual_quality and actual_quality not in downloaded_qualities:
                                print(f"   ⚠️ Got {actual_quality} instead of {quality}, keeping it")
                                files.append(result)
                                downloaded_qualities.add(actual_quality)
                            elif actual_quality and actual_quality in downloaded_qualities:
                                print(f"   ❌ Got {actual_quality} but already have it, deleting duplicate")
                                try:
                                    os.remove(result)
                                except:
                                    pass
                            else:
                                print(f"   ⚠️ Unknown quality, keeping file anyway")
                                files.append(result)
                    else:
                        print(f"   ⚠️ FALLBACK method failed")
                except Exception as e:
                    print(f"   ❌ FALLBACK method error: {e}")
            
            if quality not in downloaded_qualities:
                print(f"   ❌ {quality} - ALL METHODS FAILED!")
            
            await asyncio.sleep(2)
        
        # Final summary
        print(f"\n   📊 Download Summary:")
        print(f"   ✅ Successfully downloaded: {list(downloaded_qualities)}")
        missing = all_qualities - downloaded_qualities
        if missing:
            print(f"   ❌ Missing qualities: {list(missing)}")
        
        self.task.files = files
        return files

# ==========================================
# STATUS
# ==========================================
class Status:
    def __init__(self, c, cid, msg=None):
        self.c, self.cid, self.msg = c, cid, msg
        self.last_update = 0

    async def create(self, t):
        try:
            self.msg = await self.c.send_message(self.cid, t)
        except:
            pass
        return self.msg

    async def update(self, t, force=False):
        now = time.time()
        if self.msg and (force or now - self.last_update >= PROGRESS_UPDATE_INTERVAL):
            try:
                await self.msg.edit_text(t)
                self.last_update = now
            except:
                pass

    async def send(self, t):
        try:
            return await self.c.send_message(self.cid, t)
        except:
            return None

# ==========================================
# URL RESOLVER - HYBRID MODE
# ==========================================
class Resolver:
    def __init__(self, st=None):
        self.st = st
        self.h = {"User-Agent": "Mozilla/5.0"}

    async def get_hidden(self, url):
        d = None
        try:
            if self.st:
                await self.st.update("🔍 **Extracting link...**")
            
            print(f"🔍 Opening episode page: {url[:60]}...")
            d = get_driver()
            d.get(url)
            await asyncio.sleep(5)
            
            soup = BeautifulSoup(d.page_source, 'html.parser')
            
            for e in soup.find_all(attrs={"data-url": True}):
                try:
                    dec = base64.b64decode(e['data-url']).decode()
                    if "trdownload" in dec or "http" in dec:
                        print(f"   ✅ Hidden link extracted: {dec[:60]}...")
                        return dec
                except Exception as err:
                    print(f"   ⚠️ Decode error: {err}")
                    pass
            
            print(f"   ❌ No data-url attribute found in page")
            return None
            
        except Exception as e:
            print(f"❌ get_hidden error: {e}")
            traceback.print_exc()
            return None
        finally:
            if d:
                try:
                    d.quit()
                except:
                    pass

    def scan_for_quality_links(self, driver, context_name="Main"):
        """🔥 NEW: Scan page for quality download links"""
        found = []
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    text = link.text.strip().lower() if link.text else ""
                    href = link.get_attribute("href")
                    if not href or "javascript" in href.lower():
                        continue
                    
                    quality = None
                    check_text = text + " " + href.lower()
                    
                    if "1080" in check_text:
                        quality = "1080p"
                    elif "720" in check_text:
                        quality = "720p"
                    elif "480" in check_text:
                        quality = "480p"
                    elif "360" in check_text:
                        quality = "360p"
                    
                    if quality:
                        # Avoid duplicates
                        existing_urls = [f['url'] for f in found]
                        if href not in existing_urls:
                            found.append({'quality': quality, 'url': href})
                            print(f"      [{context_name}] Found {quality}: {href[:50]}...")
                except:
                    pass
        except Exception as e:
            print(f"      [{context_name}] Scan error: {e}")
        return found

    async def scan_with_iframes(self, driver):
        """🔥 NEW: Scan main page + all iframes for links"""
        all_links = []
        
        # Scan main page first
        print(f"   📄 Scanning main page...")
        all_links.extend(self.scan_for_quality_links(driver, "Main"))
        
        # Scan all iframes
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                print(f"   📦 Found {len(iframes)} iframes, scanning...")
                for i, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        iframe_links = self.scan_for_quality_links(driver, f"Iframe-{i+1}")
                        all_links.extend(iframe_links)
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()
        except Exception as e:
            print(f"   ⚠️ Iframe scan error: {e}")
        
        return all_links

    async def get_swift(self, hidden):
        d = None
        try:
            if self.st:
                await self.st.update("🚀 **Getting downloading URL...**")
            
            print(f"🚀 Opening hidden link: {hidden[:60]}...")
            d = get_driver()
            d.get(hidden)
            await asyncio.sleep(8)
            
            url = d.current_url
            print(f"   Current URL: {url[:60]}...")
            
            if "multiquality" in url:
                print(f"   ✅ Swift from redirect: {url}")
                return url
            
            if "aipebel" in url or "flash" in url:
                page_source = d.page_source
                m = re.search(r'(https?://[^"\']*swift\.multiquality\.click[^"\']*)', page_source)
                if m:
                    swift_url = m.group(1).replace('\\','')
                    print(f"   ✅ Swift from page source: {swift_url}")
                    return swift_url
            
            print(f"   ℹ️ Using hidden URL for scanning: {hidden[:10]}...")
            return hidden
            
        except Exception as e:
            print(f"❌ get_swift error: {e}")
            traceback.print_exc()
            return None
        finally:
            if d:
                try:
                    d.quit()
                except:
                    pass

# ==========================================
# ANIME FINDER - FIXED VERSION
# ==========================================
class Finder:
    def __init__(self, st=None):
        self.st, self.d = st, None

    def setup(self):
        return get_driver()

    async def get_info(self, url):
        """Fetch series info with PROPER SEASON DETECTION"""
        try:
            if self.st:
                await self.st.update("📂 **Fetching series...**")

            if not self.d:
                self.d = self.setup()

            # ✅ Yahan change kiya hai (Thread mein daal diya)
            await asyncio.to_thread(self.d.get, url)
            await asyncio.sleep(3)

            # ✅ Yahan change kiya hai
            await asyncio.to_thread(WebDriverWait(self.d, 15).until, EC.presence_of_element_located((By.TAG_NAME, "a")))

            # Scroll to load all episodes
            for scroll in range(5):
                # ✅ Yahan change kiya hai
                await asyncio.to_thread(self.d.execute_script, "window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1)

            # ✅ Yahan change kiya hai
            await asyncio.to_thread(self.d.execute_script, "window.scrollTo(0, 0);")
            await asyncio.sleep(1)

            soup = BeautifulSoup(self.d.page_source, 'html.parser')

            # Get title
            title = "Unknown"
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

            # ==========================================
            # 🔥 FIXED: Store (season, episode, url)
            # ==========================================
            eps = []
            seen_keys = set()

            all_links = soup.find_all("a", href=True)
            print(f"🔍 Total links found: {len(all_links)}")

            for a in all_links:
                href = a['href']
                text = a.get_text(" ", strip=True)

                if "/episode/" not in href.lower():
                    continue

                season = 1
                episode = 0

                # PRIMARY: URL format "anime-NxM" (e.g., spy-x-family-3x7)
                season_ep_match = re.search(r'-(\d+)x(\d+)', href)
                if season_ep_match:
                    season = int(season_ep_match.group(1))
                    episode = int(season_ep_match.group(2))

                # FALLBACK: Other formats
                if not episode:
                    se_match = re.search(r'S(\d+)\s*E(\d+)', text, re.I)
                    if se_match:
                        season = int(se_match.group(1))
                        episode = int(se_match.group(2))

                if not episode:
                    m = re.search(r'(?:Episode|Ep|EP|E)[\s\.\-:]*(\d+)', text, re.I)
                    if m:
                        episode = int(m.group(1))

                if not episode:
                    m = re.search(r'-(\d+)/?$', href)
                    if m:
                        episode = int(m.group(1))

                if not episode:
                    m = re.search(r'episode[/\-](\d+)', href, re.I)
                    if m:
                        episode = int(m.group(1))

                # Valid episode mila
                if episode > 0:
                    key = (season, episode)

                    if key not in seen_keys:
                        full_url = href
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                base = '/'.join(url.split('/')[:3])
                                full_url = base + href
                            else:
                                full_url = url.rstrip('/') + '/' + href

                        eps.append((season, episode, full_url))
                        seen_keys.add(key)
                        print(f"   ✅ S{season:02d}E{episode:02d} found")

            if not eps:
                print("❌ No episodes found!")
                return None, None, None, []

            # Sort by season, then episode
            eps.sort(key=lambda x: (x[0], x[1]))

            # Find LAST SEASON's LAST EPISODE
            seasons = {}
            for s, e, u in eps:
                if s not in seasons:
                    seasons[s] = []
                seasons[s].append((e, u))

            last_season = max(seasons.keys())
            last_season_eps = seasons[last_season]
            last_season_eps.sort(key=lambda x: x[0])
            latest_ep = last_season_eps[-1][0]

            print(f"\n{'='*40}")
            print(f"📊 Total Seasons: {len(seasons)}")
            for s in sorted(seasons.keys()):
                print(f"   Season {s}: {len(seasons[s])} episodes")
            print(f"✅ Latest: Season {last_season}, Episode {latest_ep}")
            print(f"{'='*40}\n")

            return title, last_season, latest_ep, eps

        except Exception as e:
            print(f"Finder Error: {e}")
            traceback.print_exc()
            return None, None, None, []
        finally:
            if self.d:
                try:
                    self.d.quit()
                except:
                    pass
                self.d = None

    async def get_latest_from_home(self, url):
        try:
            if self.st:
                await self.st.update("🏠 **Checking home page...**")
            if not self.d:
                self.d = self.setup()
            self.d.get(url)
            WebDriverWait(self.d, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
            soup = BeautifulSoup(self.d.page_source, 'html.parser')
            for a in soup.find_all("a", href=True):
                href = a['href']
                if "/episode/" in href or "/series/" in href:
                    return href
            return None
        except:
            return None
        finally:
            if self.d:
                self.d.quit()
                self.d = None

# ==========================================
# 🎭 RAREANIMES FINDER - WORKING VERSION
# ==========================================
class RareAnimesFinder:
    """Find episodes from RareAnimes/RareToonsIndia website - Based on working Colab code"""
    
    def __init__(self, st=None):
        self.st = st
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    async def get_soup(self, url): # ✅ 'async' add kiya
        try:
            # ✅ Yahan requests.get ko thread mein daal diya
            resp = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=15, verify=False)
            if resp.status_code == 200:
                # ✅ BeautifulSoup parsing ko bhi thread mein daal diya taaki CPU block na ho
                return await asyncio.to_thread(BeautifulSoup, resp.text, 'html.parser')
        except Exception as e:
            print(f"❌ Connection error: {e}")
        return None
    
    async def get_info(self, url):
        """Get series info and episodes - Following Colab logic exactly"""
        try:
            if self.st:
                await self.st.update("🔍 **Scanning RareAnimes...**")
            
            print(f"\n{'='*50}")
            print(f"🎭 RareAnimes Finder")
            print(f"🔗 URL: {url}")
            print(f"{'='*50}")
            
            # ✅ Yahan await lagaya gaya hai
            soup = await self.get_soup(url)
            if not soup:
                print("❌ Website load failed!")
                return None, None, None,[]
            
            # Get title
            title = "Unknown"
            if soup.title:
                raw_title = soup.title.string.strip()
                # Clean title
                title = re.sub(r'\s*[-|]\s*(Rare\s*Toons?\s*India|RareAnimes).*$', '', raw_title, flags=re.I)
                title = re.sub(r'\s*(Hindi\s*Dubbed\s*)?Episodes?\s*Download.*$', '', title, flags=re.I)
                title = title.strip()
            
            # Extract season from URL or title
            season = 1
            season_match = re.search(r'season[- ]?(\d+)', url, re.I)
            if not season_match:
                season_match = re.search(r'season[- ]?(\d+)', raw_title if soup.title else '', re.I)
            if season_match:
                season = int(season_match.group(1))
            
            print(f"🎬 Title: {title}")
            print(f"🏝️ Season: {season}")
            
            if self.st:
                await self.st.update(f"📺 **{title}**\n\n🔍 Finding episodes...")
            
            # Find content div (same as Colab)
            content_div = soup.find('div', class_='entry-content')
            if not content_div:
                content_div = soup.find('div', class_='post-content')
            if not content_div:
                content_div = soup.find('article')
            if not content_div:
                content_div = soup
            
            # ==========================================
            # EPISODE FINDING - EXACT COLAB LOGIC
            # ==========================================
            all_episodes =[]
            all_links = content_div.find_all('a')
            
            keywords =[
                "watchmultiquality", "watchmultquality", "multiquality",
                "multi-quality", "multquality"
            ]
            
            for link in all_links:
                text = link.get_text().strip()
                clean_text = text.lower().replace(" ", "").replace("-", "").replace("_", "")
                href = link.get('href')
                
                if not href:
                    continue
                
                # Check if it's a quality link
                is_quality_link = False
                for keyword in keywords:
                    if keyword.replace("-", "") in clean_text:
                        is_quality_link = True
                        break
                
                if not is_quality_link:
                    continue
                
                # Extract episode number
                ep_num = None
                ep_match = re.search(r'episode[_\s-]*(\d+)|ep[_\s-]*(\d+)|e(\d+)', text, re.IGNORECASE)
                if ep_match:
                    ep_num = int(ep_match.group(1) or ep_match.group(2) or ep_match.group(3))
                
                # Check for Hindi
                has_hindi = 'hindi' in text.lower()
                
                all_episodes.append({
                    'text': text,
                    'url': href,
                    'episode_number': ep_num,
                    'has_hindi': has_hindi
                })
            
            if not all_episodes:
                print("❌ No episodes found!")
                return title, season, None,[]
            
            # Remove duplicates
            seen_urls = set()
            unique_episodes = []
            for ep in all_episodes:
                if ep['url'] not in seen_urls:
                    seen_urls.add(ep['url'])
                    unique_episodes.append(ep)
            
            all_episodes = unique_episodes
            
            print(f"\n✅ Total {len(all_episodes)} episode(s) found")
            
            # Show episodes
            for ep in all_episodes:
                hindi_mark = "🇮🇳" if ep['has_hindi'] else "  "
                ep_mark = f"[EP{ep['episode_number']}]" if ep['episode_number'] else "[???]"
                print(f"   {hindi_mark} {ep_mark} {ep['text'][:50]}...")
            
            # ==========================================
            # SMART SELECTION - EXACT COLAB LOGIC
            # ==========================================
            hindi_episodes = [ep for ep in all_episodes if ep['has_hindi']]
            
            if hindi_episodes:
                numbered_hindi = [ep for ep in hindi_episodes if ep['episode_number'] is not None]
                if numbered_hindi:
                    selected = max(numbered_hindi, key=lambda x: x['episode_number'])
                    print(f"\n🎯 Selection: Highest Hindi Episode (EP{selected['episode_number']})")
                else:
                    selected = hindi_episodes[-1]
                    print(f"\n🎯 Selection: Last Hindi Episode")
            else:
                numbered =[ep for ep in all_episodes if ep['episode_number'] is not None]
                if numbered:
                    selected = max(numbered, key=lambda x: x['episode_number'])
                    print(f"\n🎯 Selection: Highest Episode (EP{selected['episode_number']})")
                else:
                    selected = all_episodes[-1]
                    print(f"\n🎯 Selection: Last Episode")
            
            latest_ep = selected['episode_number'] or len(all_episodes)
            
            print(f"📺 Selected: {selected['text'][:50]}...")
            print(f"🔗 URL: {selected['url'][:60]}...")
            print(f"{'='*50}\n")
            
            # Convert to list format: [(season, episode, url), ...]
            episodes_list = []
            for ep in all_episodes:
                ep_num = ep['episode_number'] or (all_episodes.index(ep) + 1)
                episodes_list.append((season, ep_num, ep['url']))
            
            return title, season, latest_ep, episodes_list
            
        except Exception as e:
            print(f"❌ RareAnimesFinder error: {e}")
            traceback.print_exc()
            return None, None, None,
            
    def resolve_codedew(self, codedew_url):
        """Resolve codedew zipper URL - EXACT COLAB LOGIC (requests only, no Selenium)"""
        print(f"⏳ Resolving Codedew...")
        print(f"🔗 URL: {codedew_url[:60]}...")
        
        soup = self.get_soup(codedew_url)
        if not soup:
            print("❌ Page load failed!")
            return None
        
        # Find mainActionBtn - same as Colab
        download_btn = soup.find('a', id='mainActionBtn')
        if download_btn and download_btn.get('href'):
            link = download_btn['href']
            if "javascript" in link.lower():
                print("❌ JavaScript link (invalid)")
                return None
            
            print(f"✅ Resolved!")
            print(f"🔗 Player URL: {link[:60]}...\n")
            return link
        
        print("❌ Download button not found!")
        return None
    
    async def resolve_codedew_async(self, codedew_url):
        """Async version of resolve_codedew"""
        return self.resolve_codedew(codedew_url)

# ==========================================
# 🇮🇳 HINDIANIMEZONE SUPPORT
# ==========================================

class _DummyMsg:
    """Swallows synchronous edit_text calls from scrap.Scraper internals."""
    def edit_text(self, *a, **kw): pass


class HindiAnimeZoneFinder:
    """Fetch series title + latest episode from a HindiAnimeZone series page."""

    def __init__(self, st=None):
        self.st = st
        self.scraper = _haz_scraper

    async def get_info(self, url):
        """Returns (title, season=1, latest_ep)."""
        if self.st:
            await self.st.update(
                "🇮🇳 **HindiAnimeZone**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔍 Fetching series info..."
            )
        title = await self.scraper.get_page_title(url)
        if self.st:
            await self.st.update(
                f"🇮🇳 **HindiAnimeZone**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 {title}\n"
                f"🔍 Checking latest episode..."
            )
        latest_ep = await self.scraper.check_latest(url)
        return title, 1, latest_ep

    async def resolve_episode_urls(self, ep, url, name):
        """Return dict of {quality: direct_url} for an episode."""
        return await self.scraper.extract_all(ep, url, _DummyMsg(), name)


class HAZDownloader:
    """Async downloader for HAZ direct links (R2 / Pixeldrain)."""

    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36")

    def __init__(self, task, st):
        self.task = task
        self.st = st
        self.dir = task.directory
        os.makedirs(self.dir, exist_ok=True)

    async def download_url(self, url, quality):
        """Download one direct URL → local file path, with progress."""
        try:
            # Build filename
            fname = url.split('/')[-1].split('?')[0]
            if not fname or '.' not in fname:
                fname = f"{self.task.series_name}_Ep{self.task.episode}_{quality}.mkv"
            fname = re.sub(r'[<>:"/\\|?*\[\]]', '_', fname)[:200]
            fpath = os.path.join(self.dir, fname)

            headers = {"User-Agent": self.UA}

            # Pixeldrain → use their API
            if 'pixeldrain.com' in url:
                pid = url.rstrip('/').split('/')[-1]
                url = f"https://pixeldrain.com/api/file/{pid}"
                headers["Referer"] = "https://pixeldrain.com/"

            async with aiohttp.ClientSession(headers=headers) as sess:
                async with sess.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        print(f"❌ HAZ HTTP {resp.status} for {quality}")
                        return None

                    total = int(resp.headers.get('Content-Length', 0))
                    downloaded = 0
                    last_upd = time.time()

                    with open(fpath, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024):
                            if self.task.cancelled:
                                return None
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = time.time()
                            if now - last_upd >= 5 and total > 0:
                                pct = int(downloaded / total * 100)
                                mb  = downloaded / (1024 ** 2)
                                tmb = total / (1024 ** 2)
                                elapsed = now - last_upd
                                spd = (downloaded / elapsed / (1024 ** 2)) if elapsed else 0
                                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                                await self.st.update(
                                    f"📥 **Downloading {quality}...**\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🎬 **{self.task.series_name}**\n"
                                    f"📔 Episode: {self.task.episode}\n\n"
                                    f"[{bar}] {pct}%\n"
                                    f"⬇️ {mb:.1f} / {tmb:.1f} MB\n"
                                    f"⚡ {spd:.2f} MB/s\n"
                                    f"━━━━━━━━━━━━━━━━━━━━━━"
                                )
                                last_upd = now

            if os.path.exists(fpath) and os.path.getsize(fpath) > 100 * 1024:
                print(f"✅ HAZ downloaded: {fname} ({os.path.getsize(fpath)//1024}KB)")
                return fpath
            print(f"❌ HAZ file too small / missing: {fpath} ({os.path.getsize(fpath) if os.path.exists(fpath) else 0} bytes)")
            return None

        except Exception as e:
            print(f"❌ HAZDownloader.download_url [{quality}]: {e}")
            return None

    async def download_all(self, quality_urls):
        """Download all qualities, return list of local paths."""
        files = []
        total_q = len(quality_urls)
        for idx, (quality, url) in enumerate(quality_urls.items(), 1):
            await self.st.update(
                f"📥 **HAZ Download ({idx}/{total_q})**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 **{self.task.series_name}**\n"
                f"📔 Episode: {self.task.episode}\n"
                f"🎞️ Quality: {quality}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━",
                force=True
            )
            fpath = await self.download_url(url, quality)
            if fpath:
                files.append(fpath)
        return files


# ==========================================
# 🔗 CODEDEW RESOLVER - REFERENCE CODE EXACT COPY
# ==========================================
# ==========================================
# 🌏 TOONWORLD4ALL SUPPORT
# ==========================================

class ToonWorld4AllFinder:
    """Find episodes and title from a ToonWorld4All series page."""

    UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36")

    def __init__(self, st=None):
        self.st = st
        self.headers = {"User-Agent": self.UA}

    async def _get_soup(self, url):
        try:
            resp = await asyncio.to_thread(
                requests.get, url, headers=self.headers, timeout=20
            )
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            print(f"❌ TW4ALL fetch error: {e}")
        return None

    def _get_props(self, html):
        """Extract window.__PROPS__ JSON from archive page HTML."""
        import re as _re
        m = _re.search(r'window\.__PROPS__\s*=\s*(.*?)\s*;\s*\n', html, _re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        return None

    async def get_info(self, url):
        """Returns (title, season, latest_ep) from a series page."""
        if self.st:
            await self.st.update(
                "🌏 **ToonWorld4All**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔍 Fetching series info..."
            )

        soup = await self._get_soup(url)
        if not soup:
            return None, 1, None

        # Extract title
        title = "Unknown"
        if soup.title:
            raw = soup.title.string.strip()
            # Remove site name suffix
            import re as _re
            title = _re.sub(r'\s*[|\-–]\s*ToonWorld4All.*$', '', raw, flags=_re.I)
            # Remove "Download" prefix
            title = _re.sub(r'^Download\s+', '', title, flags=_re.I)
            # Remove quality/format tags at end
            title = _re.sub(r'\s+\d{3,4}p.*$', '', title)
            title = title.strip()

        # Extract season
        season = 1
        import re as _re
        sm = _re.search(r'[Ss]eason\s*(\d+)', url + title)
        if sm:
            season = int(sm.group(1))

        if self.st:
            await self.st.update(
                f"🌏 **ToonWorld4All**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 {title}\n"
                f"🔍 Scanning episodes..."
            )

        # Find episode links in content div
        content = (soup.find('div', class_='entry-content')
                   or soup.find('div', class_='post-content')
                   or soup.find('article')
                   or soup)

        episodes = []
        for a in content.find_all('a', href=True):
            href = a['href']
            # episode links: archive.toonworld4all.me/episode/slug-SxE
            if 'archive.toonworld4all' in href and '/episode/' in href:
                # parse SxE from slug
                ep_m = _re.search(r'-(\d+)x(\d+)$', href.rstrip('/'))
                if ep_m:
                    s = int(ep_m.group(1))
                    e = int(ep_m.group(2))
                else:
                    ep_m2 = _re.search(r'(\d+)x(\d+)', href)
                    if ep_m2:
                        s = int(ep_m2.group(1))
                        e = int(ep_m2.group(2))
                    else:
                        continue
                episodes.append((s, e, href))

        if not episodes:
            return title, season, None

        episodes.sort(key=lambda x: (x[0], x[1]))
        latest = episodes[-1]
        return title, latest[0], latest[1]

    async def resolve_episode_urls(self, ep, series_url, series_name):
        """Return dict of {quality_label: direct_url} for an episode."""
        import re as _re

        # If series URL given, find the archive URL for this episode
        archive_url = None
        if 'archive.toonworld4all' in series_url and '/episode/' in series_url:
            archive_url = series_url
        else:
            soup = await self._get_soup(series_url)
            if not soup:
                return {}
            content = (soup.find('div', class_='entry-content')
                       or soup.find('article')
                       or soup)
            for a in content.find_all('a', href=True):
                href = a['href']
                if 'archive.toonworld4all' in href and '/episode/' in href:
                    ep_m = _re.search(r'(\d+)x(\d+)', href)
                    if ep_m and int(ep_m.group(2)) == ep:
                        archive_url = href
                        break
            if not archive_url:
                # Fallback: just take the latest
                for a in content.find_all('a', href=True):
                    href = a['href']
                    if 'archive.toonworld4all' in href and '/episode/' in href:
                        archive_url = href

        if not archive_url:
            print(f"❌ TW4ALL: No archive URL found for ep {ep}")
            return {}

        print(f"📡 TW4ALL archive URL: {archive_url}")

        # Fetch archive episode page
        try:
            resp = await asyncio.to_thread(
                requests.get, archive_url, headers=self.headers, timeout=20
            )
            if resp.status_code != 200:
                print(f"❌ TW4ALL archive HTTP {resp.status_code}")
                return {}
            html = resp.text
        except Exception as e:
            print(f"❌ TW4ALL archive fetch: {e}")
            return {}

        props = self._get_props(html)
        if not props:
            print("❌ TW4ALL: No __PROPS__ found in archive page")
            return {}

        encodes = props.get('data', {}).get('data', {}).get('encodes', [])
        if not encodes:
            print("❌ TW4ALL: No encodes in props")
            return {}

        print(f"✅ TW4ALL: Found {len(encodes)} encode options")

        quality_urls = {}
        preferred_hosts = ['FilePress', 'filepress', 'MEGA', 'mega', 'AppDrive', 'appdrive']

        for encode in encodes:
            label = encode.get('readable', {}).get('codec', encode.get('resolution', 'Unknown'))
            files = encode.get('files', [])
            if not files:
                continue

            # Pick best host (prefer FilePress)
            chosen_file = None
            for host_pref in preferred_hosts:
                for f in files:
                    if host_pref.lower() in f.get('host', '').lower():
                        chosen_file = f
                        break
                if chosen_file:
                    break
            if not chosen_file:
                chosen_file = files[0]

            redirect_path = chosen_file.get('link', '')
            if not redirect_path:
                continue

            # Build full redirect URL
            if redirect_path.startswith('/'):
                redirect_url = f"https://archive.toonworld4all.me{redirect_path}"
            else:
                redirect_url = redirect_path

            # Call redirect API with Referer
            try:
                redir_headers = dict(self.headers)
                redir_headers['Referer'] = archive_url
                redir_resp = await asyncio.to_thread(
                    requests.get, redirect_url, headers=redir_headers, timeout=15
                )
                redir_html = redir_resp.text
                redir_props = self._get_props(redir_html)
                if redir_props and 'link' in redir_props:
                    link_data = redir_props['link']
                    domain = link_data.get('domain', '')
                    hidden = link_data.get('hidden', '')
                    if domain and hidden:
                        dl_url = domain.rstrip('/') + '/' + hidden
                        quality_urls[label] = dl_url
                        print(f"   ✅ {label}: {dl_url[:60]}...")
                    else:
                        print(f"   ⚠️ {label}: incomplete link data")
                else:
                    print(f"   ⚠️ {label}: no redirect props")
            except Exception as e:
                print(f"   ❌ {label} redirect error: {e}")

        return quality_urls


class SmartCodedewResolver:
    """
    EXACT same logic as reference code:
    Step 1: codedew/zipper/?url=xxx → HTML parse → next zipper URL
    Step 2: codedew/zipper/?url=yyy → HTML parse → zipper with ad_step
    Step 3: codedew/zipper/?url=yyy&ad_step=2 → HTML parse → cdn/ziptron
    Step 4: cdn/ziptron.php/?xxx → FINAL!
    """
    
    def __init__(self, st=None):
        self.st = st
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False
    
    def resolve_one_step(self, url, step_number):
        """
        EXACT COPY of reference code's resolve_zipper_link()
        - Requests se HTML lo
        - Meta redirect check karo
        - First valid <a> link lo
        - Return karo
        """
        print(f"\n   [STEP {step_number}] 🔍 Codedew URL ke andar ghus raha hoon...")
        print(f"   URL: {url[:70]}...")
        
        try:
            # ✅ allow_redirects=False taki har redirect separately handle ho
            response = self.session.get(url, timeout=20, allow_redirects=False)
            
            # ==========================================
            # CASE 1: Server Redirect (301/302)
            # ==========================================
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location:
                    next_url = urllib.parse.urljoin(url, location)
                    print(f"   ➡️ Server Redirect ({response.status_code})")
                    print(f"   🔗 URL {step_number}: {next_url[:70]}...")
                    
                    # ✅ If redirect goes to multiquality, we need its HTML
                    # So follow ONE more redirect to get the actual page
                    if 'multiquality' in next_url:
                        print(f"   📄 Multiquality detected, getting HTML...")
                        return self._parse_page_for_link(next_url, step_number)
                    
                    return next_url
            
            # ==========================================
            # CASE 2: 200 OK - Parse HTML (Reference Code Logic)
            # ==========================================
            return self._parse_page_for_link(url, step_number, response=response)
            
        except Exception as e:
            print(f"   ❌ STEP {step_number} ERROR: {e}")
            return None
    
    def _parse_page_for_link(self, url, step_number, response=None):
        """Parse HTML and find next link - EXACT reference code logic"""
        try:
            if response is None:
                response = self.session.get(url, timeout=20)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            landed_url = response.url if hasattr(response, 'url') else url
            
            print(f"   📄 Parsing HTML of: {landed_url[:60]}...")
            
            # ==========================================
            # 1. Meta Redirect Check (Reference Code)
            # ==========================================
            meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('^refresh$', re.I)})
            if meta_refresh:
                content = meta_refresh.get('content', '')
                if 'url=' in content.lower():
                    meta_url = content.split('url=')[-1].strip().strip('"').strip("'")
                    full_url = urllib.parse.urljoin(landed_url, meta_url)
                    
                    display = "Auto-Redirect"
                    if 'ad_step' in full_url:
                        display = "Scanning..."
                    elif 'cdn/ziptron' in full_url:
                        display = "Finalizing..."
                    
                    print(f"   ✅ STEP {step_number} SUCCESS ({display})")
                    print(f"   🔗 URL {step_number}: {full_url[:70]}...")
                    return full_url
            
            # ==========================================
            # 2. mainActionBtn (Codedew Specific)
            # ==========================================
            action_btn = soup.find('a', id='mainActionBtn')
            if action_btn and action_btn.get('href'):
                href = action_btn['href']
                if href and href != '#' and 'javascript' not in href.lower():
                    full_href = urllib.parse.urljoin(landed_url, href)
                    print(f"   ✅ STEP {step_number} SUCCESS (ActionBtn)")
                    print(f"   🔗 URL {step_number}: {full_href[:70]}...")
                    return full_href
            
            # ==========================================
            # 3. Manual Link Check (Reference Code)
            # ==========================================
            # Priority 1: Find cdn/ziptron link
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'cdn/ziptron' in href:
                    full_href = urllib.parse.urljoin(landed_url, href)
                    print(f"   ✅ STEP {step_number} SUCCESS (cdn/ziptron found!)")
                    print(f"   🔗 URL {step_number}: {full_href[:70]}...")
                    return full_href
            
            # Priority 2: Find codedew zipper link
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if not href or href == '#' or 'javascript' in href.lower():
                    continue
                
                full_href = urllib.parse.urljoin(landed_url, href)
                
                # Skip same URL
                if full_href.rstrip('/') == url.rstrip('/'):
                    continue
                if full_href.rstrip('/') == landed_url.rstrip('/'):
                    continue
                
                # Skip social/ads
                skip = ['facebook', 'twitter', 'instagram', 'google.com/ads',
                        'desidubanime', 'ads.', 'tracker']
                if any(s in full_href.lower() for s in skip):
                    continue
                
                # Prefer codedew URLs
                if 'codedew.com' in full_href:
                    display = text[:20] if text else "Button"
                    print(f"   ✅ STEP {step_number} SUCCESS (Found: {display})")
                    print(f"   🔗 URL {step_number}: {full_href[:70]}...")
                    return full_href
            
            # Priority 3: Any valid link (Reference Code Fallback)
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if not href or href == '#' or 'javascript' in href.lower():
                    continue
                
                full_href = urllib.parse.urljoin(landed_url, href)
                
                if full_href.rstrip('/') == url.rstrip('/'):
                    continue
                if full_href.rstrip('/') == landed_url.rstrip('/'):
                    continue
                
                skip = ['facebook', 'twitter', 'instagram', 'ads.',
                        'desidubanime', 'tracker']
                if any(s in full_href.lower() for s in skip):
                    continue
                
                display = text[:20] if text else "Button"
                print(f"   ✅ STEP {step_number} SUCCESS (Found: {display})")
                print(f"   🔗 URL {step_number}: {full_href[:70]}...")
                return full_href
            
            print(f"   ❌ STEP {step_number} FAIL: Koi link nahi mila")
            return None
            
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
            return None
    
    async def resolve(self, initial_url):
        """
        Run steps until cdn/ziptron found
        EXACT flow: zipper → zipper → zipper+ad_step → cdn/ziptron
        """
        print(f"\n{'='*60}")
        print(f"🔗 CODEDEW RESOLVER (Reference Method)")
        print(f"{'='*60}")
        
        if self.st:
            await self.st.update("🔗 **Resolving step by step...**")
        
        current_url = initial_url
        visited = set()
        max_steps = 10
        
        for step in range(1, max_steps + 1):
            # ✅ CHECK: Already at FINAL?
            if 'cdn/ziptron' in current_url:
                print(f"\n{'='*60}")
                print(f"🎉 FINAL DESTINATION URL MIL GAYI 🎉")
                print(f"🎯 Target Link: {current_url}")
                print(f"{'='*60}")
                return current_url
            
            # ✅ LOOP DETECTION
            # ad_step URLs are allowed to repeat base
            if 'ad_step' in current_url:
                check_key = current_url  # Full URL with ad_step
            else:
                check_key = current_url.split('?')[0]  # Base URL only
            
            if check_key in visited:
                print(f"\n   🔄 LOOP DETECTED at step {step}!")
                print(f"   URL already visited: {current_url[:60]}...")
                print(f"   Switching to Selenium method...")
                return None
            visited.add(check_key)
            
            if self.st:
                await self.st.update(f"🔗 **Step {step}/10...**")
            
            # Resolve next step
            next_url = self.resolve_one_step(current_url, step)
            
            if not next_url:
                print(f"\n   ❌ Resolution stopped at step {step}")
                return None
            
            # ✅ CHECK: Got FINAL?
            if 'cdn/ziptron' in next_url:
                print(f"\n{'='*60}")
                print(f"🎉 FINAL DESTINATION URL MIL GAYI 🎉")
                print(f"🎯 Target Link: {next_url}")
                print(f"{'='*60}")
                return next_url
            
            # ✅ CHECK: Same URL returned?
            if next_url.rstrip('/') == current_url.rstrip('/'):
                print(f"   🔄 Same URL returned at step {step}")
                return None
            
            current_url = next_url
            await asyncio.sleep(0.5)
        
        print(f"   ⚠️ Max {max_steps} steps reached without cdn/ziptron")
        return None

# ==========================================
# DOWNLOADER WITH ARIA2 (COOKIE FILE MODE - STABLE)
# ==========================================
class Downloader:
    def __init__(self, task, st=None):
        self.task = task
        self.st = st
        self.dir = task.directory

    def popups(self, d, m):
        try:
            if len(d.window_handles) > 1:
                for h in d.window_handles:
                    if h != m:
                        d.switch_to.window(h)
                        d.close()
                d.switch_to.window(m)
        except:
            pass

    def save_cookies_netscape(self, cookies, path):
        """Save cookies in Netscape format for Aria2"""
        with open(path, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                domain = cookie.get('domain', '')
                if not domain.startswith('.'): domain = '.' + domain
                path_val = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure') else 'FALSE'
                expires = str(int(cookie.get('expiry', time.time() + 3600)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                f.write(f"{domain}\tTRUE\t{path_val}\t{secure}\t{expires}\t{name}\t{value}\n")

    async def download_with_aria2(self, url, cookie_file, referer, user_agent, quality, num, total):
        """Download with server filename + auto cleanup + better error handling"""
        start_time = time.time()
        max_download_time = 1800  # 30 minutes max per file
        est = {"1080p":220,"720p":90,"480p":55,"360p":40}.get(quality,100) * 1024 * 1024

        cmd = [
            "aria2c",
            "-x", "8", "-s", "8", "-k", "1M",
            "-d", self.dir,
            "--load-cookies", cookie_file,
            "--user-agent", user_agent,
            "--referer", referer,
            "--header", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "--header", "Accept-Language: en-US,en;q=0.9",
            "--header", "Sec-Fetch-Site: same-site",
            "--header", "Upgrade-Insecure-Requests: 1",
            "--check-certificate=false",
            "--console-log-level=warn",
            "--file-allocation=none",
            "--summary-interval=0",
            "--timeout=60",           # 🔥 NEW: Connection timeout
            "--connect-timeout=30",   # 🔥 NEW: Initial connect timeout
            "--max-tries=5",          # 🔥 NEW: Aria2 internal retries
            "--retry-wait=3",         # 🔥 NEW: Wait between retries
            url
        ]

        before_files = set(os.listdir(self.dir)) if os.path.exists(self.dir) else set()

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        # ✅ Store process reference for cancel
        self.task.active_process = process

        last_size = 0
        last_time = time.time()

        while process.returncode is None:
            await asyncio.sleep(1)

            # ✅ CANCEL CHECK
            if self.task.cancelled:
                print(f"      ❌ CANCELLED by user!")
                try:
                    process.terminate()
                    await asyncio.sleep(1)
                    process.kill()
                except:
                    pass
                self.task.active_process = None
                # Cleanup partial files
                after_cancel = set(os.listdir(self.dir)) if os.path.exists(self.dir) else set()
                for f in after_cancel - before_files:
                    try:
                        os.remove(os.path.join(self.dir, f))
                    except:
                        pass
                return None

            # 🔥 NEW: Check for timeout
            if time.time() - start_time > max_download_time:
                print(f"      ⏰ Download timeout for {quality}")
                try:
                    process.terminate()
                except:
                    pass
                return None

            current_file = None
            current_size = 0

            for f in os.listdir(self.dir):
                if f not in before_files and not f.endswith('.aria2') and f != "cookies.txt":
                    fp = os.path.join(self.dir, f)
                    if os.path.isfile(fp):
                        try:
                            sz = os.path.getsize(fp)
                            if sz > current_size:
                                current_size = sz
                                current_file = f
                        except:
                            pass

            if current_file and current_size > 0:
                now = time.time()
                
                speed = (current_size - last_size) / max(1, now - last_time)
                last_size = current_size
                last_time = now

                if current_size > est * 0.9:
                    est = int(current_size * 1.2)

                pct = min((current_size / est) * 100, 99)
                eta = (est - current_size) / speed if speed > 0 else 0

                bar = progress_bar(pct)
                
                # ✅ REPLACE: Progress update block inside download_with_aria2
                if self.st:
                    # Source URL display (truncated)
                    source_url = self.task.swift_url or url
                    if len(source_url) > 45:
                        url_display = source_url[:42] + "..."
                    else:
                        url_display = source_url
                    
                    # Clean anime name
                    clean_series = clean_anime_name(self.task.series_name)
                    if not clean_series or clean_series in ["Unknown", ""]:
                        clean_series = self.task.series_name
                    
                    # Episode/Season
                    ep_display = self.task.episode or 'N/A'
                    season_display = getattr(self.task, 'season', None) or 'N/A'
                    
                    # Batch info
                    batch_line = ""
                    if self.task.batch_mode:
                        batch_line = f"\n📑 Batch: Ep {self.task.current_episode}/{self.task.total_episodes}"

                    await self.st.update(f"""
📥 **Downloading...**
🔗 `{url_display}`

🎬 **{clean_series}**
🏝️ Season: {season_display}
📔 Episode: {ep_display}
🎥 Quality: {quality.upper()}
🎙️ Language: Detecting...

{bar} **{pct:.1f}%**

📦 {fmt_bytes(current_size)} / {fmt_bytes(est)}
⚡ {fmt_bytes(speed)}/s | ⏱️ {fmt_time(eta)}

📊 Downloading {num}/{total} qualities{batch_line}

❌ Cancel: `/cancel {self.task.cancel_id}`
""")
                    
            try:
                await asyncio.wait_for(asyncio.shield(process.wait()), timeout=0.1)
            except asyncio.TimeoutError:
                pass

        # ✅ Clear process reference
        self.task.active_process = None

        await process.wait()

        # 🔥 FIX 1: Check if aria2c download was 100% successful
        if process.returncode != 0:
            print(f"   ❌[Error] Download incomplete (Aria2c code: {process.returncode})")
            for f in os.listdir(self.dir):
                if f not in before_files and f != "cookies.txt":
                    try: os.remove(os.path.join(self.dir, f))
                    except: pass
            return None

        after_files = set(os.listdir(self.dir))
        new_files = after_files - before_files

        # Check for lingering .aria2 files
        incomplete_files = set()
        for f in os.listdir(self.dir):
            if f.endswith('.aria2'):
                incomplete_files.add(f[:-6])

        for f in list(new_files):
            if f.endswith('.aria2'):
                new_files.discard(f)
                try: os.remove(os.path.join(self.dir, f))
                except: pass
            elif f in incomplete_files:
                # Delete adhoori files
                new_files.discard(f)
                try: os.remove(os.path.join(self.dir, f))
                except: pass

        if new_files:
            largest = None
            largest_size = 0
            
            for f in new_files:
                if f == "cookies.txt":
                    continue
                fp = os.path.join(self.dir, f)
                try:
                    sz = os.path.getsize(fp)
                    if sz > largest_size:
                        largest_size = sz
                        largest = fp
                except: pass
            
            if largest and largest_size > 1024:
                original_name = os.path.basename(largest)
                clean_name = clean_unwanted_tags(original_name)
                
                # ✅ Ensure .mp4 extension
                video_exts = ['.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv']
                for ext in video_exts:
                    if clean_name.lower().endswith(ext):
                        clean_name = clean_name[:-len(ext)] + '.mp4'
                        break
                
                if not clean_name.lower().endswith('.mp4'):
                    clean_name = clean_name + '.mp4'
                
                clean_path = os.path.join(self.dir, clean_name)
                
                if original_name != clean_name:
                    try:
                        os.rename(largest, clean_path)
                        print(f"      📂 Original: {original_name}")
                        print(f"      ✨ Cleaned:  {clean_name}")
                        largest = clean_path
                    except: pass
                
                return largest

        return None

    async def download(self, swift):
        """Download with CORRECT retry URL + skip downloaded qualities"""
        d = None
        files = []
        downloaded_qualities = set()
        
        # ✅ FIX 1: ALWAYS use this URL for ALL retries
        original_swift_url = swift
        
        print(f"[{self.task.task_id}] Target: {swift}")

        try:
            if self.st:
                await self.st.update("🔍 **Finding download links...**")

            max_quality_retries = 3
            wait_times = [5, 7, 9]
            
            for quality_attempt in range(max_quality_retries):
                print(f"\n   🔄 Scan attempt {quality_attempt + 1}/{max_quality_retries}")
                
                service = Service(CHROMEDRIVER_PATH)
                opts = get_chrome_options()
                opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                d = webdriver.Chrome(service=service, options=opts)
                d.set_page_load_timeout(60)
                
                cookie_file = os.path.join(self.dir, "cookies.txt")
                found_links = []
                
                try:
                    # ✅ FIX 2: ALWAYS open original URL (with full params)
                    print(f"   🌐 Opening: {original_swift_url[:60]}...")
                    d.get(original_swift_url)
                    
                    wait_time = wait_times[quality_attempt]
                    print(f"   ⏳ Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    
                    main_window = d.current_window_handle
                    self.popups(d, main_window)
                    
                    current_url = d.current_url
                    print(f"   📍 Browser at: {current_url[:60]}...")
                    
                    # Skip wrong redirects
                    if "rareanimes.app" in current_url or "raretoonsindia" in current_url:
                        print(f"   ⚠️ Wrong redirect!")
                        d.quit()
                        d = None
                        continue
                    
                    user_agent = d.execute_script("return navigator.userAgent")
                    cookies = d.get_cookies()
                    self.save_cookies_netscape(cookies, cookie_file)
                    
                    # ==========================================
                    # SCAN MAIN PAGE
                    # ==========================================
                    for link in d.find_elements(By.TAG_NAME, "a"):
                        try:
                            text = (link.text or "").strip().lower()
                            href = link.get_attribute("href") or ""
                            if not href or "javascript" in href.lower():
                                continue
                            if "rareanimes" in href or "raretoonsindia" in href:
                                continue
                            
                            check = text + " " + href.lower()
                            quality = None
                            
                            if "1080" in check or "fhd" in check:
                                quality = "1080p"
                            elif "720" in check:
                                quality = "720p"
                            elif "480" in check:
                                quality = "480p"
                            elif "360" in check:
                                quality = "360p"
                            
                            # ✅ FIX 3: Skip already downloaded
                            if quality and quality not in downloaded_qualities:
                                if href not in [x[1] for x in found_links]:
                                    found_links.append((quality, href))
                                    print(f"      ✅ {quality}: {href[:50]}")
                        except:
                            pass
                    
                    # ==========================================
                    # SCAN IFRAMES
                    # ==========================================
                    try:
                        iframes = d.find_elements(By.TAG_NAME, "iframe")
                        for i, iframe in enumerate(iframes):
                            try:
                                d.switch_to.frame(iframe)
                                await asyncio.sleep(2)
                                
                                for link in d.find_elements(By.TAG_NAME, "a"):
                                    try:
                                        text = (link.text or "").strip().lower()
                                        href = link.get_attribute("href") or ""
                                        if not href or "javascript" in href.lower():
                                            continue
                                        
                                        check = text + " " + href.lower()
                                        quality = None
                                        
                                        if "1080" in check:
                                            quality = "1080p"
                                        elif "720" in check:
                                            quality = "720p"
                                        elif "480" in check:
                                            quality = "480p"
                                        elif "360" in check:
                                            quality = "360p"
                                        
                                        # ✅ Skip already downloaded
                                        if quality and quality not in downloaded_qualities:
                                            if href not in [x[1] for x in found_links]:
                                                found_links.append((quality, href))
                                                print(f"      [Iframe] ✅ {quality}")
                                    except:
                                        pass
                                
                                d.switch_to.default_content()
                            except:
                                d.switch_to.default_content()
                    except:
                        pass
                    
                    d.quit()
                    d = None
                    
                    # ==========================================
                    # DOWNLOAD FOUND QUALITIES
                    # ==========================================
                    if not found_links:
                        print(f"   ⚠️ No NEW qualities found")
                        if quality_attempt < max_quality_retries - 1:
                            await asyncio.sleep(3)
                        continue
                    
                    # Remove duplicates
                    unique = {}
                    for q, u in found_links:
                        if q not in unique:
                            unique[q] = u
                    
                    found_links = [(q, u) for q, u in unique.items()]
                    quality_order = {"360p": 1, "480p": 2, "720p": 3, "1080p": 4}
                    found_links.sort(key=lambda x: quality_order.get(x[0], 5))
                    
                    print(f"   📊 New: {[x[0] for x in found_links]}")
                    print(f"   ✅ Done: {downloaded_qualities}")
                    
                    self.task.swift_url = original_swift_url
                    
                    for i, (quality, link) in enumerate(found_links, 1):
                        # ✅ FIX 4: Double-check skip
                        if quality in downloaded_qualities:
                            print(f"   ⏭️ Skip {quality} (already done)")
                            continue
                        
                        print(f"\n   📥 {quality}...")
                        
                        for dl_attempt in range(3):
                            try:
                                f = await self.download_with_aria2(
                                    link, cookie_file,
                                    original_swift_url,  # ✅ Use original URL as referer
                                    user_agent,
                                    quality, i, len(found_links)
                                )
                                
                                if f and os.path.exists(f) and os.path.getsize(f) > 10240:
                                    files.append(f)
                                    downloaded_qualities.add(quality)
                                    print(f"   ✅ {quality} done!")
                                    break
                                else:
                                    print(f"   ⚠️ {quality} attempt {dl_attempt + 1} failed")
                                    if dl_attempt < 2:
                                        await asyncio.sleep(3)
                            except Exception as e:
                                print(f"   ❌ {quality} error: {e}")
                        
                        await asyncio.sleep(2)
                    
                    # Check missing
                    expected = {'360p', '480p', '720p', '1080p'}
                    missing = expected - downloaded_qualities
                    
                    if not missing:
                        print(f"   ✅ ALL qualities done!")
                        break
                    else:
                        print(f"   ⚠️ Missing: {missing}")
                        if quality_attempt < max_quality_retries - 1:
                            print(f"   🔄 Will retry with: {original_swift_url[:50]}...")
                    
                except Exception as e:
                    print(f"   ❌ Attempt {quality_attempt + 1} error: {e}")
                    traceback.print_exc()
                    if d:
                        try:
                            d.quit()
                        except:
                            pass
                        d = None
            
            # Cleanup
            if os.path.exists(cookie_file):
                try:
                    os.remove(cookie_file)
                except:
                    pass
            
            self.task.files = files
            print(f"   🎉 Total: {len(files)} files, Done: {downloaded_qualities}")
            return files

        except Exception as e:
            print(f"[{self.task.task_id}] ❌ CRITICAL: {e}")
            traceback.print_exc()
            return files
        finally:
            if d:
                try:
                    d.quit()
                except:
                    pass

# ==========================================
# 📤 UPLOADER - COMPLETE CLASS (ALL FEATURES)
# ==========================================
class Uploader:
    """
    Complete Uploader with:
    - User DM first → Channel forward
    - Beautiful progress with all details
    - Audio filtering for channels
    - DM/Channel status tracking
    - Clean anime name in caption
    """

    def __init__(self, c, st, task):
        self.c = c
        self.st = st
        self.task = task
        
        # Progress tracking
        self.start = None
        self.last = 0
        self.name = ""
        self.num = 0
        self.total = 0
        
        # File details
        self.current_quality = "Unknown"
        self.current_language = "Unknown"
        self.current_season = "N/A"
        self.current_episode = "N/A"
        
        # DM/Channel status
        self.dm_done = False
        self.channel_done = False
        self.channel_total = 0
        self.channel_completed = 0
        self.is_uploading_to_channel = False
        self.channel_name = ""
        self.channel_id = ""

    # ==========================================
    # 📊 PROGRESS BAR
    # ==========================================
    async def prog(self, cur, tot):
        """Beautiful progress with DM/Channel status"""
        if not self.start:
            self.start = time.time()
        el = time.time() - self.start
        spd = cur / el if el > 0 else 0
        pct = (cur / tot * 100) if tot > 0 else 0
        eta = (tot - cur) / spd if spd > 0 else 0
        now = time.time()

        if now - self.last >= PROGRESS_UPDATE_INTERVAL:
            bar = progress_bar(pct)

            # Batch info
            batch_line = ""
            if self.task.batch_mode:
                batch_line = f"\n📑 Batch: Episode {self.task.current_episode}/{self.task.total_episodes}"

            # DM status icon
            dm_icon = "✅" if self.dm_done else "⏳"

            # Channel status + name
            if self.channel_total > 0:
                if self.channel_completed >= self.channel_total:
                    channel_line = "\n🗄️ Channel: ✅"
                elif self.is_uploading_to_channel:
                    channel_line = f"\n🗄️ Channel: ⏳"
                    channel_line += f"\n📛 {self.channel_name} (`{self.channel_id}`)"
                else:
                    channel_line = "\n🗄️ Channel: ❌"
            else:
                channel_line = "\n🗄️ Channel: ➖ (Not Set)"

            # Header and target
            if self.is_uploading_to_channel:
                upload_header = "📤 **Uploading to Channel...**"
                target_line = f"🗄️ → {self.channel_name}"
            else:
                upload_header = "📤 **Uploading to DM...**"
                target_line = "👤 → Your DM"

            await self.st.update(f"""
{upload_header}

🎬 **{self.name}**
🏝️ Season: {self.current_season}
📔 Episode: {self.current_episode}
🎥 Quality: {self.current_quality}
🎙️ Language: {self.current_language}
👤 DM: {dm_icon}{channel_line}

{bar} **{pct:.1f}%**

📦 {fmt_bytes(cur)} / {fmt_bytes(tot)}
⚡ {fmt_bytes(spd)}/s | ⏱️ {fmt_time(eta)}

📊 Quality {self.num}/{self.total} | {target_line}{batch_line}

❌ Cancel: `/cancel {self.task.cancel_id}`
""")
            self.last = now

    # ==========================================
    # 🔧 HELPER FUNCTIONS
    # ==========================================
    def _get_file_details(self, filepath):
        """Get quality, language, season, episode from file"""
        raw = os.path.basename(filepath)
        
        quality = get_real_quality(filepath)
        language = get_audio_language(filepath)
        if not language or language == "Unknown":
            language = "Detecting..."
        
        season, episode = extract_season_episode_from_filename(raw)
        if not season or not episode:
            info = parse_filename(raw)
            if not season:
                season = info.get('season')
            if not episode:
                episode = info.get('episode')
        
        return {
            'quality': quality or "Unknown",
            'language': language,
            'season': season or 'N/A',
            'episode': episode or self.task.episode or 'N/A'
        }

    def _get_channel_language_display(self, languages):
        """Hindi+Tamil → Hindi, Tamil"""
        if languages.lower() == 'all':
            return "All Audio"
        return ', '.join(l.strip().capitalize() for l in languages.replace('+', ',').split(','))

    # ==========================================
    # 📤 UPLOAD TO USER (DM) - MAIN METHOD
    # ==========================================
    async def upload_to_user(self, cid, path, anime, thumb_id=None):
        """
        Upload to user DM first
        Returns: (success, user_message)
        """
        global upload_semaphore

        async with upload_semaphore:
            try:
                # ==========================================
                # VALIDATE FILE
                # ==========================================
                is_valid, reason = validate_file(path)
                if not is_valid:
                    print(f"   ❌ Invalid file: {reason}")
                    return False, None

                sz = os.path.getsize(path)
                raw = os.path.basename(path)
                dur, w, h = video_info(path)

                # ==========================================
                # CLEAN FILENAME & DISPLAY NAME
                # ==========================================
                clean_file = clean_unwanted_tags(raw, cid)
                clean_file = re.sub(r'\.(mp4|mkv|avi|webm)$', '', clean_file, flags=re.I)

                display_name = clean_anime_name(clean_file)
                if not display_name or display_name in ["Unknown", "Direct Download", "Download", ""]:
                    display_name = clean_anime_name(anime)
                if not display_name or display_name in ["Unknown", ""]:
                    display_name = anime

                # ==========================================
                # SET PROGRESS TRACKING INFO
                # ==========================================
                details = self._get_file_details(path)
                self.name = display_name
                self.current_quality = details['quality']
                self.current_language = details['language']
                self.current_season = details['season']
                self.current_episode = details['episode']
                self.dm_done = False
                self.is_uploading_to_channel = False
                self.start = time.time()
                self.last = 0

                # Count matching channels for status display
                user_channels = db.get('channels', {}).get(cid, [])
                self.channel_total = sum(
                    1 for ch in user_channels
                    if SequenceMatcher(None, anime.lower(), ch['anime'].lower()).ratio() >= 0.67
                )
                self.channel_completed = 0
                self.channel_done = False

                # ==========================================
                # THUMBNAIL
                # ==========================================
                thumb = None
                
                # Custom thumbnail from user
                if thumb_id:
                    tp = os.path.join(THUMB_DIR, f"dl_{cid}_{int(time.time())}.jpg")
                    try:
                        await self.c.download_media(thumb_id, file_name=tp)
                        if os.path.exists(tp) and os.path.getsize(tp) > 0:
                            thumb = tp
                    except Exception as e:
                        print(f"   ⚠️ Thumb download failed: {e}")

                # Auto-generate from video
                if not thumb:
                    tp = os.path.join(THUMB_DIR, f"auto_{self.task.task_id}_{int(time.time())}.jpg")
                    thumb = make_thumb(path, tp)

                # ==========================================
                # METADATA TAG
                # ==========================================
                final_path = path
                upload_filename = display_name

                if cid in db.get('metadata', {}):
                    user_meta = db['metadata'][cid]
                    tag = user_meta.get('tag', '')
                    if tag:
                        print(f"   🏷️ Applying metadata: [{tag}]")
                        final_path = await apply_metadata(
                            path, tag, clean_file,
                            season=details['season'] if details['season'] != 'N/A' else None,
                            episode=details['episode'] if details['episode'] != 'N/A' else None,
                            quality=details['quality']
                        )
                        # Build smart filename
                        smart_name = display_name
                        if details['season'] != 'N/A' and details['episode'] != 'N/A':
                            smart_name += f" S{details['season']} Ep{details['episode']}"
                        elif details['episode'] != 'N/A':
                            smart_name += f" Ep{details['episode']}"
                        if details['quality'] and details['quality'] != 'Unknown':
                            qual_short = re.search(r'(\d{3,4})', str(details['quality']))
                            if qual_short:
                                smart_name += f" {qual_short.group(1)}p"
                        upload_filename = f"[{tag}] {smart_name}"

                # Ensure .mp4 extension
                if not upload_filename.lower().endswith('.mp4'):
                    for ext in ['.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv']:
                        if upload_filename.lower().endswith(ext):
                            upload_filename = upload_filename[:-len(ext)]
                            break
                    upload_filename = upload_filename + '.mp4'

                # ==========================================
                # CAPTION (Custom or Default)
                # ==========================================
                cap = make_caption(anime, path, sz, dur, cid, clean_file)

                # ==========================================
                # UPLOAD TO USER DM
                # ==========================================
                print(f"   📤 DM upload: {upload_filename[:50]}...")
                
                user_msg = None
                for attempt in range(3):
                    try:
                        user_msg = await self.c.send_video(
                            chat_id=cid,
                            video=final_path,
                            caption=cap,
                            file_name=upload_filename,
                            duration=dur,
                            width=w,
                            height=h,
                            thumb=thumb,
                            supports_streaming=True,
                            progress=self.prog
                        )
                        self.dm_done = True
                        print(f"   ✅ DM upload success!")
                        break
                    except FloodWait as e:
                        print(f"   ⏳ FloodWait: {e.value}s")
                        await asyncio.sleep(e.value + 1)
                    except Exception as e:
                        print(f"   ❌ DM attempt {attempt + 1} failed: {e}")
                        if attempt == 2:
                            return False, None
                        await asyncio.sleep(3)

                if not user_msg:
                    return False, None

                # ==========================================
                # CHANNEL UPLOADS (After DM success)
                # ==========================================
                for ch in user_channels:
                    similarity = SequenceMatcher(
                        None, anime.lower(), ch['anime'].lower()
                    ).ratio()
                    
                    if similarity >= 0.67:
                        try:
                            await self._upload_to_channel(
                                original_path=path,
                                meta_path=final_path,
                                channel_info=ch,
                                anime_name=display_name,
                                clean_filename=clean_file,
                                dur=dur, w=w, h=h,
                                user_id=cid,
                                user_message=user_msg
                            )
                            self.channel_completed += 1
                        except Exception as e:
                            print(f"   ❌ Channel upload error: {e}")
                            traceback.print_exc()

                # Final channel status
                if self.channel_total > 0 and self.channel_completed >= self.channel_total:
                    self.channel_done = True

                # ==========================================
                # CLEANUP
                # ==========================================
                if thumb and os.path.exists(thumb):
                    try:
                        os.remove(thumb)
                    except:
                        pass

                if final_path and final_path != path and os.path.exists(final_path):
                    try:
                        os.remove(final_path)
                    except:
                        pass

                return True, user_msg

            except Exception as e:
                print(f"   ❌ Upload Error: {e}")
                traceback.print_exc()
                return False, None

    # ==========================================
    # 📢 UPLOAD TO CHANNEL
    # ==========================================
    async def _upload_to_channel(
        self, original_path, meta_path, channel_info,
        anime_name, clean_filename, dur, w, h, user_id, user_message
    ):
        """
        Channel upload logic:
        - No audio filter → FORWARD from DM (fast, no re-upload)
        - Audio filter needed → DIRECT upload filtered file
        """
        try:
            channel_id = int(channel_info['channel_id'])
            languages = channel_info['languages']
            channel_title = channel_info.get('channel_title', 'Channel')

            print(f"\n   📢 Channel: {channel_title}")
            print(f"   🎧 Filter: {languages}")
            
            # Set tracking for progress bar
            self.is_uploading_to_channel = True
            self.channel_name = channel_title
            self.channel_id = channel_id

            # ==========================================
            # STEP 1: AUDIO FILTERING
            # ==========================================
            source_file = meta_path if (meta_path and os.path.exists(meta_path)) else original_path
            output_dir = os.path.dirname(original_path)

            filtered_file = None
            audio_was_filtered = False

            if languages.lower() != 'all':
                print(f"   🎧 Filtering audio for: {languages}")
                filtered_file = await filter_audio(source_file, languages, output_dir)
                
                if filtered_file != source_file:
                    audio_was_filtered = True
                    print(f"   ✅ Audio filtered successfully!")
                else:
                    print(f"   ℹ️ No filtering needed")
                    filtered_file = None

            # Determine which file to use
            upload_file = filtered_file if audio_was_filtered else source_file

            # ==========================================
            # STEP 2: DETECT LANGUAGE IN UPLOAD FILE
            # ==========================================
            actual_language = get_audio_language_strict(upload_file)
            
            if not actual_language or actual_language in ["Unknown", "No Audio", None]:
                actual_language = self._get_channel_language_display(languages)
            elif "Multi Audio" in actual_language and languages.lower() != 'all':
                actual_language = self._get_channel_language_display(languages)

            print(f"   🌐 Language: {actual_language}")

            # Update progress tracking
            self.current_language = actual_language

            # ==========================================
            # STEP 3: BUILD CAPTION
            # ==========================================
            info = parse_filename(os.path.basename(original_path))
            quality = get_real_quality(upload_file)
            season = info.get('season') or 'N/A'
            episode = info.get('episode') or 'N/A'
            sz = os.path.getsize(upload_file)
            duration_str = fmt_dur(dur)
            size_str = fmt_bytes(sz)

            # Custom caption check
            if user_id and user_id in db.get('captions', {}):
                template = db['captions'][user_id]
                cap = apply_custom_caption(
                    template, anime_name, season, episode,
                    actual_language, quality, size_str, duration_str
                )
            else:
                # Default caption
                is_movie = info.get('is_movie') or self.task.is_movie
                if is_movie:
                    cap = f"""🎬 {anime_name}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🍿 Type: Movie
│ 🌐 Language: {actual_language}
│ 📊 Quality: {quality}
│ 📦 Size: {size_str}
│ ⏱️ Duration: {duration_str}
╰━━━━━━━━━━━━━━━━━━━╯"""
                else:
                    cap = f"""🎬 {anime_name}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🏝️ Season: {season}
│ 📺 Episode: {episode}
│ 🌐 Language: {actual_language}
│ 📊 Quality: {quality}
│ 📦 Size: {size_str}
│ ⏱️ Duration: {duration_str}
╰━━━━━━━━━━━━━━━━━━━╯"""

            # ==========================================
            # STEP 4: THUMBNAIL
            # ==========================================
            thumb = None

            # User's custom thumbnail
            if user_id in db.get('thumbnails', {}) and db['thumbnails'][user_id]:
                tid = smart_thumb_match(anime_name, db['thumbnails'][user_id])
                if tid:
                    tp = os.path.join(THUMB_DIR, f"ch_{user_id}_{int(time.time())}.jpg")
                    try:
                        await self.c.download_media(tid, file_name=tp)
                        if os.path.exists(tp):
                            thumb = tp
                    except:
                        pass

            # Auto-generate
            if not thumb:
                tp = os.path.join(THUMB_DIR, f"ch_auto_{int(time.time())}.jpg")
                thumb = make_thumb(upload_file, tp)

            # ==========================================
            # STEP 5: UPLOAD TO CHANNEL
            # ==========================================
            # Build filename for channel
            if isinstance(season, int) and isinstance(episode, int):
                upload_filename = f"{anime_name} S{season:02d}E{episode:02d} {quality}.mp4"
            elif season != 'N/A' and episode != 'N/A':
                upload_filename = f"{anime_name} S{season}E{episode} {quality}.mp4"
            else:
                upload_filename = f"{anime_name} {quality}.mp4"

            # ==========================================
            # CHOOSE METHOD: Forward or Direct
            # ==========================================
            if audio_was_filtered and filtered_file:
                # ✅ Audio was filtered → MUST direct upload
                print(f"   📤 DIRECT upload (audio was filtered)")
                
                self.start = time.time()
                self.last = 0

                await self.c.send_video(
                    chat_id=channel_id,
                    video=upload_file,
                    caption=cap,
                    file_name=upload_filename,
                    duration=dur,
                    width=w, height=h,
                    thumb=thumb,
                    supports_streaming=True,
                    progress=self.prog
                )
                print(f"   ✅ Channel done (DIRECT) | {actual_language}")

            else:
                # ✅ No filter → FORWARD from DM (fast!)
                if user_message:
                    try:
                        print(f"   📢 FORWARD from DM (no filter needed)")
                        await user_message.copy(
                            chat_id=channel_id,
                            caption=cap
                        )
                        print(f"   ✅ Channel done (FORWARD)")
                    except Exception as fw_err:
                        # Fallback: direct upload
                        print(f"   ⚠️ Forward failed: {fw_err}, trying direct...")
                        await self.c.send_video(
                            chat_id=channel_id,
                            video=upload_file,
                            caption=cap,
                            file_name=upload_filename,
                            duration=dur,
                            width=w, height=h,
                            thumb=thumb,
                            supports_streaming=True
                        )
                        print(f"   ✅ Channel done (DIRECT fallback)")
                else:
                    # No user_message available
                    print(f"   📤 DIRECT upload (no user_message)")
                    await self.c.send_video(
                        chat_id=channel_id,
                        video=upload_file,
                        caption=cap,
                        file_name=upload_filename,
                        duration=dur,
                        width=w, height=h,
                        thumb=thumb,
                        supports_streaming=True
                    )
                    print(f"   ✅ Channel done (DIRECT)")

            # ==========================================
            # STEP 6: CLEANUP
            # ==========================================
            if thumb and os.path.exists(thumb):
                try:
                    os.remove(thumb)
                except:
                    pass

            if filtered_file and filtered_file != source_file and os.path.exists(filtered_file):
                try:
                    os.remove(filtered_file)
                    print(f"   🗑️ Filtered file cleaned")
                except:
                    pass

            self.is_uploading_to_channel = False
            await asyncio.sleep(2)

        except Exception as e:
            print(f"   ❌ Channel {channel_title} failed: {e}")
            traceback.print_exc()
            self.is_uploading_to_channel = False

    # ==========================================
    # 📤 UPLOAD ALL FILES TO ALL SUBSCRIBERS
    # ==========================================
    async def upload_all(self):
        """Upload all task files to all subscribers"""
        
        # Get valid files only
        files = [f for f in self.task.files if validate_file(f)[0]]
        if not files:
            print(f"⚠️ No valid files to upload")
            return

        # ==========================================
        # ✅ SORT FILES: By quality (360p → 480p → 720p → 1080p)
        # ==========================================
        def get_sort_key(filepath):
            fname = os.path.basename(filepath).lower()
            
            # Quality priority
            if '360' in fname:
                quality_order = 1
            elif '480' in fname:
                quality_order = 2
            elif '720' in fname:
                quality_order = 3
            elif '1080' in fname:
                quality_order = 4
            else:
                quality_order = 5
            
            # Episode number (for batch)
            ep_match = re.search(r'[es](\d+)', fname, re.I)
            episode_num = int(ep_match.group(1)) if ep_match else 0
            
            # Part number (for split files)
            part_match = re.search(r'part(\d+)', fname, re.I)
            part_num = int(part_match.group(1)) if part_match else 0
            
            return (episode_num, quality_order, part_num)
        
        files = sorted(files, key=get_sort_key)
        print(f"📊 Sorted files order:")
        for f in files:
            print(f"   • {os.path.basename(f)}")

        self.total = len(files)

        # Get unique subscribers (no duplicates)
        unique_subs = {}
        for sub in self.task.subscribers:
            uid = sub['user_id']
            if uid not in unique_subs:
                unique_subs[uid] = sub

        unique_subscribers = list(unique_subs.values())
        print(f"📤 Upload: {len(files)} files → {len(unique_subscribers)} users")

        # Upload each file to each subscriber
        for i, filepath in enumerate(files, 1):
            self.num = i

            # ✅ CANCEL CHECK
            if self.task.cancelled:
                print(f"⚠️ Upload cancelled, skipping remaining files")
                break

            # Get clean display name
            display_name = clean_anime_name(os.path.basename(filepath))
            if not display_name or display_name in ["Unknown", ""]:
                display_name = clean_anime_name(self.task.series_name)

            for sub in unique_subscribers:
                uid, cid = sub['user_id'], sub['chat_id']

                # ==========================================
                # FIND USER'S THUMBNAIL
                # ==========================================
                thumb = None
                if uid in db.get('thumbnails', {}) and db['thumbnails'][uid]:
                    # Try matching with display name
                    thumb = smart_thumb_match(display_name, db['thumbnails'][uid])
                    
                    # Fallback: try series name
                    if not thumb:
                        thumb = smart_thumb_match(self.task.series_name, db['thumbnails'][uid])

                    # Update last used time
                    if thumb and 'thumb_last_used' in db:
                        if uid not in db['thumb_last_used']:
                            db['thumb_last_used'][uid] = {}
                        for tname, tid in db['thumbnails'][uid].items():
                            if tid == thumb:
                                db['thumb_last_used'][uid][tname] = time.time()
                                save_db()
                                break

                # Reset progress
                self.start = None
                self.last = 0

                # Upload (DM first → then channels)
                success, user_msg = await self.upload_to_user(cid, filepath, display_name, thumb)

                if success:
                    print(f"   ✅ File {i}/{self.total} → user {uid}")
                else:
                    print(f"   ❌ File {i}/{self.total} failed for {uid}")

                await asyncio.sleep(2)

        print(f"✅ Upload complete: {len(files)} files processed")

# ==========================================
# DELAYED CLEANUP HELPER
# ==========================================
async def delayed_cleanup(task, delay):
    """Cleanup task files after delay - for single downloads only"""
    try:
        await asyncio.sleep(delay)
        task.cleanup()
    except:
        pass

# ==========================================
# PROCESSOR
# ==========================================
async def process_task(task, st):
    global active_downloads

    try:
        task.status = "downloading"
        active_downloads[task.task_id] = task

        # ✅ Cancel check helper
        def is_cancelled():
            return task.cancelled

        # ==========================================
        # 🔍 DETECT WEBSITE TYPE
        # ==========================================
        site_key, site_data = detect_website(task.url)
        
        if site_key:
            site_name = site_data['name']
            site_type = site_data['type']
            print(f"\n{'='*60}")
            print(f"🌐 Website: {site_name}")
            print(f"🔗 URL: {task.url[:60]}...")
            print(f"{'='*60}")
        else:
            site_name = "Unknown"
            site_type = "unknown"
        
        files = []
        
        # ==========================================
        # 📦 GDFLIX / ANIMEDUBHINDI PROCESSING
        # ==========================================
        if site_type in ['gdflix', 'gdflix_direct']:
            await st.update(f"""
{site_name} **Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{task.series_name}**
📔 **Episode:** {task.episode or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━
🔍 **Extracting download links...**
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
            
            dl = GDFlixDownloader(task, st)
            
            # Check if direct GDFlix URL or need to parse
            if "gdflix" in task.url and "/file/" in task.url:
                # Direct GDFlix file URL
                result = await dl.download_from_gdflix(task.url)
                if result:
                    files = [result]
            elif hasattr(task, 'episode_data') and task.episode_data:
                # Episode data with qualities
                files = await dl.download_all_qualities(task.episode_data)
            else:
                # Need to fetch episode data first
                finder = AnimeDubHindiFinder(st)
                title, season, latest_ep, redirect_url, episodes = await finder.get_info(task.url)
                
                if episodes and latest_ep in episodes:
                    task.episode_data = episodes[latest_ep]
                    files = await dl.download_all_qualities(task.episode_data)
        
        # ==========================================
        # 🎌 TOONO / RAREANIMES / CODEDEW PROCESSING
        # ==========================================
        elif site_type in ['codedew', 'codedew_direct', 'swift', 'swift_direct', 'rareanimes'] or site_key in ['toono', 'rareanimes', None]:
            
            await st.update(f"""
{site_name if site_key else '🔍 Processing'} **Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{task.series_name}**
📔 **Episode:** {task.episode or 'N/A'}

━━━━━━━━━━━━━━━━━━━━━━
🔗 **Resolving download URL...**
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
            
            swift = None
            
            # ==========================================
            # DIRECT SWIFT/MULTIQUALITY URL
            # ==========================================
            if "swift.multiquality" in task.url or "multiquality" in task.url.lower():
                swift = task.url
                print(f"✅ Direct Swift URL")
            
            # ==========================================
            # CODEDEW URL - SMART + SELENIUM FALLBACK
            # ==========================================
            elif "codedew.com" in task.url.lower():
                print(f"🔗 Codedew: {task.url[:60]}...")
                
                await st.update(f"""
🔗 **Resolving Codedew...**
━━━━━━━━━━━━━━━━━━━━━━
🎬 **{task.series_name}**
📔 **Episode:** {task.episode or 'N/A'}
⏳ resolution...
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
                
                swift = None
                
                # ==========================================
                # METHOD 1: SmartCodedewResolver (Requests)
                # ==========================================
                try:
                    resolver = SmartCodedewResolver(st)
                    cdn_url = await resolver.resolve(task.url)
                    
                    if cdn_url and 'cdn/ziptron' in cdn_url:
                        swift = cdn_url
                        print(f"   ✅ Smart resolved: {swift[:60]}...")
                except Exception as e:
                    print(f"   ⚠️ SmartResolver error: {e}")
                
                # ==========================================
                # METHOD 2: Selenium Fallback
                # ==========================================
                if not swift:
                    print(f"\n   🌐 SELENIUM FALLBACK starting...")
                    driver = None
                    
                    try:
                        driver = get_driver()
                        driver.set_page_load_timeout(45)
                        driver.get(task.url)
                        await asyncio.sleep(10)
                        
                        # Check each step in browser
                        for browser_step in range(5):
                            current_url = driver.current_url
                            print(f"   📍 Browser [{browser_step}]: {current_url[:60]}...")
                            
                            # Found cdn/ziptron!
                            if 'cdn/ziptron' in current_url:
                                swift = current_url
                                print(f"   ✅ Selenium found cdn/ziptron!")
                                break
                            
                            # Check page source for cdn link
                            page_source = driver.page_source
                            cdn_match = re.search(
                                r'(https?://[^\s"\']*cdn/ziptron\.php/?\?[^\s"\']+)',
                                page_source
                            )
                            if cdn_match:
                                swift = cdn_match.group(1)
                                print(f"   ✅ Found cdn in source!")
                                break
                            
                            # Try clicking mainActionBtn
                            try:
                                btn = driver.find_element(By.ID, 'mainActionBtn')
                                href = btn.get_attribute('href')
                                
                                if href and 'javascript' not in href.lower() and href != '#':
                                    if 'cdn/ziptron' in href:
                                        swift = href
                                        print(f"   ✅ ActionBtn → cdn/ziptron!")
                                        break
                                    else:
                                        print(f"   🔗 ActionBtn → {href[:50]}...")
                                        driver.get(href)
                                        await asyncio.sleep(8)
                                        continue
                            except:
                                pass
                            
                            # Try clicking any link
                            try:
                                links = driver.find_elements(By.TAG_NAME, 'a')
                                for link in links:
                                    href = link.get_attribute('href') or ''
                                    if 'cdn/ziptron' in href:
                                        swift = href
                                        print(f"   ✅ Link → cdn/ziptron!")
                                        break
                                    if 'codedew.com/zipper' in href and href != current_url:
                                        driver.get(href)
                                        await asyncio.sleep(5)
                                        break
                                
                                if swift:
                                    break
                            except:
                                pass
                            
                            await asyncio.sleep(3)
                        
                        # ✅ Last resort: use whatever URL browser is on
                        if not swift:
                            final_url = driver.current_url
                            if 'codedew' in final_url or 'multiquality' in final_url:
                                swift = final_url
                                print(f"   ⚠️ Using browser URL: {swift[:60]}...")
                        
                        driver.quit()
                        driver = None
                        
                    except Exception as e:
                        print(f"   ❌ Selenium error: {e}")
                        if driver:
                            try:
                                driver.quit()
                            except:
                                pass
                
                if not swift:
                    await st.update("❌ **Failed: Could not resolve URL**")
                    task.status = "failed"
                    return False
                
                print(f"   ✅ Final URL: {swift[:99]}...")
                task.swift_url = swift
            
            # ==========================================
            # EPISODE/SERIES PAGE
            # ==========================================
            else:
                print(f"🔍 Extracting from episode page...")
                res = Resolver(st)
                
                hidden = await res.get_hidden(task.url)
                if not hidden:
                    await st.update("❌ **Failed: Link not found**")
                    task.status = "failed"
                    return False
                
                print(f"✅ Hidden link extracted")

                swift = await res.get_swift(hidden)
                if not swift:
                    await st.update("❌ **Failed: Player URL not found**")
                    task.status = "failed"
                    return False
                
                print(f"✅ Swift URL: {swift[:60]}...")

            # Now download using swift URL
            dl = Downloader(task, st)
            files = await dl.download(swift)

        # ==========================================
        # 🇮🇳 HINDIANIMEZONE
        # ==========================================
        elif site_key == 'hindianimezone' or site_type == 'haz':
            await st.update(
                f"🇮🇳 **HindiAnimeZone**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 **{task.series_name}**\n"
                f"📔 Episode: {task.episode or 'N/A'}\n\n"
                f"🔍 Extracting download links...\n"
                f"━━━━━━━━━━━━━━━━━━━━━━",
                force=True
            )

            finder = HindiAnimeZoneFinder(st)
            quality_urls = await finder.resolve_episode_urls(
                task.episode or 1,
                task.url,
                task.series_name
            )

            if not quality_urls:
                await st.update(
                    f"❌ **HAZ: No download links found**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 URL: `{task.url[:60]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━"
                )
                task.status = "failed"
                return False

            dl = HAZDownloader(task, st)
            files = await dl.download_all(quality_urls)

        # ==========================================
        # 🌏 TOONWORLD4ALL
        # ==========================================
        elif site_key == 'toonworld4all' or site_type == 'toonworld4all':
            await st.update(
                f"🌏 **ToonWorld4All**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 **{task.series_name}**\n"
                f"📔 Episode: {task.episode or 'N/A'}\n\n"
                f"🔍 Extracting download links...\n"
                f"━━━━━━━━━━━━━━━━━━━━━━",
                force=True
            )

            finder = ToonWorld4AllFinder(st)
            quality_urls = await finder.resolve_episode_urls(
                task.episode or 1,
                task.url,
                task.series_name
            )

            if not quality_urls:
                await st.update(
                    f"❌ **TW4ALL: No download links found**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 URL: `{task.url[:60]}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━"
                )
                task.status = "failed"
                return False

            dl = HAZDownloader(task, st)
            files = await dl.download_all(quality_urls)

        # ==========================================
        # ❓ UNKNOWN WEBSITE
        # ==========================================
        else:
            await st.update(
                f"❌ **Unsupported Website**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔗 URL: `{task.url[:49]}`\n\n"
                f"📋 **Supported Sites:**\n"
                f"• toono.in\n"
                f"• rareanimes.app\n"
                f"• animedubhindi.me\n"
                f"• hindianimezone.com\n"
                f"• toonworld4all.me\n"
                f"• gdflix.io / gdflix.dev\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            task.status = "failed"
            return False

        # ✅ CANCEL CHECK after download
        if task.cancelled:
            await st.update("❌ **Cancelled!** Files cleaned up.", force=True)
            task.cleanup()
            task.status = "cancelled"
            return False

        # ==========================================
        # 📤 COMMON UPLOAD LOGIC
        # ==========================================
        if not files:
            await st.update("❌ **Download failed: No files received**")
            task.status = "failed"
            return False

        # ==========================================
        # 📦 PROCESS FILES (ZIP Extract + Rename to MP4)
        # ==========================================
        processed_files = []
        
        for f in files:
            if not os.path.exists(f):
                continue
            
            # Process each file (extract if ZIP, rename to MP4)
            result = await process_downloaded_file(f, task.directory)
            processed_files.extend(result)
        
        files = processed_files
        
        if not files:
            await st.update("❌ **No video files found after processing**")
            task.status = "failed"
            return False
        
        print(f"   📁 Processed files: {len(files)}")
        for f in files:
            print(f"      • {os.path.basename(f)}")

        # ==========================================
        # ✂️ SPLIT LARGE FILES
        # ==========================================
        final_files = []
        for f in files:
            if validate_file(f)[0]:
                file_size = os.path.getsize(f)
                if file_size > MAX_FILE_SIZE:
                    print(f"✂️ File needs splitting: {fmt_bytes(file_size)}")
                    split_parts = await split_video(f, task.directory, st)
                    final_files.extend(split_parts)
                else:
                    final_files.append(f)
        
        if not final_files:
            await st.update("❌ **No valid files after processing**")
            task.status = "failed"
            return False
        
        # ==========================================
        # 🔄 FINAL CHECK: Ensure all files are .mp4
        # ==========================================
        final_files = ensure_all_mp4(final_files)
        
        print(f"   ✅ Final files (all .mp4): {len(final_files)}")
        for f in final_files:
            print(f"      • {os.path.basename(f)}")

        task.files = final_files
        valid_files = [f for f in final_files if validate_file(f)[0]]
        
        task.valid_files = valid_files
        task.file_sizes = {}
        for f in valid_files:
            try:
                task.file_sizes[f] = os.path.getsize(f)
            except:
                task.file_sizes[f] = 0

        # ✅ CANCEL CHECK before upload
        if task.cancelled:
            await st.update("❌ **Cancelled!** Files cleaned up.", force=True)
            task.cleanup()
            task.status = "cancelled"
            return False

        task.status = "uploading"

        up = Uploader(bot, st, task)
        await up.upload_all()

        # Build completion message
        total = sum(task.file_sizes.values())
        
        flist_items = []
        for f in valid_files:
            fname = clean_name(os.path.basename(f))
            quality = get_real_quality(f)
            size = task.file_sizes.get(f, 0)
            
            if "_Part" in fname:
                flist_items.append(f"✅ {fname} - {fmt_bytes(size)}")
            else:
                flist_items.append(f"✅ {fname} - {quality}")
        
        flist = "\n".join(flist_items)

        file_info = parse_filename(os.path.basename(valid_files[0])) if valid_files else {}
        display_name = file_info.get('name', task.series_name)

        split_notice = ""
        if any("_Part" in os.path.basename(f) for f in valid_files):
            split_notice = "\n\n✂️ **Note:** Large file was split into parts"

        if file_info.get('is_movie') or task.is_movie:
            complete_msg = f"""
🎉 **Movie Complete!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{display_name}**

{flist}

━━━━━━━━━━━━━━━━━━━━━━
💾 **Total:** {fmt_bytes(total)}
👥 **Sent to:** {len(task.subscribers)} users{split_notice}
━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            ep = file_info.get('episode', task.episode)
            complete_msg = f"""
🎉 **Episode {ep} Complete!**
━━━━━━━━━━━━━━━━━━━━━━

📺 **{display_name}**

{flist}

━━━━━━━━━━━━━━━━━━━━━━
💾 **Total:** {fmt_bytes(total)}
👥 **Sent to:** {len(task.subscribers)} users{split_notice}
━━━━━━━━━━━━━━━━━━━━━━
"""

        await st.update(complete_msg, force=True)

        task.status = "completed"
        task.upload_success = True
        print(f"✅ [SUCCESS] Episode {task.episode} completed\n")
        return True

    except Exception as e:
        print(f"❌ [ERROR] Process task failed: {e}")
        traceback.print_exc()
        try:
            await st.send(f"❌ Error: {str(e)[:100]}")
        except:
            pass
        task.status = "failed"
        task.upload_success = False
        return False
    
    finally:
        if task.task_id in active_downloads:
            del active_downloads[task.task_id]

        # If cancelled, cleanup immediately
        if task.cancelled:
            task.cleanup()
        elif not hasattr(task, 'is_batch_child') or not task.is_batch_child:
            asyncio.create_task(delayed_cleanup(task, FILE_CLEANUP_TIME))

async def process_batch(task, episodes, st):
    """Process multiple episodes with detailed tracking"""

    # Enable batch mode
    task.batch_mode = True
    task.total_episodes = len(episodes)

    # Results tracking
    results = {
        'success': [],
        'failed': [],
        'total_size': 0,
        'total_files': 0,
        'quality_stats': {'360P': 0, '480P': 0, '720P': 0, '1080P': 0}
    }

    # 🔥 NEW: Track all episode tasks for cleanup
    all_ep_tasks = []

    batch_start_time = time.time()

    try:
        print(f"\n{'='*50}")
        print(f"🎬 BATCH START: {task.series_name}")
        print(f"📊 Total Episodes: {len(episodes)}")
        print(f"{'='*50}\n")

        for idx, ep_item in enumerate(episodes, 1):
            task.current_episode = idx
            ep_task = None  # Initialize here

            # ✅ CANCEL CHECK
            if task.cancelled:
                print(f"❌ Batch cancelled at episode {idx}/{len(episodes)}")
                await st.update(f"""
❌ **Batch Cancelled!**
━━━━━━━━━━━━━━━━━━━━━━

📺 **{task.series_name}**
✅ Completed: {len(results['success'])} episodes
❌ Cancelled at: Episode {idx}/{len(episodes)}

🗑️ Remaining episodes skipped.
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
                break

            # Handle both tuple and dict formats
            if isinstance(ep_item, tuple):
                if len(ep_item) == 2:
                    ep_num, ep_url_or_data = ep_item
                else:
                    ep_num = ep_item[1] if len(ep_item) > 1 else idx
                    ep_url_or_data = ep_item[2] if len(ep_item) > 2 else ep_item[-1]
            elif isinstance(ep_item, dict):
                ep_num = ep_item.get('episode', idx)
                ep_url_or_data = ep_item.get('url') or ep_item.get('qualities', {})
            else:
                ep_num = idx
                ep_url_or_data = str(ep_item)

            print(f"\n[Batch {idx}/{len(episodes)}] Starting Episode {ep_num}")

            # Progress update
            await st.update(f"""
📥 **Batch Download Progress**
━━━━━━━━━━━━━━━━━━━━━━

📺 **{task.series_name}**

━━━━━━━━━━━━━━━━━━━━━━
🎬 **Current:** Episode {ep_num}
📊 **Progress:** {idx}/{len(episodes)}

✅ Success: {len(results['success'])}
❌ Failed: {len(results['failed'])}
⏳ Remaining: {len(episodes) - idx + 1}
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)

            try:
                # Determine URL
                if isinstance(ep_url_or_data, str):
                    ep_url = ep_url_or_data
                elif isinstance(ep_url_or_data, dict):
                    # AnimeDubHindi format with qualities
                    ep_url = task.url  # Use original URL
                else:
                    ep_url = str(ep_url_or_data)
                
                # Create episode task
                ep_task = Task(
                    task.user_id,
                    task.chat_id,
                    "episode",
                    f"{task.content_key}_ep{ep_num}",
                    ep_url
                )
                ep_task.series_name = task.series_name
                ep_task.episode = ep_num
                ep_task.batch_mode = True
                ep_task.current_episode = idx
                ep_task.total_episodes = len(episodes)
                ep_task.is_batch_child = True
                ep_task.site_key = getattr(task, 'site_key', None)
                
                # For AnimeDubHindi, store episode data
                if isinstance(ep_url_or_data, dict) and 'qualities' in ep_url_or_data:
                    ep_task.episode_data = ep_url_or_data

                # Track for cleanup
                all_ep_tasks.append(ep_task)

                for sub in task.subscribers:
                    ep_task.add_subscriber(sub['user_id'], sub['chat_id'])

                # Process episode
                result = await process_task(ep_task, st)

                # Track results
                if result and hasattr(ep_task, 'valid_files') and ep_task.valid_files:
                    valid_files = ep_task.valid_files
                    file_sizes = getattr(ep_task, 'file_sizes', {})
                    episode_size = sum(file_sizes.values())

                    results['success'].append((ep_num, valid_files, episode_size))
                    results['total_files'] += len(valid_files)
                    results['total_size'] += episode_size

                    # Quality tracking
                    for f in valid_files:
                        fname = os.path.basename(f).lower()
                        if '1080' in fname: results['quality_stats']['1080P'] += 1
                        elif '720' in fname: results['quality_stats']['720P'] += 1
                        elif '480' in fname: results['quality_stats']['480P'] += 1
                        elif '360' in fname: results['quality_stats']['360P'] += 1

                    print(f"✅ Episode {ep_num} - SUCCESS ({len(valid_files)} files, {fmt_bytes(episode_size)})")
                else:
                    results['failed'].append((ep_num, "Download failed"))
                    print(f"❌ Episode {ep_num} - FAILED")

            except Exception as e:
                results['failed'].append((ep_num, str(e)[:30]))
                print(f"❌ Episode {ep_num} - ERROR: {e}")
                traceback.print_exc()

            # Cleanup this episode's files
            if ep_task:
                try:
                    ep_task.cleanup()
                except:
                    pass

            # Wait before next
            if idx < len(episodes):
                await st.update(f"✅ **Episode {ep_num} Done!**\n\n⏳ Next episode in 5 seconds...", force=True)
                await asyncio.sleep(5)

            # 🔥 NEW: Cleanup this episode's files after stats collected
            if ep_task:
                ep_task.cleanup()

            # Wait before next
            if idx < len(episodes):
                await st.update(f"✅ **Episode {ep_num} Done!**\n\n⏳ Next episode in 5 seconds...", force=True)
                await asyncio.sleep(5)

        # ========== FINAL SUMMARY ==========
        total_time = time.time() - batch_start_time

        # Build quality breakdown
        quality_lines = ""
        for q, count in results['quality_stats'].items():
            if count > 0:
                quality_lines += f"   🔸 {q}: {count} files\n"

        # Build success list
        success_lines = ""
        
        # ✅ FIX: Build lookup dict ONCE (O(1) instead of O(n³))
        all_file_sizes = {}
        for ep_task in all_ep_tasks:
            if hasattr(ep_task, 'file_sizes'):
                all_file_sizes.update(ep_task.file_sizes)
        
        for ep_num, files, size in results['success']:
            success_lines += f"\n📺 **Episode {ep_num}** ({fmt_bytes(size)})\n"
            for f in files:
                fname = os.path.basename(f)
                q = get_quality(fname)
                # ✅ Simple O(1) lookup
                fsize = all_file_sizes.get(f, 0)
                success_lines += f"   ✓ {q} ({fmt_bytes(fsize)})\n"

        # Build failed list
        failed_lines = ""
        if results['failed']:
            failed_lines = "\n━━━━━━━━━━━━━━━━━━━━━━\n⚠️ **FAILED EPISODES**\n━━━━━━━━━━━━━━━━━━━━━━\n"
            for ep_num, error in results['failed']:
                failed_lines += f"   ❌ Episode {ep_num} - {error}\n"

        # Final message
        summary = f"""
🎉 **Batch Download Complete!**

━━━━━━━━━━━━━━━━━━━━━━
📺 **{task.series_name}**
━━━━━━━━━━━━━━━━━━━━━━

📊 **BATCH STATISTICS**
━━━━━━━━━━━━━━━━━━━━━━
📔 Episodes: {episodes[0][0]} to {episodes[-1][0]}
📈 Total: {len(episodes)} episodes

✅ Success: {len(results['success'])}
❌ Failed: {len(results['failed'])}

━━━━━━━━━━━━━━━━━━━━━━
📦 **DOWNLOAD SUMMARY**
━━━━━━━━━━━━━━━━━━━━━━
📁 Total Files: {results['total_files']}
💾 Total Size: {fmt_bytes(results['total_size'])}

**Quality Breakdown:**
{quality_lines}
━━━━━━━━━━━━━━━━━━━━━━
✅ **DELIVERED EPISODES**
━━━━━━━━━━━━━━━━━━━━━━
{success_lines}
{failed_lines}
━━━━━━━━━━━━━━━━━━━━━━
👥 Sent to: {len(task.subscribers)} user(s)
⏱️ Total Time: {fmt_time(total_time)}
━━━━━━━━━━━━━━━━━━━━━━
"""

        if len(results['success']) == len(episodes):
            summary += "\n🎊 **All episodes sent successfully!**"

        await st.update(summary, force=True)

        print(f"\n{'='*50}")
        print(f"🎉 BATCH COMPLETE - Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        print(f"{'='*50}\n")

        return True

    except Exception as e:
        print(f"Batch Error: {e}")
        traceback.print_exc()
        await st.send(f"❌ Batch Error: {str(e)[:100]}")
        return False
    finally:
        # 🔥 Cleanup any remaining tasks
        for ep_task in all_ep_tasks:
            try:
                ep_task.cleanup()
            except:
                pass

# ==========================================
# DOWNLOAD WORKERS
# ==========================================
async def download_worker(wid):
    global download_semaphore, batch_semaphore, queue_lock

    worker_status[wid] = "idle"
    print(f"[Download Worker {wid}] Started")

    while True:
        try:
            if _sf or _rf:
                break

            t = None
            async with queue_lock:
                if task_queue:
                    t = task_queue.popleft()

            if t is None:
                await asyncio.sleep(1)
                continue

            task = t['task']
            task_id = task.task_id

            # Check if cancelled while in queue
            if task.cancelled:
                print(f"[Worker {wid}] Task {task_id} was cancelled in queue, skipping")
                if task_id in active_downloads:
                    del active_downloads[task_id]
                task.cleanup()
                continue

            if t['type'] == 'batch':
                semaphore = batch_semaphore
            else:
                semaphore = download_semaphore

            async with semaphore:
                worker_status[wid] = "working"
                active_downloads[task_id] = task
                print(f"[Worker {wid}] Processing: {task_id}")

                try:
                    if t['type'] == 'single':
                        success = await process_task(task, t['status'])
                    elif t['type'] == 'batch':
                        success = await process_batch(task, t['episodes'], t['status'])
                    else:
                        success = False

                except Exception as e:
                    print(f"[Worker {wid}] Error: {e}")
                    traceback.print_exc()
                    try:
                        for sub in task.subscribers:
                            await bot.send_message(sub['chat_id'], f"❌ Error: {str(e)[:100]}")
                    except:
                        pass

                finally:
                    worker_status[wid] = "idle"
                    if task_id in active_downloads:
                        del active_downloads[task_id]

        except Exception as e:
            print(f"[Worker {wid}] Loop error: {e}")
            traceback.print_exc()
            await asyncio.sleep(5)
    
# ==========================================
# MONITOR - MULTI-EPISODE + MULTI-WEBSITE
# ==========================================
async def monitor():
    while True:
        try:
            if _sf or _rf:
                break

            for key, data in list(db['monitored'].items()):
                try:
                    intv = data.get('interval', 3)
                    lc = data.get('last_check', 0)

                    if time.time() - lc < intv * 60:
                        continue

                    db['monitored'][key]['last_check'] = time.time()
                    
                    monitor_url = data.get('monitor_url') or data.get('series_url')
                    site_key, site_data = detect_website(monitor_url)
                    
                    title = data.get('series_name', 'Unknown')
                    last_tracked_ep = data.get('last_episode', 0)
                    monitored_season = data.get('last_season', 1)
                    
                    # ==========================================
                    # COLLECT ALL NEW EPISODES
                    # ==========================================
                    new_episodes = []  # List of (ep_num, ep_url_or_data)
                    new_latest = last_tracked_ep
                    new_season = monitored_season
                    
                    # ==========================================
                    # 🎬 ANIMEDUBHINDI
                    # ==========================================
                    if site_key == 'animedubhindi':
                        finder = AnimeDubHindiFinder()
                        episodes = await finder.parse_episodes(monitor_url)
                        
                        if episodes:
                            for ep_num in sorted(episodes.keys()):
                                if ep_num > last_tracked_ep:
                                    new_episodes.append({
                                        'episode': ep_num,
                                        'data': episodes[ep_num],
                                        'url': monitor_url
                                    })
                                    if ep_num > new_latest:
                                        new_latest = ep_num
                    
                    # ==========================================
                    # 🎭 RAREANIMES
                    # ==========================================
                    elif site_key == 'rareanimes':
                        finder = RareAnimesFinder()
                        _, _, latest_ep, eps = await finder.get_info(monitor_url)
                        
                        if eps:
                            for item in eps:
                                if isinstance(item, tuple) and len(item) >= 3:
                                    s, e, u = item[0], item[1], item[2]
                                    if e > last_tracked_ep:
                                        new_episodes.append({
                                            'episode': e,
                                            'url': u,
                                            'data': None
                                        })
                                        if e > new_latest:
                                            new_latest = e
                                            new_season = s
                    
                    # ==========================================
                    # 🇮🇳 HINDIANIMEZONE
                    # ==========================================
                    elif site_key == 'hindianimezone':
                        haz_finder = HindiAnimeZoneFinder()
                        _, _, latest_ep = await haz_finder.get_info(monitor_url)

                        if latest_ep and latest_ep > last_tracked_ep:
                            # Each missing episode needs its own task URL
                            # We queue from (last_tracked_ep+1) to latest_ep
                            for ep_n in range(last_tracked_ep + 1, latest_ep + 1):
                                new_episodes.append({
                                    'episode': ep_n,
                                    'url': monitor_url,  # series page; HAZDownloader resolves per ep
                                    'data': None
                                })
                                new_latest = latest_ep

                    # ==========================================
                    # 🌏 TOONWORLD4ALL
                    # ==========================================
                    elif site_key == 'toonworld4all':
                        tw_finder = ToonWorld4AllFinder()
                        _, _, latest_ep = await tw_finder.get_info(monitor_url)

                        if latest_ep and latest_ep > last_tracked_ep:
                            for ep_n in range(last_tracked_ep + 1, latest_ep + 1):
                                new_episodes.append({
                                    'episode': ep_n,
                                    'url': monitor_url,
                                    'data': None
                                })
                                new_latest = latest_ep

                    # ==========================================
                    # 🎌 TOONO
                    # ==========================================
                    elif site_key == 'toono' or site_key is None:
                        f = Finder()
                        _, last_season, latest_ep, eps = await f.get_info(monitor_url)

                        if eps:
                            season_eps = {}
                            for s, e, u in eps:
                                if s not in season_eps:
                                    season_eps[s] = []
                                season_eps[s].append((e, u))

                            # Check current season
                            if monitored_season in season_eps:
                                for e, u in season_eps[monitored_season]:
                                    if e > last_tracked_ep:
                                        new_episodes.append({
                                            'episode': e,
                                            'url': u,
                                            'data': None
                                        })
                                        if e > new_latest:
                                            new_latest = e

                            # Check new season
                            if last_season and last_season > monitored_season:
                                if last_season in season_eps:
                                    new_season = last_season
                                    for e, u in season_eps[last_season]:
                                        new_episodes.append({
                                            'episode': e,
                                            'url': u,
                                            'data': None
                                        })
                                        if e > new_latest:
                                            new_latest = e
                    
                    # ==========================================
                    # 🎉 NEW EPISODES FOUND!
                    # ==========================================
                    if not new_episodes:
                        continue
                    
                    # Sort by episode number
                    new_episodes.sort(key=lambda x: x['episode'])
                    
                    ep_nums = [ep['episode'] for ep in new_episodes]
                    print(f"\n🎉 NEW EPISODES: {title}")
                    print(f"   📺 Episodes: {ep_nums}")
                    print(f"   👥 Subscribers: {len(data['subscribers'])}")
                    
                    # Notify subscribers
                    ep_list_str = ', '.join(str(e) for e in ep_nums)
                    for s in data['subscribers']:
                        try:
                            await bot.send_message(
                                s['chat_id'],
                                f"""
?? **NEW EPISODES DETECTED!**
━━━━━━━━━━━━━━━━━━━━━━

📺 **{title}**
🏝️ Season: {new_season}
🎬 Episodes: {ep_list_str}
📊 Count: {len(new_episodes)} new episode(s)

━━━━━━━━━━━━━━━━━━━━━━
⏳ **Download starting in 7 minutes...**
━━━━━━━━━━━━━━━━━━━━━━
"""
                            )
                        except Exception as e:
                            print(f"   ⚠️ Notify failed: {e}")
                    
                    # Wait 7 minutes
                    print(f"   ⏳ Waiting {MONITOR_NEW_EP_DELAY}s...")
                    await asyncio.sleep(MONITOR_NEW_EP_DELAY)
                    
                    # Update database
                    db['monitored'][key]['last_episode'] = new_latest
                    db['monitored'][key]['last_season'] = new_season
                    save_db()
                    
                    # ==========================================
                    # CREATE TASKS FOR EACH EPISODE
                    # ==========================================
                    for ep_info in new_episodes:
                        ep_num = ep_info['episode']
                        ep_url = ep_info.get('url', monitor_url)
                        ep_data = ep_info.get('data')
                        
                        for sub in data['subscribers']:
                            try:
                                content_key = f"{key}_ep{ep_num}_{sub['user_id']}"
                                
                                user_task = Task(
                                    sub['user_id'],
                                    sub['chat_id'],
                                    "episode",
                                    content_key,
                                    ep_url
                                )
                                user_task.series_name = title
                                user_task.episode = ep_num
                                user_task.site_key = site_key
                                
                                if ep_data:
                                    user_task.episode_data = ep_data

                                user_st = Status(bot, sub['chat_id'])
                                await user_st.create(f"📥 **Downloading Episode {ep_num}...**")

                                add_to_queue('single', user_task, user_st)
                                
                                print(f"   ✅ Ep {ep_num} queued for {sub['user_id']}")
                                await asyncio.sleep(2)
                                
                            except Exception as e:
                                print(f"   ❌ Task failed: {e}")
                        
                        # Delay between episodes
                        if len(new_episodes) > 1:
                            await asyncio.sleep(5)
                    
                    print(f"✅ All {len(new_episodes)} episodes queued for {title}\n")

                except Exception as e:
                    print(f"Monitor error for {key}: {e}")
                    traceback.print_exc()

            await asyncio.sleep(60)

        except Exception as e:
            print(f"Monitor loop error: {e}")
            await asyncio.sleep(60)

# ==========================================
# AUTO CLEANUP
# ==========================================
async def auto_cleanup():
    while True:
        try:
            if _sf or _rf:
                break

            now = time.time()

            for task_id, task in list(active_downloads.items()):
                if now - task.created_at > WORKER_STUCK_TIME:
                    if task.status not in ["completed", "failed"]:
                        task.status = "timeout"
                        for sub in task.subscribers:
                            try:
                                await bot.send_message(sub['chat_id'], "❌ Your download timed out. Please try again.")
                            except:
                                pass
                        task.cleanup()
                        del active_downloads[task_id]

            for d in [DOWNLOAD_DIR, THUMB_DIR]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        try:
                            fp = os.path.join(d, f)
                            if os.path.isfile(fp) and now - os.path.getmtime(fp) > FILE_CLEANUP_TIME:
                                os.unlink(fp)
                        except:
                            pass

            await asyncio.sleep(300)
        except:
            await asyncio.sleep(60)

async def thumb_cleanup():
    while True:
        try:
            if _sf or _rf:
                break

            now = time.time()
            inactive_time = THUMB_INACTIVE_DAYS * 24 * 60 * 60

            for uid in list(db.get('thumb_last_used', {}).keys()):
                for anime in list(db['thumb_last_used'].get(uid, {}).keys()):
                    last_used = db['thumb_last_used'][uid].get(anime, 0)
                    if now - last_used > inactive_time:
                        if uid in db['thumbnails'] and anime in db['thumbnails'][uid]:
                            del db['thumbnails'][uid][anime]
                            del db['thumb_last_used'][uid][anime]
                            save_db()
                            try:
                                await bot.send_message(uid, f"🗑️ **Thumbnail Deleted**\n\nYour thumbnail for **\"{anime}\"** was deleted due to 30 days inactivity.")
                            except:
                                pass

            await asyncio.sleep(86400)
        except:
            await asyncio.sleep(3600)

# ==========================================
# PREMIUM EXPIRY MONITOR WITH AUTO CLEANUP
# ==========================================
async def premium_expiry_monitor():
    """Monitor premium expiry and auto-cleanup after 7 hours"""
    while True:
        try:
            if _sf or _rf:
                break

            now = time.time()
            TWO_HOURS = 2 * 60 * 60      # 2 hours before expiry warning
            CLEANUP_HOURS = 2 * 60 * 60   # 2 hours after expiry = cleanup

            for uid, data in list(db.get('premium_users', {}).items()):
                # Skip owner/admin
                if is_owner(uid) or is_admin(uid):
                    continue

                expiry = data.get('expires', 0)
                time_left = expiry - now
                time_since_expiry = now - expiry

                # ==========================================
                # 1️⃣ MESSAGE: 2 Hours Before Expiry
                # ==========================================
                if 0 < time_left <= TWO_HOURS and not data.get('notified_2h'):
                    try:
                        hours = int(time_left / 3600)
                        minutes = int((time_left % 3600) / 60)
                        
                        await bot.send_message(uid, f"""
⚠️ **Premium Expiring Soon!**

━━━━━━━━━━━━━━━━━━━━━━
⏰ **Time Left:** {hours}h {minutes}m

🔔 Your premium will expire soon!

━━━━━━━━━━━━━━━━━━━━━━
⚠️ **IMPORTANT WARNING:**

If you don't renew within **2 hours** after expiry, all your data will be **DELETED**:

🗑️ **Will be removed:**
   • All monitored anime (/set URLs)
   • All custom thumbnails
   • All settings

━━━━━━━━━━━━━━━━━━━━━━
💎 **Renew Now:**
Contact: @Dark_isekai

🔄 **Don't lose your data!**
━━━━━━━━━━━━━━━━━━━━━━
""")
                        db['premium_users'][uid]['notified_2h'] = True
                        save_db()
                    except Exception as e:
                        print(f"Failed to send 2h warning to {uid}: {e}")

                # ==========================================
                # 2️⃣ MESSAGE: At Expiry Time
                # ==========================================
                # ✅ FIX: Wider window (-5min to +5min) to catch even if bot restarts
                elif -300 <= time_since_expiry <= 300 and not data.get('notified_expiry'):
                    try:
                        await bot.send_message(uid, f"""
🚫 **Premium Expired!**

━━━━━━━━━━━━━━━━━━━━━━
⏰ Your premium has expired now.

━━━━━━━━━━━━━━━━━━━━━━
⚠️ **CRITICAL WARNING:**

⏳ You have **2 HOURS** to renew!

If you don't renew premium in 2 hours, **ALL YOUR DATA** will be permanently deleted:

📋 **Your Current Data:**
   🎬 Monitored Anime: {len([d for d in db['monitored'].values() if any(s['user_id'] == uid for s in d['subscribers'])])}
   🖼️ Thumbnails: {len(db.get('thumbnails', {}).get(uid, {}))}

━━━━━━━━━━━━━━━━━━━━━━
💎 **Renew Immediately:**
Contact: @Dark_isekai

⏰ Deadline: 2 hours from now
🗑️ After that = AUTO DELETE
━━━━━━━━━━━━━━━━━━━━━━
""")
                        db['premium_users'][uid]['notified_expiry'] = True
                        save_db()
                    except Exception as e:
                        print(f"Failed to send expiry msg to {uid}: {e}")

                # ==========================================
                # 3️⃣ AUTO DELETE: 2 Hours After Expiry
                # ==========================================
                elif time_since_expiry >= CLEANUP_HOURS and not data.get('notified_cleanup'):
                    print(f"🗑️ Auto-deleting data for expired user: {uid}")
                    
                    # Collect data before deletion
                    deleted_anime = []
                    deleted_thumbs = []
                    
                    # Remove monitored anime
                    for key, mon_data in list(db['monitored'].items()):
                        mon_data['subscribers'] = [s for s in mon_data['subscribers'] if s['user_id'] != uid]
                        if not mon_data['subscribers']:
                            deleted_anime.append(mon_data['series_name'])
                            del db['monitored'][key]
                        elif any(s['user_id'] == uid for s in mon_data.get('subscribers', [])):
                            deleted_anime.append(mon_data['series_name'])
                    
                    # Remove thumbnails
                    if uid in db.get('thumbnails', {}):
                        deleted_thumbs = list(db['thumbnails'][uid].keys())
                        del db['thumbnails'][uid]
                    
                    if uid in db.get('thumb_last_used', {}):
                        del db['thumb_last_used'][uid]
                    
                    # Remove premium entry
                    del db['premium_users'][uid]
                    save_db()
                    
                    # Send final message with list
                    try:
                        anime_list = "\n".join([f"   • {name}" for name in deleted_anime]) if deleted_anime else "   • None"
                        thumb_list = "\n".join([f"   • {name}" for name in deleted_thumbs]) if deleted_thumbs else "   • None"
                        
                        await bot.send_message(uid, f"""
🗑️ **Data Cleanup Complete**

━━━━━━━━━━━━━━━━━━━━━━
⏰ 2 hours passed since premium expired.

All your data has been **permanently deleted** as per policy.

━━━━━━━━━━━━━━━━━━━━━━
📋 **DELETED DATA:**

🎬 **Monitored Anime ({len(deleted_anime)}):**
{anime_list}

🖼️ **Thumbnails ({len(deleted_thumbs)}):**
{thumb_list}

━━━━━━━━━━━━━━━━━━━━━━
💎 **Want to Continue?**

Renew premium to use bot again:
Contact: @Dark_isekai

✨ After renewal, you can set up everything again!
━━━━━━━━━━━━━━━━━━━━━━
""")
                    except Exception as e:
                        print(f"Failed to send cleanup msg to {uid}: {e}")

            await asyncio.sleep(300)  # Check every 5 minutes

        except Exception as e:
            print(f"Premium monitor error: {e}")
            traceback.print_exc()
            await asyncio.sleep(300)

# ==========================================
# BACKUP SCHEDULER
# ==========================================
async def backup_scheduler():
    """Run backup twice daily - 7:00 AM & 7:00 PM IST"""
    while True:
        try:
            if _sf or _rf:
                break
            
            now = datetime.now()
            
            # Find next backup time from BACKUP_TIMES
            next_backup = None
            min_wait = float('inf')
            
            for bt in BACKUP_TIMES:
                target = now.replace(
                    hour=bt['hour'], 
                    minute=bt['minute'], 
                    second=0, 
                    microsecond=0
                )
                
                # If this time already passed today, schedule for tomorrow
                if now >= target:
                    target += timedelta(days=1)
                
                wait = (target - now).total_seconds()
                if wait < min_wait:
                    min_wait = wait
                    next_backup = target
            
            if next_backup:
                # Convert to IST for display
                ist_hour = (next_backup.hour + 5) % 24
                ist_minute = (next_backup.minute + 30) % 60
                if next_backup.minute + 30 >= 60:
                    ist_hour = (ist_hour + 1) % 24
                
                print(f"⏰ Next backup at {ist_hour:02d}:{ist_minute:02d} IST (in {fmt_time(min_wait)})")
                await asyncio.sleep(min_wait)
            else:
                await asyncio.sleep(3600)
                continue
            
            # Run backup
            print("📦 Starting scheduled backup...")
            zip_files, stats = await create_backup()
            
            if zip_files:
                success = await send_backup_to_channel(zip_files, stats)
                if success:
                    print("✅ Backup sent successfully!")
                    await cleanup_old_backups()
                else:
                    print("❌ Backup send failed!")
            else:
                print("❌ Backup creation failed!")
            
            # Wait 2 minutes before checking next schedule
            await asyncio.sleep(120)
            
        except Exception as e:
            print(f"Backup scheduler error: {e}")
            traceback.print_exc()
            await asyncio.sleep(3600)

# ==========================================
# DUPLICATE CHECK
# ==========================================
def is_already_monitored(user_id, url):
    key = get_key(url)
    if not key:
        return False, None
    for k, data in db['monitored'].items():
        if k == key:
            for sub in data['subscribers']:
                if sub['user_id'] == user_id:
                    return True, data['series_name']
    return False, None

# ==========================================
# AUTO URL HANDLER - MULTI-WEBSITE SUPPORT
# ==========================================
async def handle_url(c, m):
    uid = m.from_user.id
    cid = m.chat.id
    url = m.text.strip()

    if is_banned(uid):
        return await m.reply("🚫 Banned")

    # Force sub check
    is_joined, fsub_markup = await check_force_sub(c, uid)
    if not is_joined:
        return await m.reply("🔒 **Join channel first!**\n\nUse /start", reply_markup=fsub_markup)

    if not await premium_check(m):
        return
        
    if not await cooldown_check(m):
        return

    update_cooldown(uid)

    st = Status(c, cid)
    msg = await st.create("🔍 **Detecting URL type...**")

    try:
        # ==========================================
        # 🔍 DETECT WEBSITE
        # ==========================================
        site_key, site_data = detect_website(url)
        
        if site_key:
            site_name = site_data['name']
            site_type = site_data['type']
            await msg.edit(f"{site_name} **Detected!**\n\n⏳ Processing...")
        else:
            site_name = "🔍 Unknown"
            site_type = "unknown"

        content_key = get_content_key(url)

        # ==========================================
        # ⚡ SWIFT / PLAYER DIRECT
        # ==========================================
        if "swift.multiquality" in url or "multiquality.click" in url or "liptron" in url.lower():
            await msg.edit("⚡ **Swift URL Detected!**\n\n📥 Queuing...")
            
            task = Task(uid, cid, "swift", content_key, url)
            task.series_name = "Swift Download"
            task.site_key = 'swift'
            
            success, message = add_to_queue('single', task, st)
            await msg.edit(f"""
⚡ **Swift Player**
━━━━━━━━━━━━━━━━━━━━━━

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🔗 CODEDEW ZIPPER DIRECT
        # ==========================================
        if "codedew.com/zipper" in url.lower():
            await msg.edit("?? **Codedew Detected!**\n\n📥 Queuing...")
            
            task = Task(uid, cid, "codedew", content_key, url)
            task.series_name = "Codedew Download"
            task.site_key = 'codedew'
            
            success, message = add_to_queue('single', task, st)
            await msg.edit(f"""
🔗 **Codedew**
━━━━━━━━━━━━━━━━━━━━━━

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 📦 GDFLIX DIRECT
        # ==========================================
        if site_key == 'gdflix' or ("gdflix" in url.lower() and "/file/" in url):
            await msg.edit(f"""
📦 **GDFlix Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔗 Direct file link

📥 Queuing download...
""")
            
            task = Task(uid, cid, "gdflix", content_key, url)
            task.series_name = "GDFlix Download"
            task.is_movie = True
            task.site_key = 'gdflix'
            
            success, message = add_to_queue('single', task, st)
            await msg.edit(f"""
📦 **GDFlix**
━━━━━━━━━━━━━━━━━━━━━━

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🎬 ANIMEDUBHINDI HANDLING
        # ==========================================
        if site_key == 'animedubhindi':
            await msg.edit(f"""
🎬 **AnimeDubHindi Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Scanning for episodes...
""")
            
            finder = AnimeDubHindiFinder(st)
            result = await finder.get_info(url)
            
            # Safe unpack (5 values expected)
            title = result[0] if len(result) > 0 else None
            season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            redirect_url = result[3] if len(result) > 3 else None
            episodes = result[4] if len(result) > 4 else {}
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not episodes:
                return await msg.edit("❌ **No episodes found!**")
            
            # Create task for latest episode
            task = Task(uid, cid, "episode", content_key, url)
            task.series_name = title
            task.episode = latest_ep
            task.site_key = 'animedubhindi'
            
            if latest_ep and latest_ep in episodes:
                task.episode_data = episodes[latest_ep]
            
            qualities = []
            if latest_ep and latest_ep in episodes:
                qualities = list(episodes[latest_ep].get('qualities', {}).keys())
            qual_str = ', '.join(qualities) if qualities else 'Auto-detect'
            
            success, message = add_to_queue('single', task, st)
            
            await msg.edit(f"""
👽 **AnimeDubHindi**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
🏝️ **Season:** {season}
🎯 **Latest:** Episode {latest_ep}

━━━━━━━━━━━━━━━━━━━━━━
📊 **Qualities:** {qual_str}
📺 **Total Episodes:** {len(episodes)}

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🎭 RAREANIMES HANDLING
        # ==========================================
        if site_key == 'rareanimes':
            await msg.edit(f"""
🎭 **RareAnimes Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Scanning for episodes...
""")
            
            finder = RareAnimesFinder(st)
            result = await finder.get_info(url)
            
            # Safe unpack
            title = result[0] if len(result) > 0 else None
            season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            eps = result[3] if len(result) > 3 else []
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not eps:
                return await msg.edit("❌ **No episodes found!**")
            
            # Find latest episode URL (codedew URL - DON'T RESOLVE, just pass it)
            ep_url = None
            for item in eps:
                if isinstance(item, tuple) and len(item) >= 3:
                    s, e, u = item[0], item[1], item[2]
                    if e == latest_ep:
                        ep_url = u
                        break
            
            # Fallback to last episode
            if not ep_url and eps:
                last = eps[-1]
                if isinstance(last, tuple) and len(last) >= 3:
                    ep_url = last[2]
                    latest_ep = last[1]
            
            if not ep_url:
                return await msg.edit("❌ **Could not find episode URL**")
            
            # DON'T pre-resolve codedew - pass directly to Downloader (uses Selenium)
            task = Task(uid, cid, "episode", content_key, ep_url)
            task.series_name = title
            task.episode = latest_ep
            task.season = season
            task.site_key = 'rareanimes'
            
            success, message = add_to_queue('single', task, st)
            
            await msg.edit(f"""
🎭 **RareAnimes**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
🏝️ **Season:** {season}
📔 **Episode:** {latest_ep}

━━━━━━━━━━━━━━━━━━━━━━
📊 **Total Episodes:** {len(eps)}

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🎌 TOONO - SERIES URL
        # ==========================================
        if site_key == 'toono' and "/series/" in url:
            await msg.edit(f"""
📺 **Toono Series Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Fetching series info...
""")

            f = Finder(st)
            title, last_season, latest_ep, eps = await f.get_info(url)

            if not title:
                return await msg.edit("❌ **Could not fetch series info**")

            if not eps:
                return await msg.edit("❌ **No episodes found!**")

            # Find latest episode URL
            ep_url = None
            for s, e, u in eps:
                if s == last_season and e == latest_ep:
                    ep_url = u
                    break

            if not ep_url and eps:
                ep_url = eps[-1][2]
                last_season = eps[-1][0]
                latest_ep = eps[-1][1]

            if ep_url:
                task = Task(uid, cid, "episode", get_content_key(ep_url, title, latest_ep), ep_url)
                task.series_name = title
                task.episode = latest_ep
                task.site_key = 'toono'

                success, message = add_to_queue('single', task, st)
                await msg.edit(f"""
🎌 **Toono**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
🏝️ **Season:** {last_season}
📔 **Episode:** {latest_ep}

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            else:
                await msg.edit("❌ **Could not find episode URL**")
            return

        # ==========================================
        # 🎌 TOONO - MOVIE URL
        # ==========================================
        if site_key == 'toono' and "/movies/" in url:
            await msg.edit(f"""
🎥 **Toono Movie Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Fetching movie info...
""")
            
            try:
                response = await asyncio.to_thread(safe_request, url)
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                return await msg.edit(f"❌ **Connection Error**\n\n🔄 Please try again")

            h1 = soup.find("h1")
            raw_title = h1.get_text(strip=True) if h1 else "Unknown Movie"
            title = clean_page_title(raw_title)
            
            task = Task(uid, cid, "movie", content_key, url)
            task.series_name = title
            task.is_movie = True
            task.site_key = 'toono'

            success, message = add_to_queue('single', task, st)
            await msg.edit(f"""
🎥 **Toono Movie**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
🍿 **Type:** Movie

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🎌 TOONO - GENERIC (try as series)
        # ==========================================
        if site_key == 'toono':
            await msg.edit(f"""
🎌 **Toono Detected!**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Processing URL...
""")
            
            # Try to get info
            f = Finder(st)
            title, last_season, latest_ep, eps = await f.get_info(url)

            if title and eps:
                ep_url = eps[-1][2] if eps else url
                latest_ep = eps[-1][1] if eps else 1
                
                task = Task(uid, cid, "episode", content_key, ep_url)
                task.series_name = title
                task.episode = latest_ep
                task.site_key = 'toono'

                success, message = add_to_queue('single', task, st)
                await msg.edit(f"""
🎌 **Toono**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
📔 **Episode:** {latest_ep}

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            else:
                # Direct download attempt
                task = Task(uid, cid, "episode", content_key, url)
                task.series_name = "Toono Download"
                task.site_key = 'toono'
                
                success, message = add_to_queue('single', task, st)
                await msg.edit(f"""
🎌 **Toono**
━━━━━━━━━━━━━━━━━━━━━━

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
            return

        # ==========================================
        # 🇮🇳 HINDIANIMEZONE HANDLING
        # ==========================================
        if site_key == 'hindianimezone':
            await msg.edit(
                "🇮🇳 **HindiAnimeZone Detected!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔍 Fetching series info..."
            )

            finder = HindiAnimeZoneFinder(st)
            title, season, latest_ep = await finder.get_info(url)

            if not title or title == "Unknown Anime":
                return await msg.edit(
                    "❌ **Could not fetch series info**\n\n"
                    "Make sure the URL is a **series page** on HindiAnimeZone."
                )

            if not latest_ep:
                return await msg.edit(
                    f"❌ **No episodes found for:** {title}\n\n"
                    "The page may not have episodes listed yet."
                )

            task = Task(uid, cid, "episode", content_key, url)
            task.series_name = title
            task.episode = latest_ep
            task.site_key = 'hindianimezone'

            success, message = add_to_queue('single', task, st)

            await msg.edit(
                f"🇮🇳 **HindiAnimeZone**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎬 **{title}**\n"
                f"🏝️ **Season:** {season}\n"
                f"📔 **Latest Episode:** {latest_ep}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 **{message}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            return

        # ==========================================
        # ❓ UNKNOWN - TRY GENERIC DOWNLOAD
        # ==========================================
        if site_key is None:
            # Check if it looks like any supported site
            url_lower = url.lower()
            
            if "toono" in url_lower or "raretoons" in url_lower or "rareanimes" in url_lower:
                # Try RareAnimes
                await msg.edit("🔍 **Detecting as RareAnimes...**")
                
                finder = RareAnimesFinder(st)
                result = await finder.get_info(url)
                
                title = result[0] if len(result) > 0 else None
                season = result[1] if len(result) > 1 else 1
                latest_ep = result[2] if len(result) > 2 else None
                eps = result[3] if len(result) > 3 else []
                
                if title and eps:
                    ep_url = eps[-1][2] if isinstance(eps[-1], tuple) else eps[-1].get('url', url)
                    
                    task = Task(uid, cid, "episode", content_key, ep_url)
                    task.series_name = title
                    task.episode = latest_ep
                    task.site_key = 'rareanimes'
                    
                    success, message = add_to_queue('single', task, st)
                    await msg.edit(f"""
🎭 **RareAnimes**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title}**
📔 **Episode:** {latest_ep}

📥 **{message}**
━━━━━━━━━━━━━━━━━━━━━━
""")
                    return

        # ==========================================
        # 🌏 TOONWORLD4ALL URL
        # ==========================================
        if site_key == 'toonworld4all':
            await msg.edit(
                "🌏 **ToonWorld4All Detected!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔍 Fetching series info..."
            )

            finder = ToonWorld4AllFinder(st)
            title, season, latest_ep = await finder.get_info(url)

            if not title:
                return await msg.edit(
                    "❌ **Could not fetch series info**\n\n"
                    "Make sure the URL is a ToonWorld4All **series page**.\n"
                    "_Example:_ `https://toonworld4all.me/show-name/`"
                )

            if not latest_ep:
                return await msg.edit(
                    f"❌ **No episodes found for:** {title}\n\n"
                    "The page may not have episodes listed yet."
                )

            task = Task(uid, cid, "episode", content_key, url)
            task.series_name = title
            task.episode = latest_ep
            task.site_key = 'toonworld4all'

            success, message = add_to_queue('single', task, st)

            await msg.edit(
                f"🌏 **ToonWorld4All**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎬 **{title}**\n"
                f"🏝️ **Season:** {season}\n"
                f"📔 **Latest Episode:** {latest_ep}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📥 **{message}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            return

        # ==========================================
        # ❌ TRULY UNKNOWN URL
        # ==========================================
        await msg.edit(f"""
❌ **Unknown URL Format**
━━━━━━━━━━━━━━━━━━━━━━

🔗 `{url[:50]}...`

━━━━━━━━━━━━━━━━━━━━━━
📋 **Supported Sites:**

🎌 **Toono** — toono.app/series/...
🎭 **RareAnimes** — rareanimes.app/...
🎬 **AnimeDubHindi** — animedubhindi.me/...
🇮🇳 **HindiAnimeZone** — hindianimezone.com/...
🌏 **ToonWorld4All** — toonworld4all.me/show-name/
📦 **GDFlix** — gdflix.io/file/... (or gdflix.dev)
⚡ **Swift Player** — swift.multiquality.click/...

━━━━━━━━━━━━━━━━━━━━━━
""")

    except Exception as e:
        print(f"URL Error: {e}")
        traceback.print_exc()
        await msg.edit(f"❌ **Error:** {str(e)[:100]}\n\n🔄 Please try again")

# ==========================================
# COMMANDS - ORIGINAL /start MESSAGE
# ==========================================
@bot.on_message(filters.command("start"))
async def cmd_start(c, m):
    uid = m.from_user.id
    name = m.from_user.first_name
    
    # Check force subscription
    is_joined, fsub_markup = await check_force_sub(c, uid)
    
    if not is_joined:
        return await m.reply(f"""
🔒 **Access Restricted!**

━━━━━━━━━━━━━━━━━━━━━━
Hi **{name}**! 👋

To use this bot, please join our channel first:

━━━━━━━━━━━━━━━━━━━━━━
👇 **Click button below to join:**
""", reply_markup=fsub_markup)
    
    # Register user
    if uid not in db['users']:
        db['users'][uid] = {'joined': datetime.now().isoformat(), 'interval': 3}
        save_db()

    # Check premium status
    is_premium_user = is_premium(uid)
    
    # Role-based buttons
    keyboard = get_help_buttons(uid)
    
    # Premium status text
    if is_owner(uid):
        premium_status = "👑 **Owner** (Lifetime)"
    elif is_admin(uid):
        premium_status = "⚔️ **Admin** (Lifetime)"
    elif is_premium_user:
        days_left = get_premium_days_left(uid)
        premium_status = f"💎 **Premium** ({days_left} days left)"
    else:
        premium_status = "🆓 **Free User**"

    # Non-premium users
    if not is_premium_user:
        return await m.reply(f"""
🎌 **ANIME AUTO DOWNLOADER**
━━━━━━━━━━━━━━━━━━━━━━━━━━

Hey **{name}**! 👋

🔒 **Premium Access Required**

This bot is available for premium members only.

💎 **Premium Features:**
├ 🎬 Auto anime monitoring
├ 📥 Batch download (up to 15 eps)
├ 🖼️ Custom thumbnails
├ ⚡ Fast parallel downloads
├ 🎯 All quality options (360p–1080p)
├ 🔔 New episode alerts
├ ✍️ Custom captions
└ 📤 Auto channel uploading

📩 **Get Access:** @Dark_isekai
🌐 **Community:** https://t.me/Animex_Studio

━━━━━━━━━━━━━━━━━━━━━━━━━━
     ⚜ **Developed by Senpai DxD** ⚜
""", reply_markup=keyboard)

    # Premium users
    await m.reply(f"""
🎌 **ANIME AUTO DOWNLOADER**
━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome back, **{name}**! 👋
{role(uid)}  |  {premium_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **Auto URL Detection:** Active
⏳ **Cooldown:** {COOLDOWN_TIME}s per request
🌐 **Support:** @Animex_Studio
━━━━━━━━━━━━━━━━━━━━━━━━━━

Just send an anime URL and I'll handle the rest!

👇 Use the buttons below to navigate:
""", reply_markup=keyboard)
    

# ==========================================
# FORCE SUB CALLBACK HANDLER
# ==========================================
@bot.on_callback_query(filters.regex("^check_fsub$"))
async def cb_check_fsub(c, q):
    """Handle 'Joined? Click Here' button"""
    uid = q.from_user.id
    name = q.from_user.first_name
    
    is_joined, fsub_markup = await check_force_sub(c, uid)
    
    if not is_joined:
        return await q.answer("❌ Please join the channel first!", show_alert=True)
    
    # User is now a member!
    await q.message.delete()
    
    # Register user
    if uid not in db['users']:
        db['users'][uid] = {'joined': datetime.now().isoformat(), 'interval': 3}
        save_db()
    
    is_premium_user = is_premium(uid)
    keyboard = get_help_buttons(uid)
    
    if is_owner(uid):
        premium_status = "👑 **Owner** (Lifetime)"
    elif is_admin(uid):
        premium_status = "⚔️ **Admin** (Lifetime)"
    elif is_premium_user:
        days_left = get_premium_days_left(uid)
        premium_status = f"💎 **Premium** ({days_left} days left)"
    else:
        premium_status = "🆓 **Free User**"
    
    if not is_premium_user:
        await c.send_message(uid, f"""
╔══════════════════════╗
║ 🎌 ANIME AUTO DOWNLOADER ║
╚══════════════════════╝

✅ **Verification Successful!**

Namaste **{name}**! 👋

━━━━━━━━━━━━━━━━━━━━━━
⚠️ **PREMIUM REQUIRED**
━━━━━━━━━━━━━━━━━━━━━━

🔒 This bot is **Premium Only**

💎 **Get Access:**
👉 @Dark_isekai

༺═━━━━━━ {{ ⚜ }} ━━━━━━═༻
     **👑 Developed by Senpai DxD**
༺═━━━━━━ {{ ⚜ }} ━━━━━━═༻
""", reply_markup=keyboard)
    else:
        await c.send_message(uid, f"""
╔══════════════════════╗
║ 🎌 ANIME AUTO DOWNLOADER ║
╚══════════════════════╝

✅ **Verification Successful!**

Namaste **{name}**! 👋
{role(uid)}

━━━━━━━━━━━━━━━━━━━━━━
💎 {premium_status}
━━━━━━━━━━━━━━━━━━━━━━

🌐 **Website Support:** https://t.me/Animex_Studio
⏳ **Cooldown:** {COOLDOWN_TIME}s

👇 **Choose an option below:**

༺═━━━━━━ {{ ⚜ }} ━━━━━━═༻
     **👑 Developed by Senpai DxD**
༺═━━━━━━ {{ ⚜ }} ━━━━━━═༻
""", reply_markup=keyboard)
    
    await q.answer("✅ Verified!")

# ==========================================
# BUTTON CALLBACK HANDLER
# ==========================================
@bot.on_callback_query(filters.regex(r"^(help_user|help_admin|help_owner|help_master|back_main)$"))
async def button_handler(c, q):
    """Handle help button clicks"""
    uid = q.from_user.id
    data = q.data

    back_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main")]
    ])

    user_extra_btns = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Rename", callback_data="rename_menu"),
            InlineKeyboardButton("🏷️ Metadata", callback_data="meta_menu")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_main")]
    ])

    try:
        if data == "help_user":
            await q.message.edit(HELP_USER, reply_markup=user_extra_btns)

        elif data == "help_admin":
            if is_admin(uid) or is_owner(uid) or is_master(uid):
                await q.message.edit(HELP_ADMIN, reply_markup=back_btn)
            else:
                await q.answer("❌ Admin access required!", show_alert=True)

        elif data == "help_owner":
            if is_owner(uid) or is_master(uid):
                await q.message.edit(HELP_OWNER, reply_markup=back_btn)
            else:
                await q.answer("❌ Owner access required!", show_alert=True)

        elif data == "back_main":
            keyboard = get_help_buttons(uid)

            if is_owner(uid):
                premium_status = "👑 **Owner** (Lifetime)"
            elif is_admin(uid):
                premium_status = "⚔️ **Admin** (Lifetime)"
            elif is_master(uid):
                premium_status = "🔱 **Master** (Full Access)"
            elif is_premium(uid):
                days_left = get_premium_days_left(uid)
                premium_status = f"💎 **Premium** ({days_left} days left)"
            else:
                premium_status = "🆓 **Free User**"

            name = q.from_user.first_name

            await q.message.edit(f"""
🎌 **ANIME AUTO DOWNLOADER**
━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome, **{name}**! 👋
{role(uid)}  |  {premium_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ **Auto URL Detection:** Active
⏳ **Cooldown:** {COOLDOWN_TIME}s
🌐 **Support:** @Animex_Studio
━━━━━━━━━━━━━━━━━━━━━━━━━━

👇 Use the buttons below to navigate:
""", reply_markup=keyboard)

        await q.answer()

    except Exception as e:
        print(f"Callback error: {e}")
        await q.answer("❌ Error occurred!", show_alert=True)

# ==========================================
# 🔄 REFRESH / LIST / REMOVE CALLBACKS
# ==========================================

@bot.on_callback_query(filters.regex("^refresh_status$"))
async def cb_refresh_status(c, q):
    uid = q.from_user.id
    try:
        await q.answer("⏳ Refreshing...")
        refresh_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
            InlineKeyboardButton("📋 My List", callback_data="refresh_list"),
        ]])
        await q.edit_message_text(_build_status_text(uid), reply_markup=refresh_btn)
    except Exception as e:
        if not isinstance(e, MessageNotModified):
            print(f"Refresh status callback error: {type(e).__name__}: {e}")
            try:
                await q.answer(f"❌ Refresh failed: {str(e)[:40]}", show_alert=True)
            except Exception:
                pass

@bot.on_callback_query(filters.regex("^refresh_gstatus$"))
async def cb_refresh_gstatus(c, q):
    try:
        await q.answer("⏳ Refreshing...")
        refresh_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_gstatus")
        ]])
        await q.edit_message_text(_build_gstatus_text(), reply_markup=refresh_btn)
    except Exception as e:
        if not isinstance(e, MessageNotModified):
            print(f"Refresh global status callback error: {type(e).__name__}: {e}")
            try:
                await q.answer(f"❌ Refresh failed: {str(e)[:40]}", show_alert=True)
            except Exception:
                pass

@bot.on_callback_query(filters.regex("^refresh_list$"))
async def cb_refresh_list(c, q):
    uid = q.from_user.id
    try:
        await q.answer("⏳ Refreshing...")
        msg, btns, _ = _build_list_msg_and_btns(uid)
        await q.edit_message_text(msg, reply_markup=btns)
    except Exception as e:
        if not isinstance(e, MessageNotModified):
            print(f"Refresh list callback error: {type(e).__name__}: {e}")
            try:
                await q.answer(f"❌ Refresh failed: {str(e)[:40]}", show_alert=True)
            except Exception:
                pass

@bot.on_callback_query(filters.regex(r"^remove_anime_(\d+)$"))
async def cb_remove_anime(c, q):
    uid = q.from_user.id
    try:
        idx = int(q.data.split("_")[2]) - 1
        us = [(k, d) for k, d in db['monitored'].items()
              if any(s['user_id'] == uid for s in d['subscribers'])]
        if idx < 0 or idx >= len(us):
            await q.answer("❌ Anime not found!", show_alert=True)
            return
        k, d = us[idx]
        name = d['series_name']
        d['subscribers'] = [x for x in d['subscribers'] if x['user_id'] != uid]
        if not d['subscribers']:
            del db['monitored'][k]
        save_db()
        await q.answer(f"✅ Removed: {name}")
        # Refresh the list in-place
        msg, btns, _ = _build_list_msg_and_btns(uid)
        await q.message.edit(msg, reply_markup=btns)
    except Exception as e:
        await q.answer(f"❌ {str(e)[:50]}", show_alert=True)

@bot.on_message(filters.command("set"))
async def cmd_set(c, m):
    uid = m.from_user.id
    if is_banned(uid): 
        return await m.reply("🚫 Banned")
    if not await premium_check(m): 
        return
    if not await cooldown_check(m): 
        return
    if len(m.command) < 2: 
        return await m.reply("❌ **Usage:** `/set URL`")

    url = m.command[1]
    
    # Detect website
    site_key, site_data = detect_website(url)
    
    if not site_key:
        return await m.reply(f"""
❌ **Unsupported Website**
━━━━━━━━━━━━━━━━━━━━━━

📋 **Supported Sites:**
• toono.app/series/...
• rareanimes.app/...
• animedubhindi.me/...
• toonworld4all.me/show-name/

━━━━━━━━━━━━━━━━━━━━━━
""")
    
    update_cooldown(uid)
    st = Status(c, m.chat.id)
    msg = await st.create(f"{site_data['name']} **Detected!**\n\n⏳ Setting up...")

    try:
        title = None
        latest_ep = None
        season = 1
        monitor_url = None
        episode_url = None
        episode_data = None
        
        # ==========================================
        # 🎬 ANIMEDUBHINDI
        # ==========================================
        if site_key == 'animedubhindi':
            finder = AnimeDubHindiFinder(st)
            result = await finder.get_info(url)
            
            title = result[0] if len(result) > 0 else None
            season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            redirect_url = result[3] if len(result) > 3 else None
            episodes = result[4] if len(result) > 4 else {}
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not redirect_url:
                return await msg.edit("❌ **Could not find episode page**")
            
            # Monitor the redirect URL (episode page)
            monitor_url = redirect_url
            
            if episodes and latest_ep and latest_ep in episodes:
                episode_data = episodes[latest_ep]
        
        # ==========================================
        # 🎭 RAREANIMES
        # ==========================================
        elif site_key == 'rareanimes':
            await msg.edit(f"""
🎭 **RareAnimes**
━━━━━━━━━━━━━━━━━━━━━━

🔍 Scanning for episodes...
""")
            
            finder = RareAnimesFinder(st)
            result = await finder.get_info(url)
            
            # Safe unpack
            title = result[0] if len(result) > 0 else None
            season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            eps = result[3] if len(result) > 3 else []
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not eps:
                return await msg.edit("❌ **No episodes found!**")
            
            # Monitor URL is the main page
            monitor_url = url
            
            # Find latest episode URL (codedew URL - DON'T resolve, pass directly)
            episode_url = None
            for item in eps:
                if isinstance(item, tuple) and len(item) >= 3:
                    s, e, u = item[0], item[1], item[2]
                    if e == latest_ep:
                        episode_url = u
                        break
            
            # Fallback
            if not episode_url and eps:
                last = eps[-1]
                if isinstance(last, tuple) and len(last) >= 3:
                    episode_url = last[2]
                    latest_ep = last[1]
                        
        # ==========================================
        # 🎌 TOONO (EXISTING)
        # ==========================================
        elif site_key == 'toono':
            if "/series/" not in url:
                return await m.reply("❌ **Invalid Toono URL**\n\nUse: `/set https://toono.in/series/anime-name`")
            
            f = Finder(st)
            title, season, latest_ep, eps = await f.get_info(url)

            if not title:
                return await msg.edit("❌ **Could not fetch series info**")

            if not eps:
                return await msg.edit("❌ **No episodes found!**")

            # Monitor the series URL
            monitor_url = url
            
            # Find latest episode URL
            for s, e, u in eps:
                if s == season and e == latest_ep:
                    episode_url = u
                    break
            
            if not episode_url and eps:
                episode_url = eps[-1][2]
                season = eps[-1][0]
                latest_ep = eps[-1][1]
        
        # ==========================================
        # 🇮🇳 HINDIANIMEZONE
        # ==========================================
        elif site_key == 'hindianimezone':
            finder = HindiAnimeZoneFinder(st)
            title, season, latest_ep = await finder.get_info(url)

            if not title or title == "Unknown Anime":
                return await msg.edit(
                    "❌ **Could not fetch series info**\n\n"
                    "Make sure the URL is a HindiAnimeZone **series page** (not an episode page).\n"
                    "_Example:_ `https://hindianimezone.com/anime-name/`"
                )

            if not latest_ep:
                return await msg.edit(
                    f"❌ **No episodes found for:** {title}\n\n"
                    "The page may not list episodes yet."
                )

            monitor_url = url
            episode_url = url   # process_task uses series URL; extract_all finds the right episode

        # ==========================================
        # 🌏 TOONWORLD4ALL
        # ==========================================
        elif site_key == 'toonworld4all':
            finder = ToonWorld4AllFinder(st)
            title, season, latest_ep = await finder.get_info(url)

            if not title:
                return await msg.edit(
                    "❌ **Could not fetch series info**\n\n"
                    "Make sure the URL is a ToonWorld4All **series page**.\n"
                    "_Example:_ `https://toonworld4all.me/show-name/`"
                )

            if not latest_ep:
                return await msg.edit(
                    f"❌ **No episodes found for:** {title}\n\n"
                    "The page may not list episodes yet."
                )

            monitor_url = url
            episode_url = url

        else:
            return await msg.edit("❌ **This URL type doesn't support monitoring**")
        
        # ==========================================
        # CHECK DUPLICATE
        # ==========================================
        key = f"{site_key}_{re.sub(r'[^a-z0-9]', '', title.lower())}"
        
        for k, d in db['monitored'].items():
            if k == key:
                for sub in d['subscribers']:
                    if sub['user_id'] == uid:
                        return await msg.edit(f"⚠️ **Already monitoring:** {title}")
        
        # ==========================================
        # SAVE TO DATABASE
        # ==========================================
        intv = db['users'].get(uid, {}).get('interval', 3)
        
        if key in db['monitored']:
            # Add subscriber to existing
            if not any(s['user_id'] == uid for s in db['monitored'][key]['subscribers']):
                db['monitored'][key]['subscribers'].append({'user_id': uid, 'chat_id': m.chat.id})
                save_db()
            return await msg.edit(f"✅ **Added to existing:** {title}")
        
        db['monitored'][key] = {
            'series_name': title,
            'series_url': url,
            'monitor_url': monitor_url,  # URL to check for new episodes
            'site_key': site_key,
            'last_episode': latest_ep or 0,
            'last_season': season or 1,
            'interval': intv,
            'last_check': 0,
            'subscribers': [{'user_id': uid, 'chat_id': m.chat.id}]
        }
        save_db()

        await msg.edit(f"""
✅ **Monitoring Started!**
━━━━━━━━━━━━━━━━━━━━━━

{site_data['name']}
🎬 **{title}**

━━━━━━━━━━━━━━━━━━━━━━
🏝️ **Season:** {season or 1}
📔 **Latest Episode:** {latest_ep or 0}
⏱️ **Check Interval:** {intv} min

━━━━━━━━━━━━━━━━━━━━━━
📥 **Downloading latest episode...**
━━━━━━━━━━━━━━━━━━━━━━
""")

        # Download latest episode
        if episode_url or episode_data:
            task = Task(uid, m.chat.id, "episode", f"{key}_ep{latest_ep}", episode_url or url)
            task.series_name = title
            task.episode = latest_ep
            
            if episode_data:
                task.episode_data = episode_data
            
            add_to_queue('single', task, st)

    except Exception as e:
        print(f"Set Error: {e}")
        traceback.print_exc()
        await msg.edit(f"❌ **Error:** {str(e)[:100]}")

@bot.on_message(filters.command("batch"))
async def cmd_batch(c, m):
    uid = m.from_user.id
    if is_banned(uid): 
        return await m.reply("🚫 Banned")
    if not await premium_check(m): 
        return
    if not await cooldown_check(m): 
        return
    
    if len(m.command) < 3: 
        return await m.reply(f"""
❌ **Batch Download Format**
━━━━━━━━━━━━━━━━━━━━━━

📝 **Usage:**
`/batch URL S01 Ep 1-5`
`/batch URL 1-5`

━━━━━━━━━━━━━━━━━━━━━━
📋 **Examples:**

🎌 **Toono:**
`/batch https://toono.app/series/anime S01 Ep 1-10`

🎭 **RareAnimes:**
`/batch https://rareanimes.app/anime-name/ 3-8`

🎬 **AnimeDubHindi:**
`/batch https://animedubhindi.me/anime/ Ep 1-5`

🇮🇳 **HindiAnimeZone:**
`/batch https://hindianimezone.me/anime-name/ S01 Ep 1-5`

━━━━━━━━━━━━━━━━━━━━━━
⚠️ **Max {MAX_BATCH} episodes per batch**
━━━━━━━━━━━━━━━━━━━━━━
""")

    url = m.command[1]
    
    # Detect website
    site_key, site_data = detect_website(url)
    
    if not site_key:
        # Try to detect from URL content
        url_lower = url.lower()
        if "rareanimes" in url_lower or "raretoons" in url_lower:
            site_key = 'rareanimes'
            site_data = SUPPORTED_WEBSITES.get('rareanimes', {'name': '🎭 RareAnimes'})
        elif "animedubhindi" in url_lower:
            site_key = 'animedubhindi'
            site_data = SUPPORTED_WEBSITES.get('animedubhindi', {'name': '🎬 AnimeDubHindi'})
        elif "toono" in url_lower:
            site_key = 'toono'
            site_data = SUPPORTED_WEBSITES.get('toono', {'name': '🎌 Toono'})
        else:
            return await m.reply(f"""
❌ **Unsupported Website**
━━━━━━━━━━━━━━━━━━━━━━

📋 **Supported Sites:**
• toono.app
• rareanimes.app
• animedubhindi.me

━━━━━━━━━━━━━━━━━━━━━━
""")

    # Parse season and episode range
    full_args = " ".join(m.command[2:])
    
    season_num = None
    start_ep = None
    end_ep = None
    
    # Parse season (S01, S1, Season 1, etc.)
    season_match = re.search(r'[Ss](\d+)|[Ss]eason\s*(\d+)', full_args)
    if season_match:
        season_num = int(season_match.group(1) or season_match.group(2))
    
    # Parse episode range (Ep 1-5, 1-5, 1 to 5, etc.)
    ep_match = re.search(r'(?:[Ee]p\s*)?(\d+)\s*(?:-|to)\s*(\d+)', full_args, re.I)
    if ep_match:
        start_ep = int(ep_match.group(1))
        end_ep = int(ep_match.group(2))
        if end_ep < start_ep:
            start_ep, end_ep = end_ep, start_ep
    else:
        # Try simple format: 1-5
        try:
            parts = m.command[2].replace(" ", "").split("-")
            if len(parts) == 2:
                start_ep = int(parts[0])
                end_ep = int(parts[1])
                if end_ep < start_ep:
                    start_ep, end_ep = end_ep, start_ep
        except:
            pass

    if start_ep is None or end_ep is None:
        return await m.reply(f"""
❌ **Invalid Episode Range**
━━━━━━━━━━━━━━━━━━━━━━

📝 **Correct Formats:**
• `1-5` or `Ep 1-5`
• `1 to 5`
• `S01 Ep 1-5`

━━━━━━━━━━━━━━━━━━━━━━
""")

    total_requested = end_ep - start_ep + 1
    if total_requested > MAX_BATCH:
        return await m.reply(f"❌ **Max {MAX_BATCH} episodes allowed!**\n\nYou requested: {total_requested}")

    update_cooldown(uid)
    st = Status(c, m.chat.id)
    
    site_name = site_data.get('name', '🔍 Unknown')
    msg = await st.create(f"{site_name} **Batch Processing...**\n\n⏳ Fetching episodes...")

    try:
        title = None
        download_eps = []
        
        # ==========================================
        # 🎬 ANIMEDUBHINDI BATCH
        # ==========================================
        if site_key == 'animedubhindi':
            finder = AnimeDubHindiFinder(st)
            result = await finder.get_info(url)
            
            title = result[0] if len(result) > 0 else None
            detected_season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            redirect_url = result[3] if len(result) > 3 else None
            episodes = result[4] if len(result) > 4 else {}
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not episodes:
                return await msg.edit("❌ **No episodes found!**")
            
            if season_num is None:
                season_num = detected_season or 1
            
            # Filter episodes in range
            for ep_num in range(start_ep, end_ep + 1):
                if ep_num in episodes:
                    download_eps.append((ep_num, episodes[ep_num]))
                    print(f"   ✓ Episode {ep_num} found")

        # ==========================================
        # 🇮🇳 HINDIANIMEZONE BATCH
        # ==========================================
        elif site_key == 'hindianimezone':
            finder = HindiAnimeZoneFinder(st)
            title, detected_season, latest_ep = await finder.get_info(url)

            if not title:
                return await msg.edit("❌ **Could not fetch series info**")

            if latest_ep is None:
                return await msg.edit("❌ **No episodes found!**")

            if season_num is None:
                season_num = detected_season or 1

            # HAZ uses the series page for episode extraction. Each batch
            # child passes its episode number into the existing HAZ resolver.
            for ep_num in range(start_ep, end_ep + 1):
                if ep_num <= latest_ep:
                    download_eps.append((ep_num, url))
                    print(f"   ✓ Episode {ep_num} available")
        
        # ==========================================
        # 🎭 RAREANIMES BATCH
        # ==========================================
        elif site_key == 'rareanimes':
            finder = RareAnimesFinder(st)
            result = await finder.get_info(url)
            
            title = result[0] if len(result) > 0 else None
            detected_season = result[1] if len(result) > 1 else 1
            latest_ep = result[2] if len(result) > 2 else None
            eps = result[3] if len(result) > 3 else []
            
            if not title:
                return await msg.edit("❌ **Could not fetch series info**")
            
            if not eps:
                return await msg.edit("❌ **No episodes found!**")
            
            if season_num is None:
                season_num = detected_season or 1
            
            # Filter episodes in range
            for item in eps:
                ep_num = None
                ep_url = None
                
                if isinstance(item, tuple):
                    if len(item) >= 3:
                        ep_num = item[1]
                        ep_url = item[2]
                    elif len(item) == 2:
                        ep_num = item[0]
                        ep_url = item[1]
                elif isinstance(item, dict):
                    ep_num = item.get('episode', 0)
                    ep_url = item.get('url', '')
                
                if ep_num and ep_url and start_ep <= ep_num <= end_ep:
                    download_eps.append((ep_num, ep_url))
                    print(f"   ✓ Episode {ep_num} found")
        
        # ==========================================
        # 🎌 TOONO BATCH
        # ==========================================
        elif site_key == 'toono':
            if "/series/" not in url:
                return await msg.edit("❌ **Toono batch requires series URL**\n\nExample: `https://toono.in/series/anime-name`")
            
            f = Finder(st)
            title, last_season, latest_ep, all_eps = await f.get_info(url)

            if not title:
                return await msg.edit("❌ **Could not fetch series info**")

            if not all_eps:
                return await msg.edit("❌ **No episodes found!**")
            
            if season_num is None:
                season_num = last_season or 1
            
            # Filter by season and range
            for s, e, u in all_eps:
                if s == season_num and start_ep <= e <= end_ep:
                    download_eps.append((e, u))
                    print(f"   ✓ S{s}E{e} found")
        
        else:
            return await msg.edit("❌ **Batch not supported for this site**")
        
        # Sort episodes by number
        download_eps.sort(key=lambda x: x[0])
        
        if not download_eps:
            # Show what's available
            available_str = ""
            
            if site_key == 'animedubhindi' and episodes:
                available_eps = sorted(episodes.keys())
                if len(available_eps) > 10:
                    available_str = f"Ep {available_eps[0]}-{available_eps[-1]}"
                else:
                    available_str = f"Ep {', '.join(map(str, available_eps))}"
            elif site_key == 'hindianimezone' and latest_ep:
                available_str = f"Ep 1-{latest_ep}"
            elif site_key == 'rareanimes' and eps:
                ep_nums = []
                for item in eps:
                    if isinstance(item, tuple) and len(item) >= 2:
                        ep_nums.append(item[1])
                    elif isinstance(item, dict):
                        ep_nums.append(item.get('episode', 0))
                ep_nums = sorted([e for e in ep_nums if e > 0])
                if ep_nums:
                    available_str = f"Ep {ep_nums[0]}-{ep_nums[-1]}"
            elif site_key == 'toono' and all_eps:
                season_eps = [e for s, e, u in all_eps if s == season_num]
                if season_eps:
                    available_str = f"S{season_num} Ep {min(season_eps)}-{max(season_eps)}"
            
            return await msg.edit(f"""
❌ **Episodes {start_ep}-{end_ep} not found!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{title or 'Unknown'}**
🏝️ **Season:** {season_num}

━━━━━━━━━━━━━━━━━━━━━━
✅ **Available:** {available_str or 'Unknown'}

💡 Check the correct episode range!
━━━━━━━━━━━━━━━━━━━━━━
""")
        
        # Check missing episodes
        found_nums = [ep[0] for ep in download_eps]
        missing = [i for i in range(start_ep, end_ep + 1) if i not in found_nums]
        
        missing_msg = ""
        if missing:
            if len(missing) <= 5:
                missing_msg = f"\n⚠️ **Missing:** Ep {', '.join(map(str, missing))}"
            else:
                missing_msg = f"\n⚠️ **Missing:** {len(missing)} episodes"
        
        # Create batch task
        content_key = f"batch_{site_key}_{hash(url)}_{start_ep}_{end_ep}"
        task = Task(uid, m.chat.id, "batch", content_key, url)
        task.series_name = title
        task.site_key = site_key
        
        # Add to queue
        success, message = add_to_queue('batch', task, st, download_eps)

        await msg.edit(f"""
✅ **Batch Queued!**
━━━━━━━━━━━━━━━━━━━━━━

{site_name}
🎬 **{title}**

━━━━━━━━━━━━━━━━━━━━━━
🏝️ **Season:** {season_num}
📔 **Episodes:** {start_ep} to {end_ep}
🎥 **Found:** {len(download_eps)} episodes{missing_msg}

━━━━━━━━━━━━━━━━━━━━━━
📥 **{message}**

⏳ Download starting soon...
━━━━━━━━━━━━━━━━━━━━━━
""")

    except Exception as e:
        print(f"Batch Error: {e}")
        traceback.print_exc()
        await msg.edit(f"❌ **Error:** {str(e)[:100]}")

def _build_list_msg_and_btns(uid):
    """Build the anime list message + inline keyboard for a user."""
    us = [d for d in db['monitored'].values() if any(s['user_id'] == uid for s in d['subscribers'])]
    if not us:
        msg = (
            "📭 **No Anime Monitored**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You haven't added any anime yet.\n\n"
            "💡 Use `/set URL` to start monitoring.\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        btns = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_list")
        ]])
        return msg, btns, []

    lines = "📺 **Your Monitored Anime**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    buttons = []
    for i, s in enumerate(us, 1):
        ep  = s.get('last_episode', 0)
        season = s.get('last_season', 1)
        name = s['series_name']
        lines += f"**{i}.** 🎌 {name}\n    └ S{str(season).zfill(2)} • Ep {ep}\n\n"
        buttons.append([
            InlineKeyboardButton(f"❌ Remove #{i} {name[:22]}", callback_data=f"remove_anime_{i}")
        ])

    lines += f"━━━━━━━━━━━━━━━━━━━━━━\n📊 Total: {len(us)} anime"
    buttons.append([InlineKeyboardButton("🔄 Refresh List", callback_data="refresh_list")])
    return lines, InlineKeyboardMarkup(buttons), us

@bot.on_message(filters.command("list"))
async def cmd_list(c, m):
    uid = m.from_user.id
    if not await premium_check(m): return
    msg, btns, _ = _build_list_msg_and_btns(uid)
    await m.reply(msg, reply_markup=btns)

@bot.on_message(filters.command("del"))
async def cmd_del(c, m):
    uid = m.from_user.id
    if not await premium_check(m): return  # ✅ PEHLE
    us = [(k, d) for k, d in db['monitored'].items() if any(s['user_id'] == uid for s in d['subscribers'])]
    if not us: return await m.reply("📺 Nothing")
    if len(m.command) < 2: return await m.reply("❌ `/del <num>`")
    try: num = int(m.command[1])
    except: return await m.reply("❌ Invalid")
    if num < 1 or num > len(us): return await m.reply("❌ Invalid")

    k, d = us[num - 1]
    d['subscribers'] = [x for x in d['subscribers'] if x['user_id'] != uid]
    if not d['subscribers']: del db['monitored'][k]
    save_db()
    await m.reply(f"✅ Removed: **{d['series_name']}**")

@bot.on_message(filters.command("website"))
async def cmd_website(c, m):
    """Show all monitored websites and their episode pages"""
    uid = m.from_user.id
    if not await premium_check(m): 
        return
    
    # Get user's monitored anime
    user_monitors = []
    for key, data in db['monitored'].items():
        for sub in data['subscribers']:
            if sub['user_id'] == uid:
                user_monitors.append(data)
                break
    
    if not user_monitors:
        return await m.reply(f"""
📺 **No Monitored Anime**
━━━━━━━━━━━━━━━━━━━━━━

You haven't set any anime for monitoring.

💡 **How to monitor:**
`/set URL`

📋 **Supported Sites:**
• toono.app
• rareanimes.app
• animedubhindi.me

━━━━━━━━━━━━━━━━━━━━━━
""")
    
    text = """📺 **YOUR MONITORED ANIME**
━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, data in enumerate(user_monitors, 1):
        site_key = data.get('site_key', 'unknown')
        site_data = SUPPORTED_WEBSITES.get(site_key, {'name': '🔗 Unknown'})
        
        title = data.get('series_name', 'Unknown')
        season = data.get('last_season', 1)
        episode = data.get('last_episode', 0)
        monitor_url = data.get('monitor_url', data.get('series_url', 'N/A'))
        
        text += f"""**{i}. {title}**
   {site_data['name']}
   🏝️ Season: {season} | 📺 Episode: {episode}
   🔗 `{monitor_url[:50]}...`

"""
    
    text += f"""━━━━━━━━━━━━━━━━━━━━━━
📊 **Total:** {len(user_monitors)} anime

💡 **Commands:**
• `/list` - Simple list
• `/del NUM` - Remove anime
• `/time MINS` - Set check interval
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await m.reply(text)

@bot.on_message(filters.command("time"))
async def cmd_time(c, m):
    uid = m.from_user.id
    if len(m.command) < 2:
        cur = db['users'].get(uid, {}).get('interval', 3)
        return await m.reply(f"⏰ Current: {cur} min")
    if not await premium_check(m): return
    try: mins = int(m.command[1])
    except: return await m.reply("❌ Invalid")
    if mins < MIN_INTERVAL or mins > MAX_INTERVAL: return await m.reply(f"❌ {MIN_INTERVAL}-{MAX_INTERVAL}")

    if uid not in db['users']: db['users'][uid] = {}
    db['users'][uid]['interval'] = mins
    for k, d in db['monitored'].items():
        if any(s['user_id'] == uid for s in d['subscribers']):
            db['monitored'][k]['interval'] = mins
    save_db()
    await m.reply(f"✅ Interval: {mins} min")

@bot.on_message(filters.command("cleanup"))
async def cmd_cleanup_user(c, m):
    """User apna data reset kar sakta hai - Premium nahi jayega"""
    uid = m.from_user.id
    
    if is_banned(uid):
        return await m.reply("🚫 Banned")
    
    # Show confirmation
    btns = [
        [InlineKeyboardButton("⚠️ HAAN, RESET KARO", callback_data=f"cleanup_confirm_{uid}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cleanup_cancel")]
    ]
    
    # Count user's data
    monitored_count = len([d for d in db['monitored'].values() if any(s['user_id'] == uid for s in d['subscribers'])])
    thumb_count = len(db.get('thumbnails', {}).get(uid, {}))
    has_caption = uid in db.get('captions', {})
    channel_count = len(db.get('channels', {}).get(uid, []))
    has_metadata = uid in db.get('metadata', {})
    rename_count = len(db.get('rename_rules', {}).get(uid, []))
    
    await m.reply(f"""
⚠️ **DATA RESET CONFIRMATION**
━━━━━━━━━━━━━━━━━━━━━━

Kya aap apna **SABHI DATA** reset karna chahte ho?

━━━━━━━━━━━━━━━━━━━━━━
📋 **REMOVE HOGA:**
━━━━━━━━━━━━━━━━━━━━━━
🎬 Monitored Anime: **{monitored_count}**
🖼️ Thumbnails: **{thumb_count}**
📝 Custom Caption: **{'Yes' if has_caption else 'No'}**
📢 Linked Channels: **{channel_count}**
🏷️ Metadata Tag: **{'Yes' if has_metadata else 'No'}**
✏️ Rename Rules: **{rename_count}**

━━━━━━━━━━━━━━━━━━━━━━
✅ **SAFE RAHEGA:**
━━━━━━━━━━━━━━━━━━━━━━
💎 Premium Status: Safe
👤 Account: Safe

━━━━━━━━━━━━━━━━━━━━━━
⚠️ **YEH ACTION UNDO NAHI HO SAKTA!**
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))


@bot.on_callback_query(filters.regex(r"^cleanup_"))
async def cb_cleanup(c, q):
    uid = q.from_user.id
    data = q.data
    
    if data == "cleanup_cancel":
        return await q.message.edit("❌ **Reset Cancelled**")
    
    if data.startswith("cleanup_confirm_"):
        target_uid = int(data.split("_")[2])
        
        # Security check
        if uid != target_uid and not is_owner(uid):
            return await q.answer("❌ You can only reset your own data!", show_alert=True)
        
        await q.message.edit("⏳ **Resetting data...**")
        
        removed = {
            'anime': 0,
            'thumbs': 0,
            'caption': False,
            'channels': 0,
            'metadata': False,
            'rename': 0
        }
        
        # Remove monitored anime
        for key, data in list(db['monitored'].items()):
            data['subscribers'] = [s for s in data['subscribers'] if s['user_id'] != target_uid]
            if not data['subscribers']:
                removed['anime'] += 1
                del db['monitored'][key]
            elif any(s['user_id'] == target_uid for s in data.get('subscribers', [])):
                removed['anime'] += 1
        
        # Remove thumbnails
        if target_uid in db.get('thumbnails', {}):
            removed['thumbs'] = len(db['thumbnails'][target_uid])
            del db['thumbnails'][target_uid]
        
        if target_uid in db.get('thumb_last_used', {}):
            del db['thumb_last_used'][target_uid]
        
        # Remove caption
        if target_uid in db.get('captions', {}):
            removed['caption'] = True
            del db['captions'][target_uid]
        
        # Remove channels
        if target_uid in db.get('channels', {}):
            removed['channels'] = len(db['channels'][target_uid])
            del db['channels'][target_uid]
        
        # Remove metadata
        if target_uid in db.get('metadata', {}):
            removed['metadata'] = True
            del db['metadata'][target_uid]
        
        # Remove rename rules
        if target_uid in db.get('rename_rules', {}):
            removed['rename'] = len(db['rename_rules'][target_uid])
            del db['rename_rules'][target_uid]
        
        save_db()
        
        await q.message.edit(f"""
✅ **DATA RESET COMPLETE!**
━━━━━━━━━━━━━━━━━━━━━━

📋 **REMOVED:**
━━━━━━━━━━━━━━━━━━━━━━
🎬 Monitored Anime: **{removed['anime']}**
🖼️ Thumbnails: **{removed['thumbs']}**
📝 Custom Caption: **{'Removed' if removed['caption'] else 'N/A'}**
📢 Linked Channels: **{removed['channels']}**
🏷️ Metadata Tag: **{'Removed' if removed['metadata'] else 'N/A'}**
✏️ Rename Rules: **{removed['rename']}**

━━━━━━━━━━━━━━━━━━━━━━
💎 **Premium Status:** Unchanged ✅

🔄 Aap ab fresh start kar sakte ho!
━━━━━━━━━━━━━━━━━━━━━━
""")

def _build_status_text(uid):
    sc = len([d for d in db['monitored'].values() if any(s['user_id'] == uid for s in d['subscribers'])])
    tc = len(db['thumbnails'].get(uid, {}))
    qc = len([t for t in task_queue if t['task'].user_id == uid]) if task_queue else 0
    ac = len([t for t in active_downloads.values() if t.user_id == uid]) if active_downloads else 0

    if is_owner(uid):
        premium_info = "👑 Owner (Lifetime)"
    elif is_admin(uid):
        premium_info = "⚔️ Admin (Lifetime)"
    elif is_premium(uid):
        days = get_premium_days_left(uid)
        premium_info = f"💎 Premium ({days} days)"
    else:
        premium_info = "🆓 Free User"

    return (
        f"📊 **YOUR STATUS**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Role: {role(uid)}\n"
        f"💎 Plan: {premium_info}\n\n"
        f"📺 Monitored Anime: **{sc}**\n"
        f"🖼️ Thumbnails: **{tc}**\n"
        f"📋 Your Queue: **{qc}** pending\n"
        f"⚡ Your Active: **{ac}** downloading\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

@bot.on_message(filters.command("status"))
async def cmd_status(c, m):
    uid = m.from_user.id
    refresh_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
        InlineKeyboardButton("📋 My List", callback_data="refresh_list"),
    ]])
    await m.reply(_build_status_text(uid), reply_markup=refresh_btn)

def _build_gstatus_text():
    w = sum(1 for s in worker_status.values() if s == "working")
    i = sum(1 for s in worker_status.values() if s == "idle")
    return (
        f"🌐 **Global Status**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Users: **{len(db['users'])}**\n"
        f"📺 Series: **{len(db['monitored'])}**\n"
        f"📋 Queue: **{len(task_queue)}/{MAX_QUEUE}**\n"
        f"📥 Active Downloads: **{len(active_downloads)}**\n\n"
        f"⚙️ Workers: **{TOTAL_WORKERS}**\n"
        f"🟢 Message Worker: 1 (Always Free)\n"
        f"🔵 Download Workers: {MAX_DOWNLOAD_WORKERS}\n"
        f"   ├─ 🟡 Working: {w}\n"
        f"   └─ ⚪ Idle: {i}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

@bot.on_message(filters.command("gstatus"))
async def cmd_gst(c, m):
    refresh_btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh_gstatus")
    ]])
    await m.reply(_build_gstatus_text(), reply_markup=refresh_btn)

@bot.on_message(filters.command("cleanupspace"))
async def cmd_clean(c, m):
    cnt, freed = 0, 0
    for d in [DOWNLOAD_DIR, THUMB_DIR, WORKER_DIR]:
        if os.path.exists(d):
            for root, _, files in os.walk(d):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        freed += os.path.getsize(fp)
                        os.unlink(fp)
                        cnt += 1
                    except: pass
    await m.reply(f"🧹 Deleted {cnt} files | Freed {fmt_bytes(freed)}")

@bot.on_message(filters.command("broadcast"))
async def cmd_broadcast(c, m):
    """Broadcast message to all users"""
    if not is_admin(m.from_user.id):
        return await m.reply("❌ Admin only")
    
    # Method 1: Reply to a message
    if m.reply_to_message:
        broadcast_msg = m.reply_to_message
        
        btns = [
            [InlineKeyboardButton("✅ SEND TO ALL", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
        ]
        
        # Store message for broadcast
        db['pending_broadcast'] = {
            'from_user': m.from_user.id,
            'chat_id': m.chat.id,
            'message_id': broadcast_msg.id,
            'type': 'forward'
        }
        save_db()
        
        total_users = len(db.get('users', {}))
        
        await m.reply(f"""
📢 **BROADCAST PREVIEW**
━━━━━━━━━━━━━━━━━━━━━━

📨 **Message Type:** Forward
👥 **Recipients:** {total_users} users

━━━━━━━━━━━━━━━━━━━━━━
⚠️ Kya aap yeh message sabhi ko bhejana chahte ho?
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))
        return
    
    # Method 2: Text with command
    if len(m.text.split(None, 1)) > 1:
        text = m.text.split(None, 1)[1]
        
        btns = [
            [InlineKeyboardButton("✅ SEND TO ALL", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
        ]
        
        # Store text for broadcast
        db['pending_broadcast'] = {
            'from_user': m.from_user.id,
            'chat_id': m.chat.id,
            'text': text,
            'type': 'text'
        }
        save_db()
        
        total_users = len(db.get('users', {}))
        
        await m.reply(f"""
📢 **BROADCAST PREVIEW**
━━━━━━━━━━━━━━━━━━━━━━

📨 **Message Type:** Text
👥 **Recipients:** {total_users} users

━━━━━━━━━━━━━━━━━━━━━━
📝 **Preview:**
━━━━━━━━━━━━━━━━━━━━━━

{text[:500]}{'...' if len(text) > 500 else ''}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ Kya aap yeh message sabhi ko bhejana chahte ho?
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))
        return
    
    # Show usage
    await m.reply(f"""
📢 **BROADCAST COMMAND**
━━━━━━━━━━━━━━━━━━━━━━

📝 **Method 1:** Reply to message
Reply karke `/broadcast` likho

📝 **Method 2:** Direct text
`/broadcast Your message here`

━━━━━━━━━━━━━━━━━━━━━━
📌 **Example:**
`/broadcast 🎉 New update released!`
━━━━━━━━━━━━━━━━━━━━━━
""")


@bot.on_callback_query(filters.regex(r"^broadcast_"))
async def cb_broadcast(c, q):
    if not is_admin(q.from_user.id):
        return await q.answer("❌ Admin only", show_alert=True)
    
    data = q.data
    
    if data == "broadcast_cancel":
        if 'pending_broadcast' in db:
            del db['pending_broadcast']
            save_db()
        return await q.message.edit("❌ **Broadcast Cancelled**")
    
    if data == "broadcast_confirm":
        if 'pending_broadcast' not in db:
            return await q.message.edit("❌ **No pending broadcast**")
        
        broadcast = db['pending_broadcast']
        
        await q.message.edit("📤 **Broadcasting...**\n\n⏳ Please wait...")
        
        success = 0
        failed = 0
        blocked = 0
        
        all_users = list(db.get('users', {}).keys())
        total = len(all_users)
        
        start_time = time.time()
        
        for i, uid in enumerate(all_users):
            try:
                if broadcast['type'] == 'forward':
                    await c.forward_messages(
                        chat_id=uid,
                        from_chat_id=broadcast['chat_id'],
                        message_ids=broadcast['message_id']
                    )
                else:
                    await c.send_message(
                        uid,
                        f"""
📢 **ANNOUNCEMENT**
━━━━━━━━━━━━━━━━━━━━━━

{broadcast['text']}

━━━━━━━━━━━━━━━━━━━━━━
🤖 **Anime Auto Downloader**
"""
                    )
                success += 1
                
            except Exception as e:
                error_str = str(e).lower()
                if 'blocked' in error_str or 'deactivated' in error_str:
                    blocked += 1
                else:
                    failed += 1
            
            # Update progress every 10 users
            if (i + 1) % 10 == 0:
                try:
                    await q.message.edit(f"""
📤 **Broadcasting...**
━━━━━━━━━━━━━━━━━━━━━━

📊 Progress: {i + 1}/{total}
✅ Success: {success}
❌ Failed: {failed}
🚫 Blocked: {blocked}

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━
""")
                except:
                    pass
            
            await asyncio.sleep(0.1)  # Rate limiting
        
        elapsed = time.time() - start_time
        
        # Cleanup
        if 'pending_broadcast' in db:
            del db['pending_broadcast']
            save_db()
        
        await q.message.edit(f"""
✅ **BROADCAST COMPLETE!**
━━━━━━━━━━━━━━━━━━━━━━

📊 **RESULTS:**
━━━━━━━━━━━━━━━━━━━━━━
👥 Total Users: **{total}**
✅ Delivered: **{success}**
❌ Failed: **{failed}**
🚫 Blocked Bot: **{blocked}**

⏱️ Time: **{fmt_time(elapsed)}**

━━━━━━━━━━━━━━━━━━━━━━
📢 Broadcast by: {q.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━
""")

@bot.on_message(filters.command("thum") & filters.reply)
async def cmd_thum(c, m):
    uid = m.from_user.id
    r = m.reply_to_message
    if not await premium_check(m): return
    if not r or not r.photo: return await m.reply("❌ Reply to image")
    if len(m.command) < 2: return await m.reply("❌ `/thum Name`")
    name = " ".join(m.command[1:])
    if uid not in db['thumbnails']: db['thumbnails'][uid] = {}
    if 'thumb_last_used' not in db: db['thumb_last_used'] = {}
    if uid not in db['thumb_last_used']: db['thumb_last_used'][uid] = {}

    db['thumbnails'][uid][name] = r.photo.file_id
    db['thumb_last_used'][uid][name] = time.time()
    save_db()
    await m.reply(f"✅ Thumbnail set: **{name}**")

@bot.on_message(filters.command("seethum"))
async def cmd_seethum(c, m):
    uid = m.from_user.id
    if not await premium_check(m): 
        return
    
    if uid not in db['thumbnails'] or not db['thumbnails'][uid]:
        return await m.reply("🖼️ **No thumbnails saved!**\n\nUse `/thum AnimeName` (reply to image) to set.")
    
    user_thumbs = db['thumbnails'][uid]
    
    # If name is provided, send that specific thumbnail
    if len(m.command) >= 2:
        search_name = " ".join(m.command[1:])
        
        # Exact match first
        if search_name in user_thumbs:
            thumb_id = user_thumbs[search_name]
            try:
                await c.send_photo(
                    m.chat.id, 
                    thumb_id, 
                    caption=f"🖼️ **Thumbnail:** {search_name}"
                )
                return
            except Exception as e:
                return await m.reply(f"❌ Failed to send: {str(e)[:50]}")
        
        # Fuzzy match
        best_match, similarity = fuzzy(search_name, user_thumbs.keys(), t=0.5)
        if best_match:
            thumb_id = user_thumbs[best_match]
            try:
                await c.send_photo(
                    m.chat.id, 
                    thumb_id, 
                    caption=f"🖼️ **Thumbnail:** {best_match}\n\n💡 Searched: `{search_name}` ({similarity}% match)"
                )
                return
            except Exception as e:
                return await m.reply(f"❌ Failed to send: {str(e)[:50]}")
        
        return await m.reply(f"❌ **Thumbnail not found:** `{search_name}`\n\nUse `/seethum` to see all thumbnails.")
    
    # No name provided, show list
    t = "🖼️ **Your Thumbnails:**\n\n"
    for i, name in enumerate(user_thumbs.keys(), 1):
        t += f"{i}. `{name}`\n"
    
    t += f"\n━━━━━━━━━━━━━━━━━━━━━━"
    t += f"\n📊 **Total:** {len(user_thumbs)}"
    t += f"\n\n💡 **View thumbnail:** `/seethum AnimeName`"
    t += f"\n🗑️ **Delete:** `/delthum AnimeName`"
    
    await m.reply(t)

@bot.on_message(filters.command("delthum"))
async def cmd_delthum(c, m):
    uid = m.from_user.id
    if not await premium_check(m): return  # ✅ ADD THIS LINE HERE
    if len(m.command) < 2: return await m.reply("❌ `/delthum Name`")
    name = " ".join(m.command[1:])
    if uid not in db['thumbnails'] or name not in db['thumbnails'][uid]:
        return await m.reply("❌ Not found")
    del db['thumbnails'][uid][name]
    if uid in db.get('thumb_last_used', {}) and name in db['thumb_last_used'][uid]:
        del db['thumb_last_used'][uid][name]
    save_db()
    await m.reply(f"🗑️ Deleted: **{name}**")

# ==========================================
# IMPROVED CAPTION GUIDE WITH CODE BLOCKS
# ==========================================

CAPTION_GUIDE = """📋 **CUSTOM CAPTION GUIDE**

━━━━━━━━━━━━━━━━━━━━━━
🏷️ **FORMATTING TAGS**
━━━━━━━━━━━━━━━━━━━━━━
`[B]`  → **Bold**
`[T]`  → _Italic_
`[M]`  → `Monospace`
`[Q]`  → Normal
`[S]`  → ~~Strikethrough~~
`[SP]` → ||Spoiler||

━━━━━━━━━━━━━━━━━━━━━━
🔗 **VARIABLES**
━━━━━━━━━━━━━━━━━━━━━━
`{f}`  → Filename
`{s}`  → Season Number
`{e}`  → Episode Number
`{q}`  → Video Quality
`{l}`  → Audio Language
`{sz}` → File Size
`{d}`  → Duration

━━━━━━━━━━━━━━━━━━━━━━
✨ **TAG COMBINATIONS**
━━━━━━━━━━━━━━━━━━━━━━
`[B+T]` → Bold + Italic
`[B+S]` → Bold + Strike
`[B+T+SP]` → Bold + Italic + Spoiler
`[B]` → Bold
`[SP+T]` → Spoiler + Italic

━━━━━━━━━━━━━━━━━━━━━━
📝 **EXAMPLE TEMPLATE**
━━━━━━━━━━━━━━━━━━━━━━
<code>/setcaption [B]🎬 {f}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🏝️ Season: {s}
│ 📺 Episode: {e}
│ 🌐 Language: {l}
│ 📊 Quality: {q}
│ 📦 Size: {sz}
│ ⏱️ Duration: {d}
╰━━━━━━━━━━━━━━━━━━━╯
🔰 Join Channel</code>

━━━━━━━━━━━━━━━━━━━━━━
📌 **HOW IT WORKS**
━━━━━━━━━━━━━━━━━━━━━━
• Tag starts styling from its position
• Next tag stops previous style
• Variables auto-replace with data

━━━━━━━━━━━━━━━━━━━━━━
💡 **AUTO-CORRECT**
━━━━━━━━━━━━━━━━━━━━━━
`[b]` → `[B]`
`[bt]` → `[B+T]`

━━━━━━━━━━━━━━━━━━━━━━
"""

# Default captions (Series & Movie)
DEFAULT_SERIES_CAPTION = """[B]🎬 {f}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🏝️ Season: {s}
│ 📺 Episode: {e}
│ 🌐 Language: {l}
│ 📊 Quality: {q}
│ 📦 Size: {sz}
│ ⏱️ Duration: {d}
╰━━━━━━━━━━━━━━━━━━━╯"""

DEFAULT_MOVIE_CAPTION = """[B]🎬 {f}
╭━━━━━━━━━━━━━━━━━━━╮
│ 🍿 Type: Movie
│ 🌐 Language: {l}
│ 📊 Quality: {q}
│ 📦 Size: {sz}
│ ⏱️ Duration: {d}
╰━━━━━━━━━━━━━━━━━━━╯"""

@bot.on_message(filters.command("setcaption"))
async def cmd_setcaption(c, m):
    """Set custom caption template with styling"""
    uid = m.from_user.id
    if not await premium_check(m): 
        return
    
    # If no template provided, show guide
    if len(m.text.split(None, 1)) < 2:
        return await m.reply(CAPTION_GUIDE)
    
    # Get template (everything after /setcaption)
    template = m.text.split(None, 1)[1]
    
    # Auto-correct tags
    corrected = auto_correct_tags(template)
    
    # Save to database
    if 'captions' not in db:
        db['captions'] = {}
    
    db['captions'][uid] = corrected
    save_db()
    
    # Check if corrections were made
    auto_correct_note = ""
    if corrected != template:
        auto_correct_note = "\n🔧 **Auto-Corrected Tags**"
    
    # Generate styled preview
    try:
        preview_styled = apply_custom_caption(
            corrected,
            file_name="Carnitrix",
            season="1",
            episode="1",
            language="Hindi, Tamil, Telugu, English",
            quality="720P HD",
            size_str="5.91 GB",
            duration_str="1:50:36"
        )
    except Exception as e:
        # Fallback: plain preview
        preview_styled = corrected
        preview_styled = preview_styled.replace('{f}', 'Carnitrix')
        preview_styled = preview_styled.replace('{s}', '1')
        preview_styled = preview_styled.replace('{e}', '1')
        preview_styled = preview_styled.replace('{q}', '720P HD')
        preview_styled = preview_styled.replace('{l}', 'Hindi, Tamil, Telugu, English')
        preview_styled = preview_styled.replace('{sz}', '5.91 GB')
        preview_styled = preview_styled.replace('{d}', '1:50:36')
        # Remove tags for plain text
        import re
        preview_styled = re.sub(r'\[.*?\]', '', preview_styled)
    
    # ✅ FIX: Code block markers
    code_start = "```"
    code_end = "```"
    
    # Try to send with HTML formatting
    try:
        await m.reply(f"""✅ **Caption Template Saved!**{auto_correct_note}

━━━━━━━━━━━━━━━━━━━━━━
📝 **TEMPLATE**
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{corrected}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 **PREVIEW OUTPUT**
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /seecaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        # If HTML fails, try Markdown
        print(f"HTML parse error: {e}, trying Markdown")
        
        try:
            await m.reply(f"""✅ **Caption Template Saved!**{auto_correct_note}

━━━━━━━━━━━━━━━━━━━━━━
📝 **TEMPLATE**
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{corrected}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 **PREVIEW OUTPUT**
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /seecaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown", disable_web_page_preview=True)
        except:
            # Last fallback - no parse mode
            await m.reply(f"""✅ Caption Template Saved!{auto_correct_note}

━━━━━━━━━━━━━━━━━━━━━━
📝 TEMPLATE
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{corrected}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 PREVIEW OUTPUT
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /seecaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", disable_web_page_preview=True)

@bot.on_message(filters.command("seecaption"))
async def cmd_seecaption(c, m):
    """View current caption template with preview"""
    uid = m.from_user.id
    if not await premium_check(m): 
        return
    
    # Check if custom caption exists
    if uid not in db.get('captions', {}):
        return await m.reply("""ℹ️ **No Custom Caption Set**

You're using default caption format.

💡 Set custom: /setcaption
📚 Guide: /setcaption (without text)
""")
    
    # User has custom caption
    template = db['captions'][uid]
    
    # Generate styled preview
    try:
        preview_styled = apply_custom_caption(
            template,
            file_name="Carnitrix",
            season="1",
            episode="1",
            language="Hindi, Tamil, Telugu, English",
            quality="720P HD",
            size_str="5.91 GB",
            duration_str="1:50:36"
        )
    except Exception as e:
        print(f"Preview error: {e}")
        # Plain fallback
        preview_styled = template
        preview_styled = preview_styled.replace('{f}', 'Carnitrix')
        preview_styled = preview_styled.replace('{s}', '1')
        preview_styled = preview_styled.replace('{e}', '1')
        preview_styled = preview_styled.replace('{q}', '720P HD')
        preview_styled = preview_styled.replace('{l}', 'Hindi, Tamil, Telugu, English')
        preview_styled = preview_styled.replace('{sz}', '5.91 GB')
        preview_styled = preview_styled.replace('{d}', '1:50:36')
        import re
        preview_styled = re.sub(r'\[.*?\]', '', preview_styled)
    
    # ✅ FIX: Code block markers
    code_start = "```"
    code_end = "```"
    
    # Try HTML first
    try:
        await m.reply(f"""📋 **YOUR CUSTOM CAPTION**

━━━━━━━━━━━━━━━━━━━━━━
📝 **TEMPLATE**
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{template}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 **PREVIEW OUTPUT**
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /setcaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"HTML failed: {e}, trying Markdown")
        
        try:
            await m.reply(f"""📋 **YOUR CUSTOM CAPTION**

━━━━━━━━━━━━━━━━━━━━━━
📝 **TEMPLATE**
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{template}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 **PREVIEW OUTPUT**
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /setcaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown", disable_web_page_preview=True)
        except:
            await m.reply(f"""📋 YOUR CUSTOM CAPTION

━━━━━━━━━━━━━━━━━━━━━━
📝 TEMPLATE
━━━━━━━━━━━━━━━━━━━━━━
{code_start}
{template}
{code_end}

━━━━━━━━━━━━━━━━━━━━━━
👀 PREVIEW OUTPUT
━━━━━━━━━━━━━━━━━━━━━━
{preview_styled}

━━━━━━━━━━━━━━━━━━━━━━
💡 /setcaption | /delcaption
━━━━━━━━━━━━━━━━━━━━━━
""", disable_web_page_preview=True)

@bot.on_message(filters.command("delcaption"))
async def cmd_delcaption(c, m):
    """Delete custom caption and use default"""
    uid = m.from_user.id
    if not await premium_check(m): 
        return
    
    if uid not in db.get('captions', {}):
        return await m.reply("""ℹ️ **No Custom Caption!**

You're already using default caption format.

💡 Set custom: /setcaption
""")
    
    del db['captions'][uid]
    save_db()
    
    await m.reply("""✅ **Custom Caption Deleted!**

━━━━━━━━━━━━━━━━━━━━━━
🔄 Now using default caption format.

💡 Set new: /setcaption
━━━━━━━━━━━━━━━━━━━━━━
""")

# ==========================================
# CHANNEL UPLOAD SYSTEM - DUAL METHOD
# ==========================================

@bot.on_message(filters.command("addchannel"))
async def cmd_addchannel(c, m):
    """Add channel for auto upload - 2 methods"""
    uid = m.from_user.id

    if not await premium_check(m):
        return

    channel_id = None
    channel_title = None

    # METHOD 1: Reply to forwarded post
    if m.reply_to_message and m.reply_to_message.forward_from_chat:
        channel = m.reply_to_message.forward_from_chat
        channel_id = channel.id
        channel_title = channel.title

    args = m.text.split(None, 1)

    if len(args) < 2:
        return await m.reply(f"""
❌ **How to Add Channel**

━━━━━━━━━━━━━━━━━━━━━━
📌 **METHOD 1: Forward Post**
━━━━━━━━━━━━━━━━━━━━━━
1. Forward any post from your channel
2. Reply to that post with:
   `/addchannel [AnimeName]` - All audio
   `/addchannel [AnimeName] [Language]` - Specific

━━━━━━━━━━━━━━━━━━━━━━
📌 **METHOD 2: Channel ID**
━━━━━━━━━━━━━━━━━━━━━━
`/addchannel -100xxx [AnimeName]`
`/addchannel -100xxx [AnimeName] [Language]`

━━━━━━━━━━━━━━━━━━━━━━
📝 **Examples:**
━━━━━━━━━━━━━━━━━━━━━━
`/addchannel [Naruto]` → All audio
`/addchannel [Naruto] [Hindi]` → Hindi only
`/addchannel [Naruto] [Hindi+Tamil]` → Multiple

━━━━━━━━━━━━━━━━━━━━━━
🎧 **Language Options:**
━━━━━━━━━━━━━━━━━━━━━━
• `[Hindi]` - Only Hindi
• `[Tamil]` - Only Tamil
• `[Telugu]` - Only Telugu
• `[Hindi+Tamil]` - Multiple
• No language = All audio
━━━━━━━━━━━━━━━━━━━━━━
""")

    text = args[1]

    # Check if first part is channel ID
    parts = text.split(None, 1)
    if parts[0].startswith('-100') or parts[0].lstrip('-').isdigit():
        try:
            channel_id = int(parts[0])
            text = parts[1] if len(parts) > 1 else ""

            try:
                chat = await c.get_chat(channel_id)
                channel_title = chat.title
            except:
                return await m.reply(f"""
❌ **Invalid Channel ID!**

━━━━━━━━━━━━━━━━━━━━━━
Cannot find channel: `{channel_id}`

Make sure:
• ID is correct (starts with -100)
• Bot is added to channel
━━━━━━━━━━━━━━━━━━━━━━
""")
        except:
            pass

    # If still no channel
    if not channel_id:
        return await m.reply(f"""
❌ **No Channel Found!**

━━━━━━━━━━━━━━━━━━━━━━
Either:
• Forward a post and reply
• Or provide channel ID

📝 **Examples:**
`/addchannel [Naruto]` (reply to forwarded post)
`/addchannel -100123456 [Naruto] [Hindi]`
━━━━━━━━━━━━━━━━━━━━━━
""")

    # Parse [AnimeName] and optionally [Language]
    matches = re.findall(r'\[([^\]]+)\]', text)

    if len(matches) < 1:
        return await m.reply(f"""
❌ **Invalid Format!**

━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: {channel_title}
📍 ID: `{channel_id}`
━━━━━━━━━━━━━━━━━━━━━━

Use: `/addchannel [AnimeName]` or `/addchannel [AnimeName] [Language]`

📝 **Example:**
`/addchannel [Naruto]` → All audio
`/addchannel [Naruto] [Hindi]` → Hindi only
━━━━━━━━━━━━━━━━━━━━━━
""")

    anime_name = matches[0].strip()
    
    # If no language specified, use "All"
    if len(matches) >= 2:
        languages = matches[1].strip()
    else:
        languages = "All"

    # Verify bot is admin in channel
    try:
        bot_member = await c.get_chat_member(channel_id, (await c.get_me()).id)
        if bot_member.status.name not in ["ADMINISTRATOR", "OWNER"]:
            return await m.reply(f"""
❌ **Bot is not Admin!**

━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: {channel_title}

Please make the bot admin first.
━━━━━━━━━━━━━━━━━━━━━━
""")
    except Exception as e:
        return await m.reply(f"""
❌ **Cannot verify bot access!**

━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: {channel_title}
Error: {str(e)[:50]}

Make sure bot is added as admin.
━━━━━━━━━━━━━━━━━━━━━━
""")

    # Verify user is admin in channel
    try:
        user_member = await c.get_chat_member(channel_id, uid)
        if user_member.status.name not in ["ADMINISTRATOR", "OWNER"]:
            return await m.reply(f"""
❌ **You are not Admin!**

━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: {channel_title}

You must be admin in this channel.
━━━━━━━━━━━━━━━━━━━━━━
""")
    except Exception as e:
        return await m.reply(f"""
❌ **Cannot verify your access!**

━━━━━━━━━━━━━━━━━━━━━━
Error: {str(e)[:50]}
━━━━━━━━━━━━━━━━━━━━━━
""")

    # Save to database
    if 'channels' not in db:
        db['channels'] = {}
    if uid not in db['channels']:
        db['channels'][uid] = []

    # Check if EXACT SAME exists (same channel + same anime + same language)
    for ch in db['channels'][uid]:
        if (ch['channel_id'] == channel_id and 
            ch['anime'].lower() == anime_name.lower() and 
            ch['languages'].lower() == languages.lower()):
            return await m.reply(f"""
⚠️ **Already Exists!**

━━━━━━━━━━━━━━━━━━━━━━
📺 Anime: {anime_name}
📢 Channel: {channel_title}
🎧 Language: {ch['languages']}

Exact same setup already exists!
━━━━━━━━━━━━━━━━━━━━━━
""")

    # Add new channel (allow same anime with different languages)
    db['channels'][uid].append({
        'channel_id': channel_id,
        'channel_title': channel_title,
        'anime': anime_name,
        'languages': languages,
        'added': time.time()
    })
    save_db()

    lang_info = "All audio tracks" if languages == "All" else f"Only {languages}"

    await m.reply(f"""
✅ **Channel Added!**

━━━━━━━━━━━━━━━━━━━━━━
📺 Anime: `{anime_name}`
📢 Channel: {channel_title}
📍 ID: `{channel_id}`
🎧 Audio: `{languages}` ({lang_info})
━━━━━━━━━━━━━━━━━━━━━━

✅ Bot is Admin: Yes
✅ You are Admin: Yes

━━━━━━━━━━━━━━━━━━━━━━
ℹ️ When `{anime_name}` downloads,
it will auto-upload to this channel!
━━━━━━━━━━━━━━━━━━━━━━

📋 View: /seechannel
🗑️ Remove: /delchannel
━━━━━━━━━━━━━━━━━━━━━━
""")


@bot.on_message(filters.command("seechannel"))
async def cmd_seechannel(c, m):
    """View all channels"""
    uid = m.from_user.id

    if not await premium_check(m):
        return

    user_channels = db.get('channels', {}).get(uid, [])

    if not user_channels:
        return await m.reply(f"""
📢 **NO CHANNELS SET**

━━━━━━━━━━━━━━━━━━━━━━
You haven't set any channels yet.

━━━━━━━━━━━━━━━━━━━━━━
📌 **How to Add:**
━━━━━━━━━━━━━━━━━━━━━━

**Method 1:** Forward post + reply
`/addchannel [AnimeName] [Language]`

**Method 2:** Direct with ID
`/addchannel -100xxx [AnimeName] [Language]`

━━━━━━━━━━━━━━━━━━━━━━
📝 **Example:**
`/addchannel [Naruto] [Hindi]`
━━━━━━━━━━━━━━━━━━━━━━
""")

    text = """📢 **YOUR CHANNELS**

━━━━━━━━━━━━━━━━━━━━━━"""

    for i, ch in enumerate(user_channels, 1):
        text += f"""

**{i}. [{ch['anime']}]**
   📢 {ch['channel_title']}
   📍 `{ch['channel_id']}`
   🎧 {ch['languages']}"""

    text += f"""

━━━━━━━━━━━━━━━━━━━━━━
📊 **Total:** {len(user_channels)} channel(s)

🗑️ Remove: `/delchannel 1`
━━━━━━━━━━━━━━━━━━━━━━
"""

    await m.reply(text)


@bot.on_message(filters.command("delchannel"))
async def cmd_delchannel(c, m):
    """Remove channel"""
    uid = m.from_user.id

    if not await premium_check(m):
        return

    user_channels = db.get('channels', {}).get(uid, [])

    if not user_channels:
        return await m.reply("❌ No channels to remove!")

    if len(m.command) < 2:
        # Show list with numbers
        text = """🗑️ **SELECT TO REMOVE**

━━━━━━━━━━━━━━━━━━━━━━"""
        
        for i, ch in enumerate(user_channels, 1):
            text += f"""
{i}. [{ch['anime']}] → {ch['channel_title']}"""
        
        text += f"""

━━━━━━━━━━━━━━━━━━━━━━
Use: `/delchannel <number>`

📝 Example: `/delchannel 1`
━━━━━━━━━━━━━━━━━━━━━━
"""
        return await m.reply(text)

    try:
        num = int(m.command[1])
    except:
        return await m.reply("❌ Invalid number!")

    if num < 1 or num > len(user_channels):
        return await m.reply(f"❌ Invalid! Choose 1-{len(user_channels)}")

    # Remove channel
    removed = user_channels.pop(num - 1)
    db['channels'][uid] = user_channels
    save_db()

    # Try to leave channel if no more anime set for it
    channel_id = removed['channel_id']
    still_has_channel = any(ch['channel_id'] == channel_id for ch in user_channels)

    leave_msg = ""
    if not still_has_channel:
        try:
            await c.leave_chat(channel_id)
            leave_msg = "\n🚪 Bot left the channel"
        except:
            leave_msg = ""

    await m.reply(f"""
✅ **Channel Removed!**

━━━━━━━━━━━━━━━━━━━━━━
📺 Anime: {removed['anime']}
📢 Channel: {removed['channel_title']}
❌ Removed from auto-upload{leave_msg}
━━━━━━━━━━━━━━━━━━━━━━
""")

# ==========================================
# RENAME SYSTEM (Button-Based)
# ==========================================
user_waiting_rename = {}

@bot.on_callback_query(filters.regex(r"^rename_"))
async def rename_callback(c, q):
    """Handle rename button clicks"""
    uid = q.from_user.id
    data = q.data

    if not is_premium(uid):
        return await q.answer("❌ Premium required!", show_alert=True)

    if data == "rename_menu":
        rules = db.get('rename_rules', {}).get(uid, [])
        rules_text = ""
        if rules:
            for i, rule in enumerate(rules, 1):
                rules_text += f"{i}. `{rule}`\n"
        else:
            rules_text = "No rules set"

        btns = [[InlineKeyboardButton("➕ Set Rename", callback_data="rename_set")]]
        if rules:
            btns.append([InlineKeyboardButton("🗑️ Remove Rename", callback_data="rename_remove")])
            btns.append([InlineKeyboardButton("🧹 Cleanup All", callback_data="rename_cleanup")])
        btns.append([InlineKeyboardButton("🔙 Back", callback_data="help_user")])

        await q.message.edit(f"""
✏️ **RENAME SYSTEM**

━━━━━━━━━━━━━━━━━━━━━━
📝 **REMOVE UNWANTED TEXT**
━━━━━━━━━━━━━━━━━━━━━━

This feature removes unwanted text/tags
from your video filenames.

📌 **Examples:**
• Raretoonindia
• [RTI], [Toono]
• Hindinamedub, Toonworld4all

━━━━━━━━━━━━━━━━━━━━━━
📋 **YOUR RULES**
━━━━━━━━━━━━━━━━━━━━━━
{rules_text}

━━━━━━━━━━━━━━━━━━━━━━
💡 Separate multiple with comma (,)
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "rename_set":
        user_waiting_rename[uid] = time.time()

        btns = [[InlineKeyboardButton("❌ Cancel", callback_data="rename_menu")]]

        await q.message.edit(f"""
✏️ **SET RENAME RULES**

━━━━━━━━━━━━━━━━━━━━━━
⏳ Send text to remove within **60 seconds**

📌 **Format Examples:**
• Single: `Raretoonindia`
• Multiple: `[RTI], Toono, Hindinamedub`
• Tags: `[Toonworld4all], [HindiDub]`

━━━━━━━━━━━━━━━━━━━━━━
⌛ **Waiting for your message...**
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "rename_remove":
        rules = db.get('rename_rules', {}).get(uid, [])
        if not rules:
            return await q.answer("❌ No rules to remove!", show_alert=True)

        btns = []
        for i, rule in enumerate(rules, 1):
            btns.append([InlineKeyboardButton(f"❌ {i}. {rule}", callback_data=f"rename_del_{i}")])
        btns.append([InlineKeyboardButton("🔙 Back", callback_data="rename_menu")])

        await q.message.edit(f"""
🗑️ **SELECT TO REMOVE**

━━━━━━━━━━━━━━━━━━━━━━
📝 **YOUR REMOVE LIST**
━━━━━━━━━━━━━━━━━━━━━━

Click to remove specific rule:
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("rename_del_"):
        idx = int(data.split("_")[2]) - 1
        rules = db.get('rename_rules', {}).get(uid, [])

        if 0 <= idx < len(rules):
            removed = rules.pop(idx)
            if uid not in db['rename_rules']:
                db['rename_rules'][uid] = []
            db['rename_rules'][uid] = rules
            save_db()
            await q.answer(f"✅ Removed: {removed}", show_alert=True)

        btns = [[InlineKeyboardButton("🔙 Back", callback_data="rename_menu")]]
        await q.message.edit("✅ **Rule Removed!**\n\nClick back to see updated list.", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "rename_cleanup":
        btns = [
            [InlineKeyboardButton("✅ Yes, Remove All", callback_data="rename_cleanup_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="rename_menu")]
        ]

        rules_count = len(db.get('rename_rules', {}).get(uid, []))

        await q.message.edit(f"""
⚠️ **CONFIRM CLEANUP**

━━━━━━━━━━━━━━━━━━━━━━
Are you sure you want to remove
**ALL** rename rules?

📝 **Rules to delete:** {rules_count}
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "rename_cleanup_confirm":
        if uid in db.get('rename_rules', {}):
            del db['rename_rules'][uid]
            save_db()

        btns = [[InlineKeyboardButton("🔙 Back", callback_data="rename_menu")]]
        await q.message.edit("✅ **All Rules Deleted!**", reply_markup=InlineKeyboardMarkup(btns))

    await q.answer()

# ==========================================
# ✅ FIX 1A: handle_text_input - ADD missing commands
# 📍 Code 04 mein REPLACE karo
# ==========================================
@bot.on_message(filters.text & filters.private & ~filters.command([
    'start', 'set', 'batch', 'list', 'del', 'time', 'status', 'gstatus',
    'cleanup', 'thum', 'seethum', 'delthum', 'setcaption', 'seecaption',
    'delcaption', 'ban', 'unban', 'seeban', 'admin', 'radmin', 'seeadmin',
    'reset', 'dashboard', 'pm', 'repm', 'pmlist', 'npcleanup',
    'backup', 'update', 'restore', 'free', 'unfree', 'validate', 'domain', 'broadcast',
    'cleanupspace', 'website', 'addchannel', 'seechannel', 'delchannel',
    'cancel', 'l0'  # ← ADD THIS
]))
async def handle_text_input(c, m):
    """Handle text input for rename and metadata"""
    uid = m.from_user.id
    text = m.text.strip()

    # Check if URL
    if text.startswith("http://") or text.startswith("https://"):
        await handle_url(c, m)
        return

    # Check if waiting for rename input
    if uid in user_waiting_rename:
        wait_time = user_waiting_rename[uid]
        if time.time() - wait_time > 60:
            del user_waiting_rename[uid]
            return await m.reply("❌ **Timeout!** Please try again.")

        del user_waiting_rename[uid]

        # Parse input
        new_rules = [r.strip() for r in text.split(',') if r.strip()]

        if not new_rules:
            return await m.reply("❌ **Invalid input!** Please provide text to remove.")

        # Add to database
        if uid not in db.get('rename_rules', {}):
            if 'rename_rules' not in db:
                db['rename_rules'] = {}
            db['rename_rules'][uid] = []

        db['rename_rules'][uid].extend(new_rules)
        save_db()

        rules_text = "\n".join([f"{i}. `{r}`" for i, r in enumerate(db['rename_rules'][uid], 1)])

        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Set Rename", callback_data="rename_set")],
            [InlineKeyboardButton("🗑️ Remove Rename", callback_data="rename_remove")],
            [InlineKeyboardButton("🧹 Cleanup All", callback_data="rename_cleanup")],
            [InlineKeyboardButton("🔙 Back", callback_data="help_user")]
        ])

        await m.reply(f"""
✅ **Rename Rules Added!**

━━━━━━━━━━━━━━━━━━━━━━
📝 **YOUR REMOVE LIST**
━━━━━━━━━━━━━━━━━━━━━━
{rules_text}

━━━━━━━━━━━━━━━━━━━━━━
📌 **Example:**
Before: `[RTI]_Naruto_Toono_Ep01.mp4`
After:  `Naruto_Ep01.mp4`
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=btns)
        return

    # Check if waiting for metadata input
    if uid in user_waiting_meta:
        field = user_waiting_meta[uid].get('field')
        wait_time = user_waiting_meta[uid].get('time', 0)

        if time.time() - wait_time > 60:
            del user_waiting_meta[uid]
            return await m.reply("❌ **Timeout!** Please try again.")

        del user_waiting_meta[uid]

        # Save metadata tag
        if uid not in db.get('metadata', {}):
            if 'metadata' not in db:
                db['metadata'] = {}
            db['metadata'][uid] = {}

        db['metadata'][uid]['tag'] = text
        save_db()

        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 Preview", callback_data="meta_preview")],
            [InlineKeyboardButton("🔙 Back to Metadata", callback_data="meta_menu")]
        ])

        await m.reply(f"""
✅ **Tag Set Successfully!**

━━━━━━━━━━━━━━━━━━━━━━
🏷️ Tag: `{text}`
━━━━━━━━━━━━━━━━━━━━━━

📋 **Will be applied to:**
• Title: [{text}] Filename
• Author: {text}
• Artist: {text}
• Comment: {text}
• Album: {text}
• Show: {text}
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=btns)
        return

# ==========================================
# METADATA SYSTEM (Button-Based)
# ==========================================
user_waiting_meta = {}

@bot.on_callback_query(filters.regex(r"^meta_"))
async def metadata_callback(c, q):
    """Handle metadata button clicks - Simplified version"""
    uid = q.from_user.id
    data = q.data

    if not is_premium(uid):
        return await q.answer("❌ Premium required!", show_alert=True)

    user_meta = db.get('metadata', {}).get(uid, {})
    current_tag = user_meta.get('tag', 'Not Set')

    if data == "meta_menu":
        btns = [
            [InlineKeyboardButton("🏷️ Set Tag", callback_data="meta_set_tag")],
            [InlineKeyboardButton("👀 Preview", callback_data="meta_preview")],
            [InlineKeyboardButton("🗑️ Reset", callback_data="meta_reset")],
            [InlineKeyboardButton("🔙 Back", callback_data="help_user")]
        ]

        await q.message.edit(f"""
🏷️ **METADATA EDITOR**

━━━━━━━━━━━━━━━━━━━━━━
📝 **CURRENT TAG**
━━━━━━━━━━━━━━━━━━━━━━
🏷️ Tag: `{current_tag}`

━━━━━━━━━━━━━━━━━━━━━━
ℹ️ **HOW IT WORKS**
━━━━━━━━━━━━━━━━━━━━━━

Set your tag (e.g., `@YourChannel`)

It will be applied to:
• 📌 Title: [Tag] Filename
• 👤 Author: Tag
• 🎬 Artist: Tag
• 📝 Comment: Tag
• 💿 Album: Tag
• 📺 Show: Tag

━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "meta_set_tag":
        user_waiting_meta[uid] = {'field': 'tag', 'time': time.time()}

        btns = [[InlineKeyboardButton("❌ Cancel", callback_data="meta_menu")]]

        await q.message.edit(f"""
🏷️ **SET YOUR TAG**

━━━━━━━━━━━━━━━━━━━━━━
⏳ Send your tag within **60 seconds**

📌 **Examples:**
• `YourChannel`
• `https://t.me/Animex_Studio`
• `YourName`

━━━━━━━━━━━━━━━━━━━━━━
⌛ **Waiting for your message...**
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "meta_preview":
        if current_tag == 'Not Set':
            return await q.answer("❌ Set a tag first!", show_alert=True)

        btns = [[InlineKeyboardButton("🔙 Back", callback_data="meta_menu")]]

        await q.message.edit(f"""
👀 **METADATA PREVIEW**

━━━━━━━━━━━━━━━━━━━━━━
📁 **Sample Filename:**
`[{current_tag}] Naruto S01E05 720p.mkv`

━━━━━━━━━━━━━━━━━━━━━━
📋 **Metadata Applied:**
━━━━━━━━━━━━━━━━━━━━━━
📌 Title: `[{current_tag}] Naruto S01E05 720p`
👤 Author: `{current_tag}`
🎬 Artist: `{current_tag}`
📝 Comment: `{current_tag}`
💿 Album: `{current_tag}`
📺 Show: `{current_tag}`
━━━━━━━━━━━━━━━━━━━━━━

ℹ️ Real Quality & Languages preserved!
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "meta_reset":
        btns = [
            [InlineKeyboardButton("✅ Yes, Reset", callback_data="meta_reset_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="meta_menu")]
        ]

        await q.message.edit(f"""
⚠️ **CONFIRM RESET**

━━━━━━━━━━━━━━━━━━━━━━
Remove your metadata tag?

Current Tag: `{current_tag}`
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "meta_reset_confirm":
        if uid in db.get('metadata', {}):
            del db['metadata'][uid]
            save_db()

        btns = [[InlineKeyboardButton("🔙 Back", callback_data="meta_menu")]]
        await q.message.edit("✅ **Metadata Reset!**\n\nTag removed.", reply_markup=InlineKeyboardMarkup(btns))

    await q.answer()

# ==========================================
# ❌ TASK CANCEL COMMAND
# ==========================================
@bot.on_message(filters.command("cancel"))
async def cmd_cancel(c, m):
    """Cancel active download/upload task"""
    uid = m.from_user.id

    # If cancel ID provided → cancel that specific task
    if len(m.command) >= 2:
        cancel_id = m.command[1].strip()

        # Search in active downloads
        target_task = None
        for task_id, task in list(active_downloads.items()):
            if task.cancel_id == cancel_id:
                target_task = task
                break

        if not target_task:
            return await m.reply(f"""
❌ **Task Not Found!**
━━━━━━━━━━━━━━━━━━━━━━

ID `{cancel_id}` not found or already completed.

💡 Use `/cancel` to see active tasks.
━━━━━━━━━━━━━━━━━━━━━━
""")

        # Verify ownership (only task owner or admin can cancel)
        if target_task.user_id != uid and not is_admin(uid):
            return await m.reply("❌ **Not your task!**\n\nYou can only cancel your own tasks.")

        # Cancel the task
        target_task.cancel()

        # Update progress message
        if target_task.status_obj:
            try:
                batch_info = ""
                if target_task.batch_mode:
                    batch_info = f"\n📑 Batch: Episode {target_task.current_episode}/{target_task.total_episodes}"

                await target_task.status_obj.update(f"""
❌ **TASK CANCELLED!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{target_task.series_name}**
📺 Episode: {target_task.episode or 'N/A'}
📊 Status: {target_task.status}{batch_info}

━━━━━━━━━━━━━━━━━━━━━━
🗑️ All downloaded files will be cleaned up.
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
            except:
                pass

        await m.reply(f"""
✅ **Task Cancelled Successfully!**
━━━━━━━━━━━━━━━━━━━━━━

🎬 **{target_task.series_name}**
📺 Episode: {target_task.episode or 'N/A'}
🆔 Cancel ID: `{cancel_id}`

🗑️ Files cleaned up.
━━━━━━━━━━━━━━━━━━━━━━
""")

        print(f"❌ Task cancelled by user {uid}: {target_task.task_id}")
        return

    # No ID provided → show all active tasks for this user
    user_tasks = []
    for task_id, task in active_downloads.items():
        if task.user_id == uid and task.status not in ["cancelled", "completed", "failed"]:
            user_tasks.append(task)

    if not user_tasks:
        return await m.reply(f"""
ℹ️ **No Active Tasks**
━━━━━━━━━━━━━━━━━━━━━━

You have no active downloads or uploads.

💡 Send an anime URL to start downloading!
━━━━━━━━━━━━━━━━━━━━━━
""")

    text = """📋 **YOUR ACTIVE TASKS**
━━━━━━━━━━━━━━━━━━━━━━

"""
    for i, task in enumerate(user_tasks, 1):
        batch_info = ""
        if task.batch_mode:
            batch_info = f"\n   📑 Batch: Ep {task.current_episode}/{task.total_episodes}"

        elapsed = time.time() - task.created_at
        text += f"""**{i}. {task.series_name}**
   📺 Episode: {task.episode or 'N/A'}
   📊 Status: {task.status}
   ⏱️ Running: {fmt_time(elapsed)}{batch_info}
   ❌ Cancel: `/cancel {task.cancel_id}`

"""

    text += f"""━━━━━━━━━━━━━━━━━━━━━━
📊 **Total Active:** {len(user_tasks)}

💡 Copy the cancel command and send it!
━━━━━━━━━━━━━━━━━━━━━━
"""
    await m.reply(text)

# ==========================================
# 📥 LEECH COMMAND - SMART DIRECT LINK DOWNLOAD
# ==========================================
@bot.on_message(filters.command("l0"))
async def cmd_leech(c, m):
    """
    Smart Leech command - Download any link
    /l0 link → Download & Upload
    /l0 link -e → Download, Extract if ZIP, Upload
    /l0 link -e password → Download, Extract with password, Upload
    
    Supported URLs use their proper methods (GDFlix, Toono, etc.)
    Unsupported URLs use direct download
    """
    uid = m.from_user.id
    cid = m.chat.id
    
    if is_banned(uid):
        return await m.reply("🚫 Banned")
    
    if not await premium_check(m):
        return
    
    if not await cooldown_check(m):
        return
    
    # Parse command
    args = m.text.split(None)
    
    if len(args) < 2:
        return await m.reply(f"""
📥 **LEECH COMMAND**
━━━━━━━━━━━━━━━━━━━━━━

📝 **Usage:**

**Simple Download:**
`/l0 <link>`

**Download + Extract ZIP:**
`/l0 <link> -e`

**Download + Extract with Password:**
`/l0 <link> -e <password>`

━━━━━━━━━━━━━━━━━━━━━━
📌 **Examples:**

`/l0 https://example.com/video.mp4`
`/l0 https://gdflix.io/file/xxx`
`/l0 https://example.com/anime.zip -e`
`/l0 https://example.com/anime.zip -e mypass123`

━━━━━━━━━━━━━━━━━━━━━━
🌐 **Supported Sites (Auto-detect):**
• GDFlix, Toono, RareAnimes
• AnimeDubHindi, Swift, Codedew
• Any direct download link

⚠️ **Notes:**
• Auto-split files > 1.9GB
• ZIP extraction supported
• Original format preserved
━━━━━━━━━━━━━━━━━━━━━━
""")
    
    url = args[1]
    extract_mode = False
    zip_password = None
    
    # Check for -e flag
    if len(args) >= 3 and args[2].lower() == '-e':
        extract_mode = True
        if len(args) >= 4:
            zip_password = args[3]
    
    # Validate URL
    if not url.startswith('http://') and not url.startswith('https://'):
        return await m.reply("❌ **Invalid URL!**\n\nURL must start with http:// or https://")
    
    update_cooldown(uid)
    
    st = Status(c, cid)
    
    # ==========================================
    # DETECT WEBSITE TYPE
    # ==========================================
    site_key, site_data = detect_website(url)
    
    if site_key:
        site_name = site_data['name']
        await st.create(f"""
📥 **Leech Starting...**
━━━━━━━━━━━━━━━━━━━━━━

{site_name} **Detected!**

🔗 `{url[:50]}{'...' if len(url) > 50 else ''}`

📦 Extract Mode: {'✅ Yes' if extract_mode else '❌ No'}

⏳ Using optimized method...
━━━━━━━━━━━━━━━━━━━━━━
""")
    else:
        await st.create(f"""
📥 **Leech Starting...**
━━━━━━━━━━━━━━━━━━━━━━

🔗 **Direct Link**

🔗 `{url[:50]}{'...' if len(url) > 50 else ''}`

📦 Extract Mode: {'✅ Yes' if extract_mode else '❌ No'}
🔐 Password: {'✅ Set' if zip_password else '❌ None'}

⏳ Connecting...
━━━━━━━━━━━━━━━━━━━━━━
""")
    
    try:
        # Create task
        content_key = f"leech_{uid}_{int(time.time())}"
        task = Task(uid, cid, "leech", content_key, url)
        task.series_name = "Leech Download"
        task.is_movie = True
        
        download_dir = task.directory
        downloaded_files = []
        
        # ==========================================
        # METHOD SELECTION BASED ON WEBSITE
        # ==========================================
        
        # ----- GDFLIX -----
        if site_key == 'gdflix' or ('gdflix' in url.lower() and '/file/' in url):
            print(f"📦 Using GDFlix method for leech")
            await st.update("📦 **Using GDFlix method...**", force=True)
            
            dl = GDFlixDownloader(task, st)
            result = await dl.download_from_gdflix(url)
            
            if result and os.path.exists(result):
                downloaded_files.append(result)
        
        # ----- SWIFT/MULTIQUALITY -----
        elif site_key == 'swift' or 'multiquality' in url.lower():
            print(f"⚡ Using Swift method for leech")
            await st.update("⚡ **Using Swift method...**", force=True)
            
            dl = Downloader(task, st)
            files = await dl.download(url)
            if files:
                downloaded_files.extend(files)
        
        # ----- CODEDEW -----
        elif site_key == 'codedew' or 'codedew.com' in url.lower():
            print(f"🔗 Using Codedew method for leech")
            await st.update("🔗 **Resolving Codedew...**", force=True)
            
            # Resolve codedew first
            resolver = SmartCodedewResolver(st)
            swift_url = await resolver.resolve(url)
            
            if swift_url:
                dl = Downloader(task, st)
                files = await dl.download(swift_url)
                if files:
                    downloaded_files.extend(files)
        
        # ----- DIRECT DOWNLOAD (Unsupported/Unknown) -----
        else:
            print(f"📥 Using direct download for leech")
            await st.update("📥 **Direct downloading...**", force=True)
            
            # Download using requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()
            
            # Get filename
            filename = None
            if "content-disposition" in response.headers:
                cd = response.headers["content-disposition"]
                fname_match = re.findall(r"filename\*?=([^;]+)", cd, re.IGNORECASE)
                if fname_match:
                    filename = fname_match[0].strip().strip('"').strip("'")
                    if "UTF-8''" in filename:
                        filename = filename.split("UTF-8''")[-1]
                    filename = urllib.parse.unquote(filename)
            
            if not filename:
                filename = urllib.parse.unquote(url.split("/")[-1].split("?")[0])
            
            if not filename or len(filename) < 3:
                # Guess extension from content-type
                content_type = response.headers.get('content-type', '')
                if 'video' in content_type:
                    filename = f"leech_{int(time.time())}.mp4"
                elif 'zip' in content_type:
                    filename = f"leech_{int(time.time())}.zip"
                else:
                    filename = f"leech_{int(time.time())}"
            
            save_path = os.path.join(download_dir, filename)
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress
            downloaded = 0
            start_time = time.time()
            last_update = start_time
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if task.cancelled:
                        f.close()
                        try:
                            os.remove(save_path)
                        except:
                            pass
                        return await st.update("❌ **Cancelled!**", force=True)
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    now = time.time()
                    if now - last_update >= PROGRESS_UPDATE_INTERVAL:
                        elapsed = now - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        
                        if total_size > 0:
                            pct = (downloaded / total_size) * 100
                            eta = (total_size - downloaded) / speed if speed > 0 else 0
                        else:
                            pct = 0
                            eta = 0
                        
                        bar = progress_bar(pct)
                        
                        await st.update(f"""
📥 **Downloading...**
━━━━━━━━━━━━━━━━━━━━━━

📁 `{filename[:40]}{'...' if len(filename) > 40 else ''}`

{bar} **{pct:.1f}%**

📦 {fmt_bytes(downloaded)} / {fmt_bytes(total_size) if total_size > 0 else '???'}
⚡ {fmt_bytes(speed)}/s | ⏱️ {fmt_time(eta)}

❌ Cancel: `/cancel {task.cancel_id}`
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
                        last_update = now
            
            if os.path.exists(save_path) and os.path.getsize(save_path) > 1024:
                downloaded_files.append(save_path)
                print(f"✅ Direct download: {filename} ({fmt_bytes(os.path.getsize(save_path))})")
        
        # ==========================================
        # CHECK DOWNLOAD SUCCESS
        # ==========================================
        if not downloaded_files:
            await st.update("❌ **Download failed!**\n\nNo files downloaded.", force=True)
            task.cleanup()
            return
        
        # ==========================================
        # EXTRACT MODE (Only if -e flag and file is ZIP)
        # ==========================================
        files_to_upload = []
        
        if extract_mode:
            for filepath in downloaded_files:
                # Check if file is actually a ZIP
                if is_zip_file(filepath):
                    await st.update(f"""
📦 **Extracting ZIP...**
━━━━━━━━━━━━━━━━━━━━━━

📁 `{os.path.basename(filepath)}`
🔐 Password: {'Yes' if zip_password else 'No'}

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
                    
                    import zipfile
                    
                    try:
                        extract_dir = os.path.join(download_dir, f"extracted_{int(time.time())}")
                        os.makedirs(extract_dir, exist_ok=True)
                        
                        with zipfile.ZipFile(filepath, 'r') as zip_ref:
                            if zip_password:
                                zip_ref.extractall(extract_dir, pwd=zip_password.encode())
                            else:
                                zip_ref.extractall(extract_dir)
                        
                        # Find all files in extracted dir
                        for root, dirs, files_in_dir in os.walk(extract_dir):
                            for file in files_in_dir:
                                file_path = os.path.join(root, file)
                                if os.path.getsize(file_path) > 1024:  # > 1KB
                                    files_to_upload.append(file_path)
                        
                        # Delete original ZIP
                        try:
                            os.remove(filepath)
                        except:
                            pass
                        
                        print(f"✅ Extracted {len(files_to_upload)} files")
                        
                    except zipfile.BadZipFile:
                        print(f"⚠️ Not a valid ZIP, using as-is")
                        files_to_upload.append(filepath)
                    except RuntimeError as e:
                        if "password" in str(e).lower():
                            await st.update("❌ **Wrong password or password required!**\n\nUse: `/l0 link -e password`", force=True)
                            task.cleanup()
                            return
                        else:
                            print(f"⚠️ Extract error: {e}, using as-is")
                            files_to_upload.append(filepath)
                else:
                    # Not a ZIP file, use as-is
                    print(f"ℹ️ Not a ZIP file, using as-is")
                    files_to_upload.append(filepath)
        else:
            # No extraction requested
            files_to_upload = downloaded_files
        
        if not files_to_upload:
            await st.update("❌ **No files to upload!**", force=True)
            task.cleanup()
            return
        
        # ==========================================
        # PROCESS FILES (Keep original format, only video→mp4)
        # ==========================================
        processed_files = []
        video_extensions = ('.mp4', '.mkv', '.avi', '.webm', '.mov', '.wmv', '.flv', '.m4v')
        
        for f in files_to_upload:
            if not os.path.exists(f):
                continue
            
            filename_lower = os.path.basename(f).lower()
            
            # Only rename video files to .mp4
            if any(filename_lower.endswith(ext) for ext in video_extensions):
                renamed = ensure_mp4_extension(f)
                processed_files.append(renamed)
            else:
                # Keep original format (ZIP, RAR, PDF, etc.)
                processed_files.append(f)
        
        # ==========================================
        # SPLIT LARGE VIDEO FILES
        # ==========================================
        final_files = []
        for f in processed_files:
            if os.path.exists(f):
                file_size = os.path.getsize(f)
                filename_lower = os.path.basename(f).lower()
                
                # Only split video files
                is_video = any(filename_lower.endswith(ext) for ext in video_extensions) or filename_lower.endswith('.mp4')
                
                if is_video and file_size > MAX_FILE_SIZE:
                    await st.update(f"✂️ **Splitting large file...**\n\n📦 {fmt_bytes(file_size)}", force=True)
                    split_parts = await split_video(f, download_dir, st)
                    final_files.extend(split_parts)
                else:
                    final_files.append(f)
        
        if not final_files:
            await st.update("❌ **No valid files to upload!**", force=True)
            task.cleanup()
            return
        
        # Sort files
        final_files = sorted(final_files, key=lambda x: os.path.basename(x).lower())
        
        task.files = final_files
        task.status = "uploading"
        
        # ==========================================
        # UPLOAD
        # ==========================================
        await st.update(f"""
📤 **Uploading {len(final_files)} file(s)...**
━━━━━━━━━━━━━━━━━━━━━━

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
        
        # Check if video files for video upload, else document upload
        video_files = [f for f in final_files if os.path.basename(f).lower().endswith(('.mp4', '.mkv', '.avi', '.webm'))]
        
        if video_files:
            # Use video uploader
            up = Uploader(bot, st, task)
            await up.upload_all()
        else:
            # Upload as documents
            for i, filepath in enumerate(final_files, 1):
                try:
                    filename = os.path.basename(filepath)
                    file_size = os.path.getsize(filepath)
                    
                    await st.update(f"""
📤 **Uploading...**
━━━━━━━━━━━━━━━━━━━━━━

📁 `{filename[:40]}...`
📦 Size: {fmt_bytes(file_size)}
📊 File {i}/{len(final_files)}

⏳ Please wait...
━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
                    
                    await c.send_document(
                        chat_id=cid,
                        document=filepath,
                        caption=f"📁 **{filename}**\n📦 Size: {fmt_bytes(file_size)}"
                    )
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"Document upload error: {e}")
        
        # Complete message
        total = sum(os.path.getsize(f) for f in final_files if os.path.exists(f))
        
        await st.update(f"""
✅ **Leech Complete!**
━━━━━━━━━━━━━━━━━━━━━━

📁 **Files:** {len(final_files)}
💾 **Total Size:** {fmt_bytes(total)}
📦 **Extracted:** {'Yes' if extract_mode else 'No'}
🌐 **Method:** {site_name if site_key else 'Direct'}

━━━━━━━━━━━━━━━━━━━━━━
""", force=True)
        
        task.status = "completed"
        asyncio.create_task(delayed_cleanup(task, FILE_CLEANUP_TIME))
        
    except requests.exceptions.RequestException as e:
        await st.update(f"❌ **Download Error!**\n\n{str(e)[:100]}", force=True)
        task.cleanup()
    except Exception as e:
        print(f"Leech error: {e}")
        traceback.print_exc()
        await st.update(f"❌ **Error:** {str(e)[:100]}", force=True)
        task.cleanup()

@bot.on_message(filters.command("ban"))
async def cmd_ban(c, m):
    if not is_admin(m.from_user.id): return
    if len(m.command) < 2: return await m.reply("❌ `/ban ID`")
    try: t = int(m.command[1])
    except: return await m.reply("❌ Invalid")
    if t == db['owner_id']: return await m.reply("❌ Can't ban owner")
    db['banned'].add(t)
    db['admins'].discard(t)
    save_db()
    await m.reply(f"🚫 Banned: `{t}`")

@bot.on_message(filters.command("unban"))
async def cmd_unban(c, m):
    if not is_admin(m.from_user.id): return
    if len(m.command) < 2: return await m.reply("❌ `/unban ID`")
    try: t = int(m.command[1])
    except: return await m.reply("❌ Invalid")
    db['banned'].discard(t)
    save_db()
    await m.reply(f"✅ Unbanned: `{t}`")

@bot.on_message(filters.command("seeban"))
async def cmd_seeban(c, m):
    if not is_admin(m.from_user.id): return
    if not db['banned']: return await m.reply("🚫 None")
    t = "🚫 **Banned:**\n" + "\n".join([f"`{u}`" for u in db['banned']])
    await m.reply(t)

# ==========================================
# NON-PREMIUM CLEANUP COMMAND
# ==========================================
@bot.on_message(filters.command("npcleanup"))
async def cmd_npcleanup(c, m):
    """Remove all data of non-premium users"""
    if not is_admin(m.from_user.id):
        return await m.reply("❌ Admin only")
    
    # Count non-premium users with data
    non_premium_with_data = set()
    
    # Check monitored anime
    for key, data in db['monitored'].items():
        for sub in data['subscribers']:
            uid = sub['user_id']
            if not is_premium(uid) and not is_admin(uid) and not is_owner(uid):
                non_premium_with_data.add(uid)
    
    # Check thumbnails
    for uid in db.get('thumbnails', {}).keys():
        if not is_premium(uid) and not is_admin(uid) and not is_owner(uid):
            non_premium_with_data.add(uid)
    
    if not non_premium_with_data:
        return await m.reply("✅ **No non-premium user data found!**\n\nAll users with data are premium/admin/owner.")
    
    # Preview what will be removed
    preview_anime = 0
    preview_thumbs = 0
    
    for key, data in db['monitored'].items():
        for sub in data['subscribers']:
            if sub['user_id'] in non_premium_with_data:
                preview_anime += 1
                break
    
    for uid in non_premium_with_data:
        if uid in db.get('thumbnails', {}):
            preview_thumbs += len(db['thumbnails'][uid])
    
    btns = [
        [InlineKeyboardButton("⚠️ YES, REMOVE ALL", callback_data="npcleanup_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="npcleanup_cancel")]
    ]
    
    await m.reply(f"""
⚠️ **NON-PREMIUM CLEANUP**

━━━━━━━━━━━━━━━━━━━━━━
📊 **Found {len(non_premium_with_data)} non-premium users with data**

🗑️ **Will be removed:**
   🎬 Monitored Anime: ~{preview_anime}
   🖼️ Thumbnails: ~{preview_thumbs}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ This action is **IRREVERSIBLE**!

Are you sure?
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))


@bot.on_callback_query(filters.regex(r"^npcleanup_"))
async def cb_npcleanup(c, q):
    if not is_admin(q.from_user.id):
        return await q.answer("❌ Admin only", show_alert=True)
    
    if q.data == "npcleanup_cancel":
        return await q.message.edit("❌ **Cleanup Cancelled**")
    
    # Process cleanup with progress
    await q.message.edit("⏳ **Starting Cleanup...**\n\n📊 Progress: 0%")
    
    # Step 1: Identify users (20%)
    await q.message.edit("🔍 **Step 1/5:** Finding non-premium users...\n\n📊 Progress: [██░░░░░░░░] 20%")
    
    removed_data = {}
    non_premium_users = set()
    
    for uid in db.get('users', {}).keys():
        if not is_premium(uid) and not is_admin(uid) and not is_owner(uid):
            non_premium_users.add(uid)
    
    for uid in db.get('thumbnails', {}).keys():
        if not is_premium(uid) and not is_admin(uid) and not is_owner(uid):
            non_premium_users.add(uid)
    
    for key, data in db['monitored'].items():
        for sub in data['subscribers']:
            uid = sub['user_id']
            if not is_premium(uid) and not is_admin(uid) and not is_owner(uid):
                non_premium_users.add(uid)
    
    # Step 2: Remove monitored (40%)
    await q.message.edit(f"🎬 **Step 2/5:** Removing anime subscriptions...\n\n👥 Found: {len(non_premium_users)} users\n📊 Progress: [████░░░░░░] 40%")
    
    for key, data in list(db['monitored'].items()):
        series_name = data.get('series_name', 'Unknown')
        
        for sub in list(data['subscribers']):
            uid = sub['user_id']
            if uid in non_premium_users:
                if uid not in removed_data:
                    removed_data[uid] = {'anime': [], 'thumbs': [], 'captions': False}
                
                if series_name not in removed_data[uid]['anime']:
                    removed_data[uid]['anime'].append(series_name)
                
                data['subscribers'].remove(sub)
        
        # If no subscribers left, remove the entire series
        if not data['subscribers']:
            del db['monitored'][key]
    
    # Step 3: Remove thumbnails (60%)
    await q.message.edit(f"🖼️ **Step 3/5:** Removing thumbnails...\n\n📊 Progress: [██████░░░░] 60%")
    
    for uid in list(db.get('thumbnails', {}).keys()):
        if uid in non_premium_users:
            if uid not in removed_data:
                removed_data[uid] = {'anime': [], 'thumbs': [], 'captions': False}
            
            removed_data[uid]['thumbs'] = list(db['thumbnails'][uid].keys())
            del db['thumbnails'][uid]
            
            if uid in db.get('thumb_last_used', {}):
                del db['thumb_last_used'][uid]
    
    # Step 4: Remove captions (80%)
    await q.message.edit(f"📝 **Step 4/5:** Removing captions...\n\n📊 Progress: [████████░░] 80%")
    
    for uid in list(db.get('captions', {}).keys()):
        if uid in non_premium_users:
            if uid not in removed_data:
                removed_data[uid] = {'anime': [], 'thumbs': [], 'captions': False}
            
            removed_data[uid]['captions'] = True
            del db['captions'][uid]
    
    # Remove thumb_last_used orphans
    for uid in list(db.get('thumb_last_used', {}).keys()):
        if uid in non_premium_users:
            del db['thumb_last_used'][uid]
    
    # Step 5: Save database (100%)
    await q.message.edit(f"💾 **Step 5/5:** Saving database...\n\n📊 Progress: [█████████░] 90%")
    
    save_db()
    
    await q.message.edit("✅ **Cleanup Complete!**\n\n📊 Progress: [██████████] 100%")
    await asyncio.sleep(1)
    
    # ✅ FIX: Build detailed report (NO DUPLICATION)
    if not removed_data:
        return await q.message.edit("✅ **No data to remove!**")
    
    total_users = len(removed_data)
    total_anime = sum(len(d['anime']) for d in removed_data.values())
    total_thumbs = sum(len(d['thumbs']) for d in removed_data.values())
    total_captions = sum(1 for d in removed_data.values() if d.get('captions'))
    
    # Build user-wise report
    report_lines = []
    for uid, data in removed_data.items():
        user_section = f"\n👤 **User ID:** `{uid}`"
        
        if data['anime']:
            user_section += f"\n   🎬 **Anime Removed ({len(data['anime'])}):**"
            for anime in data['anime'][:5]:
                user_section += f"\n      • {anime}"
            if len(data['anime']) > 5:
                user_section += f"\n      • ...+{len(data['anime']) - 5} more"
        
        if data['thumbs']:
            user_section += f"\n   🖼️ **Thumbnails Removed ({len(data['thumbs'])}):**"
            for thumb in data['thumbs'][:5]:
                user_section += f"\n      • {thumb}"
            if len(data['thumbs']) > 5:
                user_section += f"\n      • ...+{len(data['thumbs']) - 5} more"
        
        if data.get('captions'):
            user_section += f"\n   📝 **Caption:** Removed"
        
        report_lines.append(user_section)
    
    # Combine report
    full_report = f"""
🗑️ **NON-PREMIUM CLEANUP COMPLETE!**

━━━━━━━━━━━━━━━━━━━━━━
📊 **SUMMARY**
━━━━━━━━━━━━━━━━━━━━━━
👥 Users Cleaned: **{total_users}**
🎬 Anime Removed: **{total_anime}**
🖼️ Thumbnails Removed: **{total_thumbs}**
📝 Captions Removed: **{total_captions}**

━━━━━━━━━━━━━━━━━━━━━━
📋 **DETAILED REPORT**
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for line in report_lines:
        full_report += line + "\n"
    
    full_report += f"""
━━━━━━━━━━━━━━━━━━━━━━
✅ **Cleanup completed by:** {q.from_user.first_name}
⏰ **Time:** {datetime.now().strftime('%d %b %Y, %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # If report is too long, split into multiple messages
    if len(full_report) > 4000:
        # Send summary first
        summary = f"""
🗑️ **NON-PREMIUM CLEANUP COMPLETE!**

━━━━━━━━━━━━━━━━━━━━━━
📊 **SUMMARY**
━━━━━━━━━━━━━━━━━━━━━━
👥 Users Cleaned: **{total_users}**
🎬 Anime Removed: **{total_anime}**
🖼️ Thumbnails Removed: **{total_thumbs}**
📝 Captions Removed: **{total_captions}**

━━━━━━━━━━━━━━━━━━━━━━
📋 Detailed report is too long.
Sending as separate messages...
━━━━━━━━━━━━━━━━━━━━━━
"""
        await q.message.edit(summary)
        
        # Send detailed user reports in chunks
        current_chunk = "📋 **DETAILED REPORT:**\n"
        for line in report_lines:
            if len(current_chunk) + len(line) > 3500:
                await c.send_message(q.message.chat.id, current_chunk)
                current_chunk = ""
            current_chunk += line + "\n━━━━━━━━━━━━━━━━━━━━━━"
        
        if current_chunk:
            current_chunk += f"\n\n✅ **Done by:** {q.from_user.first_name}"
            await c.send_message(q.message.chat.id, current_chunk)
    else:
        await q.message.edit(full_report)
    
    print(f"✅ NPCleanup: {total_users} users, {total_anime} anime, {total_thumbs} thumbs removed")
    
# ==========================================
# PREMIUM MANAGEMENT COMMANDS
# ==========================================

@bot.on_message(filters.command("pm"))
async def cmd_premium(c, m):
    """Grant premium"""
    if not is_admin(m.from_user.id):
        return await m.reply("❌ Admin only")

    if len(m.command) < 3:
        return await m.reply("❌ Usage: `/pm <UserID> <Days>`\n\nExample: `/pm 123456789 30`")

    try:
        target_id = int(m.command[1])
        days = int(m.command[2])
    except:
        return await m.reply("❌ Invalid format")

    if days < 1 or days > 3650:
        return await m.reply("❌ Days: 1-3650")

    add_premium(target_id, days, m.from_user.id)

    from datetime import datetime, timedelta
    expiry_date = datetime.now() + timedelta(days=days)
    expiry_str = expiry_date.strftime("%d %b %Y")

    await m.reply(f"""
✅ **Premium Granted!**

━━━━━━━━━━━━━━━━━━━━━━
👤 User: `{target_id}`
💎 Duration: {days} days
📅 Expires: {expiry_str}
👮 By: {m.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━
""")

    try:
        await c.send_message(target_id, f"""
🎉 **Premium Activated!**

━━━━━━━━━━━━━━━━━━━━━━
💎 Premium Access Granted!

⏳ Validity: {days} days
📅 Expires: {expiry_str}

━━━━━━━━━━━━━━━━━━━━━━
✨ **Features Unlocked:**
🎬 Auto monitoring
📥 Batch downloads
🖼️ Custom thumbnails
⚡ Fast downloads

Use: /start
""")
    except:
        await m.reply("⚠️ User hasn't started bot")


@bot.on_message(filters.command("repm"))
async def cmd_remove_premium(c, m):
    """Remove premium"""
    if not is_admin(m.from_user.id):
        return await m.reply("❌ Admin only")

    if len(m.command) < 2:
        return await m.reply("❌ Usage: `/repm <UserID>`")

    try:
        target_id = int(m.command[1])
    except:
        return await m.reply("❌ Invalid ID")

    if target_id == db['owner_id']:
        return await m.reply("❌ Can't remove owner")

    if target_id in db.get('admins', set()):
        return await m.reply("❌ Can't remove admin")

    if remove_premium(target_id):
        await m.reply(f"""
✅ **Premium Removed!**

━━━━━━━━━━━━━━━━━━━━━━
👤 User: `{target_id}`
🔓 Now: Free User
👮 By: {m.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━
""")

        try:
            await c.send_message(target_id, "⚠️ **Premium Expired**\n\nContact @Dark_isekai to renew")
        except:
            pass
    else:
        await m.reply("❌ User not premium")

@bot.on_message(filters.command("pmlist"))
async def cmd_premium_list(c, m):
    """List premium users"""
    if not is_admin(m.from_user.id):
        return await m.reply("❌ Admin only")

    premium_users = db.get('premium_users', {})

    if not premium_users:
        return await m.reply("📋 No premium users")

    from datetime import datetime

    msg = "💎 **PREMIUM USERS**\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    sorted_users = sorted(premium_users.items(), key=lambda x: x[1]['expires'])

    for idx, (uid, data) in enumerate(sorted_users, 1):
        try:
            user = await c.get_users(uid)
            name = user.first_name
            username = f"@{user.username}" if user.username else "No username"
        except:
            name = "Unknown"
            username = "N/A"

        expiry_timestamp = data['expires']
        expiry_date = datetime.fromtimestamp(expiry_timestamp)
        expiry_str = expiry_date.strftime("%d %b %Y")

        days_left = int((expiry_timestamp - time.time()) / 86400)

        msg += f"**{idx}.** {name}\n"
        msg += f"   📱 ID: `{uid}`\n"
        msg += f"   👤 User: {username}\n"
        msg += f"   ⏳ Validity: {days_left} days\n"
        msg += f"   📅 Expires: {expiry_str}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━\n"

    msg += f"\n📊 Total: {len(premium_users)} users"

    await m.reply(msg)

# ==========================================
# 🎁 GLOBAL FREE ACCESS COMMANDS
# ==========================================

async def broadcast_free_access(c, expiry_str):
    """Background task to broadcast free access to old users without blocking bot"""
    success, failed = 0, 0
    broadcast_msg = f"""
🎉 **GREAT NEWS!** 🎉

━━━━━━━━━━━━━━━━━━━━━━
Ab aap is bot ko bilkul **FREE** mein use kar sakte hain! 

📅 **Free Access Expiry:** {expiry_str}
━━━━━━━━━━━━━━━━━━━━━━

Premium features unlocked for everyone:
🎬 Auto monitoring
📥 Batch downloads
🖼️ Custom thumbnails
⚡ Fast downloads

Jaldi se apne favorite anime download karein! 🚀
"""
    # Sabhi purane users ko message bhejenge
    for uid in list(db.get('users', {}).keys()):
        try:
            await c.send_message(uid, broadcast_msg)
            success += 1
        except:
            failed += 1
        await asyncio.sleep(0.1)  # Telegram API flood se bachne ke liye delay

    # Admin ko report bhej do
    try:
        await c.send_message(db['owner_id'], f"📢 **Free Access Broadcast Complete!**\n✅ Sent: {success}\n❌ Failed/Blocked: {failed}")
    except:
        pass


@bot.on_message(filters.command("free"))
async def cmd_free(c, m):
    """Admin command to activate global free access"""
    if not is_admin(m.from_user.id) and not is_owner(m.from_user.id):
        return await m.reply("❌ **Admin only command**")

    if len(m.command) < 2:
        return await m.reply("❌ **Usage:** `/free <days>`\n\n📌 **Example:** `/free 20` (20 din ke liye free)")

    try:
        days = int(m.command[1])
        if days < 1:
            return await m.reply("❌ Din 1 ya usse zyada hone chahiye.")
    except:
        return await m.reply("❌ **Invalid format!** Sirf number likhein.")

    # 1. Calculate and set Global Expiry Date
    expiry_timestamp = time.time() + (days * 86400) # 86400 seconds in a day
    db['global_free_expiry'] = expiry_timestamp
    save_db()

    # Format date for message
    from datetime import datetime
    expiry_date = datetime.fromtimestamp(expiry_timestamp)
    expiry_str = expiry_date.strftime("%d %b %Y, %I:%M %p")

    await m.reply(f"""
✅ **GLOBAL FREE ACCESS ACTIVATED!**

━━━━━━━━━━━━━━━━━━━━━━
⏳ **Duration:** {days} Days
📅 **Exact Expiry:** {expiry_str}
━━━━━━━━━━━━━━━━━━━━━━

✅ Database updated.
📤 Old users ko background mein broadcast start ho gaya hai...
""")

    # 2. Trigger Broadcast in background
    asyncio.create_task(broadcast_free_access(c, expiry_str))


@bot.on_message(filters.command("unfree"))
async def cmd_unfree(c, m):
    """Admin command to manually stop free access before expiry"""
    if not is_admin(m.from_user.id) and not is_owner(m.from_user.id):
        return await m.reply("❌ **Admin only command**")

    db['global_free_expiry'] = 0
    save_db()
    
    await m.reply("🛑 **GLOBAL FREE ACCESS DEACTIVATED!**\n\nBot ab wapas normal/paid mode mein aa gaya hai.")

@bot.on_message(filters.command("backup"))
async def cmd_backup(c, m):
    """Manual backup command"""
    if not is_owner(m.from_user.id):
        return await m.reply("❌ Owner only")
    
    msg = await m.reply("📦 **Creating backup...**")
    
    try:
        zip_files, stats = await create_backup()
        
        if zip_files:
            await msg.edit("📤 **Sending to channel...**")
            success = await send_backup_to_channel(zip_files, stats)
            
            if success:
                await msg.edit("✅ **Backup completed!**\n\nSent to backup channel.")
            else:
                await msg.edit("❌ **Failed to send backup!**")
        else:
            await msg.edit("❌ **Backup creation failed!**")
    except Exception as e:
        await msg.edit(f"❌ **Error:** {str(e)[:100]}")

# ==========================================
# DATA RESTORE & REFERRAL UNBAN COMMANDS
# ==========================================

@bot.on_message(filters.command("update"))
async def cmd_update(c, m):
    """Start restore mode - receive backup ZIP files"""
    if not is_owner(m.from_user.id):
        return await m.reply("❌ Owner only")
    
    await m.reply("""📦 **DATABASE RESTORE MODE**

━━━━━━━━━━━━━━━━━━━━━━
📤 **Send backup ZIP files**

Send the backup files that bot sent to backup channel:
• backup_2024-01-15_part1.zip
• backup_2024-01-15_part2.zip
• etc.

━━━━━━━━━━━━━━━━━━━━━━
⚠️ After sending all files, use:
`/restore confirm`

━━━━━━━━━━━━━━━━━━━━━━
🔄 Restore mode activated!
📤 Start sending ZIP files now...
""")
    
    # Set restore mode
    if 'restore_mode' not in db:
        db['restore_mode'] = {}
    
    db['restore_mode'][m.from_user.id] = {
        'active': True,
        'files': [],
        'started': time.time()
    }
    save_db()


@bot.on_message(filters.document & filters.private)
async def handle_restore_files(c, m):
    """Auto-receive backup ZIP files"""
    uid = m.from_user.id
    
    # Check if in restore mode
    if uid not in db.get('restore_mode', {}) or not db['restore_mode'][uid].get('active'):
        return
    
    if not is_owner(uid):
        return
    
    # ✅ FIX: Check timeout (1 hour)
    started = db['restore_mode'][uid].get('started', 0)
    if time.time() - started > 3600:  # 1 hour
        del db['restore_mode'][uid]
        save_db()
        return await m.reply("❌ **Restore mode expired** (1 hour timeout)\n\nUse `/update` again to restart.")
    
    file_name = m.document.file_name
    
    # Only accept ZIP files
    if not file_name.endswith('.zip'):
        return await m.reply("❌ Only ZIP files accepted!\n\nSend backup ZIP files from channel.")
    
    msg = await m.reply("📥 **Downloading...**")
    
    try:
        # Download ZIP
        file_path = await m.download(file_name=os.path.join(BACKUP_DIR, file_name))
        
        # ✅ FIX: Validate ZIP file
        import zipfile
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                file_list = z.namelist()
                # Check if it contains backup data
                if not any('_data.pkl' in fname or '_stats.json' in fname for fname in file_list):
                    os.remove(file_path)
                    return await msg.edit("❌ **Not a valid backup file!**\n\nThis ZIP doesn't contain backup data.")
        except zipfile.BadZipFile:
            os.remove(file_path)
            return await msg.edit("❌ **Corrupted ZIP file!**\n\nPlease send a valid backup file.")
        
        db['restore_mode'][uid]['files'].append({
            'name': file_name,
            'path': file_path,
            'size': os.path.getsize(file_path)
        })
        save_db()
        
        count = len(db['restore_mode'][uid]['files'])
        
        await msg.edit(f"""✅ **Received!**

📦 {file_name}
💾 {fmt_bytes(os.path.getsize(file_path))}

━━━━━━━━━━━━━━━━━━━━━━
📊 Total Files: {count}

{"📤 Send more or `/restore confirm`" if count >= 1 else ""}
━━━━━━━━━━━━━━━━━━━━━━
""")
        
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)[:100]}")


@bot.on_message(filters.command("restore"))
async def cmd_restore(c, m):
    """Apply backup restore"""
    global db  # ✅ ADD THIS LINE
    
    if not is_owner(m.from_user.id):
        return await m.reply("❌ Owner only")
    
    uid = m.from_user.id
    
    if uid not in db.get('restore_mode', {}) or not db['restore_mode'][uid].get('active'):
        return await m.reply("❌ Not in restore mode!\n\nUse `/update` first.")
    
    files = db['restore_mode'][uid].get('files', [])
    
    if not files:
        return await m.reply("❌ No files received!\n\nSend backup ZIP files first.")
    
    # If no "confirm" - show buttons
    if len(m.command) < 2 or m.command[1].lower() != 'confirm':
        files_list = "\n".join([f"• {f['name']}" for f in files])
        
        btns = [
            [InlineKeyboardButton("✅ CONFIRM", callback_data="restore_yes")],
            [InlineKeyboardButton("❌ Cancel", callback_data="restore_no")]
        ]
        
        return await m.reply(f"""⚠️ **CONFIRM RESTORE**

━━━━━━━━━━━━━━━━━━━━━━
📦 Files: {len(files)}
━━━━━━━━━━━━━━━━━━━━━━
{files_list}

━━━━━━━━━━━━━━━━━━━━━━
⚠️ Current data will be REPLACED!
━━━━━━━━━━━━━━━━━━━━━━
""", reply_markup=InlineKeyboardMarkup(btns))
    
    # ✅ ADD THIS ELSE BLOCK - When "confirm" is typed
    else:
        msg = await m.reply("⏳ **Processing restore...**")
        
        try:
            import zipfile
            
            # Extract all ZIPs
            extracted_files = []
            for f in files:
                with zipfile.ZipFile(f['path'], 'r') as zip_ref:
                    zip_ref.extractall(BACKUP_DIR)
                    extracted_files.extend(zip_ref.namelist())
            
            # Find .pkl file
            pkl_file = None
            for fname in extracted_files:
                if fname.endswith('_data.pkl'):
                    pkl_file = os.path.join(BACKUP_DIR, fname)
                    break
            
            if not pkl_file or not os.path.exists(pkl_file):
                raise Exception("No database file found in backup!")
            
            # Emergency backup
            emergency = os.path.join(BACKUP_DIR, f"emergency_{int(time.time())}.pkl")
            try:
                shutil.copy2(DB_FILE, emergency)
            except:
                pass
            
            # Load new DB
            with open(pkl_file, 'rb') as f:
                new_db = pickle.load(f)
            
            old_owner = db.get('owner_id')
            
            db.clear()
            db.update(new_db)
            db['owner_id'] = old_owner

            if isinstance(db.get('admins'), list):
                db['admins'] = set(db['admins'])
            if isinstance(db.get('banned'), list):
                db['banned'] = set(db['banned'])

            if 'admins' not in db:
                db['admins'] = set()
            if 'banned' not in db:
                db['banned'] = set()
            if 'users' not in db:
                db['users'] = {}
            if 'monitored' not in db:
                db['monitored'] = {}
            if 'thumbnails' not in db:
                db['thumbnails'] = {}
            if 'thumb_last_used' not in db:
                db['thumb_last_used'] = {}
            if 'captions' not in db:
                db['captions'] = {}
            if 'premium_users' not in db:
                db['premium_users'] = {}
            if 'master_unlocked' not in db:
                db['master_unlocked'] = set()
            if 'settings' not in db:
                db['settings'] = {'default_interval': 3}
            
            if 'restore_mode' in db:
                del db['restore_mode']
            
            save_db()
            
            # Cleanup
            for f in files:
                try:
                    os.remove(f['path'])
                except:
                    pass
            for fname in extracted_files:
                try:
                    os.remove(os.path.join(BACKUP_DIR, fname))
                except:
                    pass
            
            await msg.edit(f"""✅ **RESTORE COMPLETE!**

━━━━━━━━━━━━━━━━━━━━━━
👥 Users: {len(db.get('users', {}))}
📺 Monitored: {len(db.get('monitored', {}))}
💎 Premium: {len(db.get('premium_users', {}))}
🎁 Referrals: {len(db.get('referrals', {}))}

━━━━━━━━━━━━━━━━━━━━━━
🔄 Restarting in 5 seconds...
━━━━━━━━━━━━━━━━━━━━━━
""")
            
            await asyncio.sleep(5)
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        except Exception as e:
            await msg.edit(f"❌ **Failed!**\n\n{str(e)[:200]}")
            traceback.print_exc()

@bot.on_callback_query(filters.regex(r"^restore_"))
async def cb_restore(c, q):
    global db  # ✅ FIRST LINE mein move karo!
    
    if not is_owner(q.from_user.id):
        return await q.answer("❌ Owner only", show_alert=True)
    
    uid = q.from_user.id
    
    if q.data == "restore_no":
        # Cleanup
        if uid in db.get('restore_mode', {}):
            for f in db['restore_mode'][uid].get('files', []):
                try:
                    os.remove(f['path'])
                except:
                    pass
            del db['restore_mode'][uid]
            save_db()
        
        return await q.message.edit("❌ **Cancelled**")
    
    # Process restore
    await q.message.edit("⏳ **Processing...**")
    
    try:
        import zipfile
        
        files = db['restore_mode'][uid]['files']
        
        # Extract all ZIPs
        extracted_files = []
        for f in files:
            with zipfile.ZipFile(f['path'], 'r') as zip_ref:
                zip_ref.extractall(BACKUP_DIR)
                extracted_files.extend(zip_ref.namelist())
        
        # Find .pkl file
        pkl_file = None
        for fname in extracted_files:
            if fname.endswith('_data.pkl'):
                pkl_file = os.path.join(BACKUP_DIR, fname)
                break
        
        if not pkl_file or not os.path.exists(pkl_file):
            raise Exception("No database file found in backup!")
        
        # Emergency backup
        emergency = os.path.join(BACKUP_DIR, f"emergency_{int(time.time())}.pkl")
        try:
            shutil.copy2(DB_FILE, emergency)
        except:
            pass
        
        # Load new DB
        with open(pkl_file, 'rb') as f:
            new_db = pickle.load(f)
        
        # ✅ global db already declared at top - no need here
        old_owner = db.get('owner_id')
        
        db.clear()
        db.update(new_db)
        db['owner_id'] = old_owner

        if isinstance(db.get('admins'), list):
            db['admins'] = set(db['admins'])
        if isinstance(db.get('banned'), list):
            db['banned'] = set(db['banned'])
        if isinstance(db.get('master_unlocked'), list):
            db['master_unlocked'] = set(db['master_unlocked'])

        if 'admins' not in db:
            db['admins'] = set()
        if 'banned' not in db:
            db['banned'] = set()
        if 'users' not in db:
            db['users'] = {}
        if 'monitored' not in db:
            db['monitored'] = {}
        if 'thumbnails' not in db:
            db['thumbnails'] = {}
        if 'thumb_last_used' not in db:
            db['thumb_last_used'] = {}
        if 'captions' not in db:
            db['captions'] = {}
        if 'premium_users' not in db:
            db['premium_users'] = {}
        if 'settings' not in db:
            db['settings'] = {'default_interval': 3}
        
        if 'restore_mode' in db:
            del db['restore_mode']
        
        save_db()
        
        # Cleanup
        for f in files:
            try:
                os.remove(f['path'])
            except:
                pass
        for fname in extracted_files:
            try:
                os.remove(os.path.join(BACKUP_DIR, fname))
            except:
                pass
        
        await q.message.edit(f"""✅ **RESTORE COMPLETE!**

━━━━━━━━━━━━━━━━━━━━━━
👥 Users: {len(db.get('users', {}))}
📺 Monitored: {len(db.get('monitored', {}))}
💎 Premium: {len(db.get('premium_users', {}))}

━━━━━━━━━━━━━━━━━━━━━━
🔄 Restarting in 5 seconds...
━━━━━━━━━━━━━━━━━━━━━━
""")
        
        await asyncio.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    except Exception as e:
        await q.message.edit(f"❌ **Failed!**\n\n{str(e)[:200]}")
        traceback.print_exc()

@bot.on_message(filters.command("admin"))
async def cmd_admin(c, m):
    if not is_owner(m.from_user.id): 
        return await m.reply("❌ **Owner Only!**\n\nThis command is restricted to bot owner.")
    
    if len(m.command) < 2: 
        return await m.reply("❌ **Usage:** `/admin <UserID>`\n\n**Example:** `/admin 123456789`")
    
    try: 
        t = int(m.command[1])
    except: 
        return await m.reply("❌ **Invalid ID!**\n\nPlease provide a valid numeric User ID.")
    
    if t == db['owner_id']:
        return await m.reply("❌ **Cannot add owner as admin!**\n\nOwner already has all permissions.")
    
    if t in db['admins']:
        return await m.reply(f"⚠️ **Already Admin!**\n\nUser `{t}` is already an admin.")
    
    db['admins'].add(t)
    save_db()
    
    await m.reply(f"""✅ **Admin Added!**

━━━━━━━━━━━━━━━━━━━━━━
👤 User ID: `{t}`
⚔️ Role: Admin
👮 Added by: {m.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # Notify new admin
    try:
        await c.send_message(t, f"""⚔️ **Admin Access Granted!**

━━━━━━━━━━━━━━━━━━━━━━
You are now an admin of this bot.

Use /start to see admin commands.
━━━━━━━━━━━━━━━━━━━━━━
""")
    except:
        await m.reply("⚠️ Could not notify user (user hasn't started bot)")

@bot.on_message(filters.command("radmin"))
async def cmd_radmin(c, m):
    if not is_owner(m.from_user.id): 
        return await m.reply("❌ **Owner Only!**\n\nThis command is restricted to bot owner.")
    
    if len(m.command) < 2: 
        return await m.reply("❌ **Usage:** `/radmin <UserID>`\n\n**Example:** `/radmin 123456789`")
    
    try: 
        t = int(m.command[1])
    except: 
        return await m.reply("❌ **Invalid ID!**\n\nPlease provide a valid numeric User ID.")
    
    if t not in db['admins']:
        return await m.reply(f"⚠️ **Not an Admin!**\n\nUser `{t}` is not in admin list.")
    
    db['admins'].discard(t)
    save_db()
    
    await m.reply(f"""✅ **Admin Removed!**

━━━━━━━━━━━━━━━━━━━━━━
👤 User ID: `{t}`
🔓 Role: User (demoted)
?? Removed by: {m.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # Notify removed admin
    try:
        await c.send_message(t, "⚠️ **Admin Access Revoked**\n\nYour admin privileges have been removed.")
    except:
        pass

@bot.on_message(filters.command("seeadmin"))
async def cmd_seeadmin(c, m):
    if not is_owner(m.from_user.id): 
        return await m.reply("❌ **Owner Only!**\n\nThis command is restricted to bot owner.")
    
    if not db['admins']: 
        return await m.reply("⚔️ **No Admins**\n\nNo admins added yet.\n\nUse `/admin <UserID>` to add.")
    
    admin_list = ""
    for i, uid in enumerate(db['admins'], 1):
        try:
            user = await c.get_users(uid)
            name = user.first_name
            username = f"@{user.username}" if user.username else "No username"
        except:
            name = "Unknown"
            username = "N/A"
        
        admin_list += f"{i}. **{name}**\n   📱 ID: `{uid}`\n   👤 {username}\n\n"
    
    await m.reply(f"""⚔️ **ADMIN LIST**

━━━━━━━━━━━━━━━━━━━━━━
{admin_list}
━━━━━━━━━━━━━━━━━━━━━━
📊 Total: {len(db['admins'])} admins
""")

@bot.on_message(filters.command("reset"))
async def cmd_reset(c, m):
    if not is_owner(m.from_user.id): return
    btns = [[InlineKeyboardButton("⚠️ YES", callback_data="reset_yes")], [InlineKeyboardButton("❌ No", callback_data="reset_no")]]
    await m.reply("⚠️ **Reset ALL?**", reply_markup=InlineKeyboardMarkup(btns))

@bot.on_callback_query(filters.regex(r"^reset_"))
async def cb_reset(c, q):
    if not is_owner(q.from_user.id): return
    if q.data == "reset_no": return await q.message.edit("❌ Cancelled")
    o = db['owner_id']
    db.update({'admins': set(), 'banned': set(), 'users': {}, 'monitored': {}, 'thumbnails': {}, 'thumb_last_used': {}, 'owner_id': o})
    save_db()
    await q.message.edit("✅ **Reset!**")

@bot.on_message(filters.command("domain"))
async def cmd_domain(c, m):
    """Domain change - case insensitive, full coverage"""
    uid = m.from_user.id
    
    if not is_admin(uid):
        return await m.reply("❌ Admin only")
    
    args = m.text.split()
    
    if len(args) < 4 or args[2].lower() != 'to':
        return await m.reply("""
🔗 **DOMAIN CHANGE**
━━━━━━━━━━━━━━━━━━━━━━

📝 **Usage:**
`/domain old_domain to new_domain`

📌 **Example:**
`/domain toono.in to toono.app`
`/domain raretoonsindia.com to rareanimes.app`
━━━━━━━━━━━━━━━━━━━━━━
""")
    
    old_domain = args[1].lower().replace('https://', '').replace('http://', '').strip('/')
    new_domain = args[3].lower().replace('https://', '').replace('http://', '').strip('/')
    
    msg = await m.reply(f"⏳ **Processing...**\n\n`{old_domain}` → `{new_domain}`")
    
    changes = 0
    affected_anime = []
    
    for key, data in db.get('monitored', {}).items():
        changed = False
        
        for field in ['series_url', 'monitor_url']:
            if field in data and data[field]:
                # Case-insensitive replacement
                new_val = re.sub(re.escape(old_domain), new_domain, data[field], flags=re.IGNORECASE)
                
                if new_val != data[field]:
                    data[field] = new_val
                    changes += 1
                    changed = True
        
        if changed:
            affected_anime.append(data.get('series_name', 'Unknown'))
    
    # Also update SUPPORTED_WEBSITES patterns
    for site_key, site_data in SUPPORTED_WEBSITES.items():
        new_patterns = []
        pattern_changed = False
        
        for pattern in site_data['patterns']:
            if old_domain in pattern.lower():
                new_pattern = re.sub(re.escape(old_domain), new_domain, pattern, flags=re.IGNORECASE)
                new_patterns.append(new_pattern)
                pattern_changed = True
            else:
                new_patterns.append(pattern)
        
        # Add new domain as extra pattern
        if pattern_changed:
            if new_domain not in new_patterns:
                new_patterns.append(new_domain)
            site_data['patterns'] = new_patterns
            changes += 1
    
    save_db()
    
    anime_list = "\n".join([f"   • {name}" for name in affected_anime]) if affected_anime else "   • None"
    
    await msg.edit(f"""
✅ **DOMAIN UPDATED!**
━━━━━━━━━━━━━━━━━━━━━━

🔄 `{old_domain}` → `{new_domain}`

📊 URLs Updated: **{changes}**

━━━━━━━━━━━━━━━━━━━━━━
📺 **Affected Anime:**
{anime_list}
━━━━━━━━━━━━━━━━━━━━━━
""")

@bot.on_message(filters.command("dashboard"))
async def cmd_dashboard(c, m):
    """Full system dashboard - Owner only"""
    if not is_owner(m.from_user.id): 
        return await m.reply("❌ Owner only")
    
    import platform
    
    # Get system stats
    stats = get_system_stats()
    
    # Get ping
    start_ping = time.time()
    try:
        await c.get_me()
        ping_ms = (time.time() - start_ping) * 1000
    except:
        ping_ms = 0
    
    # Worker stats
    working = sum(1 for s in worker_status.values() if s == "working")
    idle_count = sum(1 for s in worker_status.values() if s == "idle")
    
    # Database stats
    total_users = len(db.get('users', {}))
    premium_users = len(db.get('premium_users', {}))
    total_admins = len(db.get('admins', set()))
    total_monitored = len(db.get('monitored', {}))
    total_thumbnails = sum(len(t) for t in db.get('thumbnails', {}).values())
    total_captions = len(db.get('captions', {}))
    total_channels = sum(len(ch) for ch in db.get('channels', {}).values())
    banned_users = len(db.get('banned', set()))
    
    # Queue stats
    queue_size = len(task_queue)
    active_count = len(active_downloads)
    
    # Build message
    msg = f"""
╔═════════════════╗
║  🎌 **DASHBOARD** ║
╚═════════════════╝

━━━━━━━━━━━━━━━━━━━━━━
📡 **CONNECTION**
━━━━━━━━━━━━━━━━━━━━━━
🏓 Ping: **{ping_ms:.2f} ms**
🐍 Python: **{platform.python_version()}**
"""
    
    if stats:
        ram_pct = stats['ram_percent']
        disk_pct = stats['disk_percent']
        cpu_pct = stats['cpu_percent']
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━
💻 **SYSTEM RESOURCES**
━━━━━━━━━━━━━━━━━━━━━━
🧠 RAM: {stats['ram_used']:.1f}GB / {stats['ram_total']:.1f}GB ({ram_pct:.1f}%)
💿 Disk: {stats['disk_used']:.1f}GB / {stats['disk_total']:.1f}GB ({disk_pct:.1f}%)
⚡ CPU: {cpu_pct:.1f}%
"""
    
    msg += f"""
━━━━━━━━━━━━━━━━━━━━━━
👷 **WORKERS**
━━━━━━━━━━━━━━━━━━━━━━
📦 Total: **{TOTAL_WORKERS}**
🟢 Message: **1**
🔵 Download: **{MAX_DOWNLOAD_WORKERS}** (Working: {working}, Idle: {idle_count})
📤 Upload: **{MAX_UPLOAD_PARALLEL}**

━━━━━━━━━━━━━━━━━━━━━━
📊 **QUEUE**
━━━━━━━━━━━━━━━━━━━━━━
📋 Queue: **{queue_size}/{MAX_QUEUE}**
📥 Active: **{active_count}**

━━━━━━━━━━━━━━━━━━━━━━
👥 **USERS**
━━━━━━━━━━━━━━━━━━━━━━
👤 Total: **{total_users}**
💎 Premium: **{premium_users}**
⚔️ Admins: **{total_admins}**
🚫 Banned: **{banned_users}**

━━━━━━━━━━━━━━━━━━━━━━
📺 **DATA**
━━━━━━━━━━━━━━━━━━━━━━
🎬 Monitored: **{total_monitored}**
🖼️ Thumbnails: **{total_thumbnails}**
📝 Captions: **{total_captions}**
📢 Channels: **{total_channels}**

━━━━━━━━━━━━━━━━━━━━━━
👑 Owner: `{db['owner_id']}`
━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await m.reply(msg)
    
@bot.on_message(filters.text & filters.private & ~filters.command([
    'start', 'set', 'batch', 'list', 'del', 'time', 'status', 'gstatus',
    'cleanup', 'thum', 'seethum', 'delthum', 'setcaption', 'seecaption',
    'delcaption', 'ban', 'unban', 'seeban', 'admin', 'radmin', 'seeadmin',
    'reset', 'dashboard', 'pm', 'repm', 'pmlist', 'npcleanup',
    'backup', 'update', 'restore', 'validate', 'domain', 'broadcast',
    'cleanupspace', 'website', 'addchannel', 'seechannel', 'delchannel',
    'cancel'
]))
async def auto_url_handler(c, m):
    text = m.text.strip()
    if text.startswith("http://") or text.startswith("https://"):
        await handle_url(c, m)

# ==========================================
# START
# ==========================================
async def main():
    global download_semaphore, upload_semaphore, batch_semaphore, queue_lock

    print("\n" + "="*50)
    print("🎌 ANIME AUTO DOWNLOADER v12.0")
    print("="*50)

    load_db()
    print(f"👑 Owner: {db['owner_id']}")
    print(f"📊 Users: {len(db['users'])} | Series: {len(db['monitored'])}")

    download_semaphore = asyncio.Semaphore(MAX_DOWNLOAD_WORKERS)
    upload_semaphore = asyncio.Semaphore(MAX_UPLOAD_PARALLEL)
    batch_semaphore = asyncio.Semaphore(MAX_BATCH_WORKERS)
    queue_lock = asyncio.Lock()

    await bot.start()
    me = await bot.get_me()
    
    # ✅ FIX: Cache bot username globally
    global BOT_USERNAME
    BOT_USERNAME = me.username
    
    print(f"✅ @{BOT_USERNAME}")

    for i in range(MAX_DOWNLOAD_WORKERS):
        asyncio.create_task(download_worker(i))
    print(f"⚙️ {MAX_DOWNLOAD_WORKERS} download workers")

    asyncio.create_task(monitor())
    asyncio.create_task(auto_cleanup())
    asyncio.create_task(thumb_cleanup())
    asyncio.create_task(premium_expiry_monitor())
    asyncio.create_task(backup_scheduler())
    print("🔄 Background tasks started")

    print(f"\n🟢 Message Worker: Always Free")
    print(f"🔵 Download Workers: {MAX_DOWNLOAD_WORKERS}")
    print(f"🟡 Batch Workers: {MAX_BATCH_WORKERS}")
    print(f"📤 Upload Slots: {MAX_UPLOAD_PARALLEL}")
    print("="*50 + "\n")

    await idle()
    save_db()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())