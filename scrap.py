import os
import re
import json
import time
import asyncio
import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self):
        self.BASE_DIR = "/tmp/bot_data"
        self.DOWNLOAD_DIR = f"{self.BASE_DIR}/Downloads"
        self.THUMB_DIR = f"{self.BASE_DIR}/Thumbnails"
        self.CONFIG_FILE = f"{self.BASE_DIR}/config.json"
        self.USERS_FILE = f"{self.BASE_DIR}/users.json"
        self.USER_DATA_DIR = f"{self.BASE_DIR}/user_data"

        self.QUALITIES = ["480p", "720p", "1080p"]
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        for d in [self.BASE_DIR, self.DOWNLOAD_DIR, self.THUMB_DIR, self.USER_DATA_DIR]:
            os.makedirs(d, exist_ok=True)

    # ─── HELPERS ────────────────────────────────────────────────────────────────

    def _session(self):
        s = requests.Session()
        s.headers.update({"User-Agent": self.UA})
        return s

    def clean_name(self, title):
        if not title: return ""
        for p in [r'\s+Hindi.*$', r'\s+Multi.*$', r'\s+Dual.*$',
                  r'\s*-\s*Hindi\s*Anime\s*Zone.*$', r'HindiAnimeZone',
                  r'\[.*?\]', r'\(.*?Dubbed\)', r'\(Media-link.*?\)']:
            title = re.sub(p, '', title, flags=re.IGNORECASE)
        m = re.search(r'(.*?Season\s*\d+)', title, re.IGNORECASE)
        if m: title = m.group(1)
        return re.sub(r'\s+', ' ', title).strip()

    def similarity_ratio(self, a, b):
        return 1.0 if a.lower() == b.lower() else 0.0

    def get_best_matching_thumbnail(self, anime_name, thumbs):
        if not thumbs: return None
        best_match, best_ratio = None, 0.67
        for tname in thumbs:
            r = self.similarity_ratio(anime_name, tname)
            if r > best_ratio:
                best_ratio, best_match = r, tname
        if best_match:
            print(f"📸 Matched: '{best_match}' ({best_ratio*100:.0f}%)")
            return thumbs[best_match]
        return None

    def get_season(self, name):
        m = re.search(r'Season\s*(\d+)', name, re.IGNORECASE)
        return m.group(1).zfill(2) if m else "01"

    def get_anime_only(self, name):
        return re.sub(r'\s*Season\s*\d+', '', name, flags=re.IGNORECASE).strip() or name

    def clear_downloads(self):
        if os.path.exists(self.DOWNLOAD_DIR):
            for f in os.listdir(self.DOWNLOAD_DIR):
                try: os.remove(os.path.join(self.DOWNLOAD_DIR, f))
                except: pass

    # ─── METADATA ───────────────────────────────────────────────────────────────

    async def get_metadata(self, path):
        w, h, d = 0, 0, 0
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(path)]
            proc = await asyncio.create_subprocess_exec(*cmd,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
            d = int(float(json.loads(stdout).get('format', {}).get('duration', 0)))
        except: pass
        return w, h, d

    async def get_audio(self, path):
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                   '-show_streams', '-select_streams', 'a', str(path)]
            proc = await asyncio.create_subprocess_exec(*cmd,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
            streams = json.loads(stdout).get('streams', [])
            lang_map = {'hin': 'Hindi', 'hi': 'Hindi', 'eng': 'English',
                        'en': 'English', 'jpn': 'Japanese', 'ja': 'Japanese'}
            langs = []
            for st in streams:
                l = st.get('tags', {}).get('language', '').lower()
                if l in lang_map and lang_map[l] not in langs:
                    langs.append(lang_map[l])
            if langs: return ", ".join(langs)
            return "Multi Audio" if len(streams) > 1 else "Japanese"
        except: return "Multi Audio"

    async def make_thumb(self, video, output):
        try:
            cmd = f'ffmpeg -i "{video}" -ss 00:00:05 -vframes 1 -vf "scale=320:-1" "{output}" -y 2>/dev/null'
            os.system(cmd)
            return output if os.path.exists(output) else None
        except: return None

    # ─── SITE SCRAPING ──────────────────────────────────────────────────────────

    async def get_page_title(self, url):
        try:
            print(f"🔍 Getting Title: {url}")
            r = self._session().get(url, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                if soup.title and soup.title.string:
                    return self.clean_name(soup.title.string)
        except Exception as e:
            print(f"⚠️ Title Error: {e}")
        return "Unknown Anime"

    async def check_latest(self, url):
        try:
            print(f"🔍 Checking latest: {url}")
            r = self._session().get(url, timeout=15)
            if r.status_code != 200:
                print(f"❌ Status: {r.status_code}")
                return None
            nums = re.findall(r'Episode\s+(\d+)', r.text, re.IGNORECASE)
            if not nums:
                nums = re.findall(r'Ep\s+(\d+)', r.text, re.IGNORECASE)
            latest = max(int(n) for n in nums) if nums else None
            print(f"✅ Latest: {latest}")
            return latest
        except Exception as e:
            print(f"⚠️ check_latest error: {e}")
            return None

    # ─── LINK RESOLUTION ────────────────────────────────────────────────────────

    async def _resolve_hindianimezone_link(self, s, url):
        """
        like.hindianimezone.com/download1.php?code=...&q=...
        Step 1: GET to set cookies
        Step 2: POST verify=1 to unlock actual download host links
        Step 3: Pick GDShare link and resolve it
        """
        try:
            print(f"   🔓 Verifying HAZ link...")
            s.get(url, timeout=15)
            r = s.post(url, data={'verify': '1'}, timeout=20,
                       headers={'Referer': 'https://like.hindianimezone.com/'})
            soup = BeautifulSoup(r.text, 'html.parser')

            # Priority: GDShare (→ GCloud → FSL R2 direct)
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if 'gdshare' in href and href.startswith('http'):
                    print(f"   ✅ Got GDShare link: {href[:60]}")
                    return await self._resolve_gdshare(s, href)

            # Fallback: FilePress
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                if 'filepress' in href and href.startswith('http'):
                    print(f"   🔄 Fallback to FilePress: {href[:60]}")
                    return await self._resolve_gdshare_via_filepress(s, href)

        except Exception as e:
            print(f"   ⚠️ _resolve_hindianimezone_link: {e}")
        return None

    async def _resolve_gdshare(self, s, gdshare_url):
        """
        GDShare → GCloud → HTMX generate-links → FSL (Cloudflare R2) direct URL
        """
        try:
            print(f"   🔗 Following GDShare → GCloud...")
            r = s.get(gdshare_url, timeout=20, allow_redirects=True)
            gcloud_page_url = r.url
            print(f"   📍 GCloud URL: {gcloud_page_url[:80]}")

            # Find the HTMX generate-links endpoint
            hx_match = re.search(r'hx-get="(/download/[^"]+/generate-links/)"', r.text)
            if not hx_match:
                soup = BeautifulSoup(r.text, 'html.parser')
                gen_btn = soup.find(id='generate-btn')
                hx_get = gen_btn.get('hx-get', '') if gen_btn else ''
            else:
                hx_get = hx_match.group(1)

            if not hx_get:
                print("   ⚠️ No generate-links endpoint found")
                return None

            gen_url = 'https://gcloud.sbs' + hx_get
            print(f"   🔄 Calling generate-links...")
            r2 = s.get(gen_url,
                       headers={'X-Requested-With': 'XMLHttpRequest',
                                'Referer': gcloud_page_url},
                       timeout=25)

            # The generated page usually exposes several mirrors. R2/FSL can
            # be blocked by Cloudflare from server environments, while the
            # Pixeldrain API remains directly downloadable. Prefer it when
            # available and keep the other mirrors as fallbacks.
            result_soup = BeautifulSoup(r2.text, 'html.parser')

            pixeldrain_link = result_soup.find(id='pixeldrain-web-link')
            if pixeldrain_link and pixeldrain_link.get('href'):
                pixeldrain_url = pixeldrain_link['href']
                print(f"   ✅ Pixeldrain mirror: {pixeldrain_url[:80]}")
                return pixeldrain_url

            # Extract FSL (R2 direct) link as the first fallback
            fsl_match = re.search(
                r'id="fsl-download-link"[^>]*href="([^"]+)"'
                r'|href="([^"]+)"[^>]*id="fsl-download-link"', r2.text)
            if fsl_match:
                fsl_url = fsl_match.group(1) or fsl_match.group(2)
                print(f"   ✅ FSL R2 URL: {fsl_url[:80]}")
                return fsl_url

            # Fallback: any r2.dev URL in the response
            r2_urls = re.findall(r'https://[^\s"\'<>]*r2\.dev/[^\s"\'<>]+', r2.text)
            if r2_urls:
                print(f"   ✅ R2 fallback: {r2_urls[0][:80]}")
                return r2_urls[0]

            # Fallback 2: instant download link (GDShare instant)
            instant_match = re.search(
                r'id="instant-download-link"[^>]*href="([^"]+)"'
                r'|href="([^"]+)"[^>]*id="instant-download-link"', r2.text)
            if instant_match:
                instant_url = instant_match.group(1) or instant_match.group(2)
                print(f"   🔄 Trying instant download: {instant_url[:80]}")
                r3 = s.get(instant_url, timeout=20, allow_redirects=True, stream=True)
                ct = r3.headers.get('Content-Type', '')
                if 'application' in ct or 'video' in ct or 'octet' in ct:
                    print(f"   ✅ Instant direct: {r3.url[:80]}")
                    return r3.url
                # Might redirect to R2
                if 'r2.dev' in r3.url:
                    return r3.url

        except Exception as e:
            print(f"   ⚠️ _resolve_gdshare: {e}")
        return None

    async def _resolve_gdshare_via_filepress(self, s, filepress_url):
        """Resolve FilePress link via GCloud filepressCreateUrl API."""
        try:
            # FilePress links are usually on GCloud pages too
            # Just return None - GDShare is the preferred path
            pass
        except Exception as e:
            print(f"   ⚠️ _resolve_filepress: {e}")
        return None

    async def resolve_link(self, s, url):
        """Main link resolver — dispatches based on URL type."""
        if not url:
            return None

        # Direct R2 / content CDN — already a direct link
        if 'r2.dev' in url:
            return url

        # HindiAnimeZone shortlink page
        if 'like.hindianimezone.com' in url or ('hindianimezone' in url and 'download' in url):
            return await self._resolve_hindianimezone_link(s, url)

        # GDShare / GCloud
        if 'gdshare' in url or 'gcloud.sbs' in url:
            return await self._resolve_gdshare(s, url)

        # Legacy: Pixeldrain (keep for older episodes)
        if 'pixeldrain' in url:
            return url

        # Generic follow-redirects for anything else
        try:
            r = s.get(url, timeout=15, allow_redirects=True)
            if 'r2.dev' in r.url:
                return r.url
            r2_found = re.findall(r'https://[^\s"\'<>]*r2\.dev/[^\s"\'<>]+', r.text)
            if r2_found:
                return r2_found[0]
            if 'pixeldrain' in r.url:
                return r.url
        except Exception as e:
            print(f"   ⚠️ resolve_link generic: {e}")

        return url

    # ─── EPISODE EXTRACTION ─────────────────────────────────────────────────────

    async def extract_url(self, quality, ep, url):
        """Find download link for a specific quality + episode on anime page."""
        try:
            print(f"🔍 Extracting {quality} Ep {ep}...")
            s = self._session()
            r = s.get(url, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find episode header
            ep_patterns = [f"Episode {str(ep).zfill(2)}", f"Episode {ep}",
                           f"Ep {str(ep).zfill(2)}", f"Ep {ep}"]
            ep_header = None
            for pat in ep_patterns:
                found = soup.find(string=re.compile(re.escape(pat), re.IGNORECASE))
                if found:
                    ep_header = found
                    print(f"   Found header: {found.strip()[:60]}")
                    break

            target_href = None

            if ep_header:
                header_node = ep_header.find_parent()
                curr = header_node
                for _ in range(5):
                    if not curr: break
                    curr = curr.find_next_sibling()
                    if curr and curr.name == 'div':
                        link = curr.find('a', string=re.compile(quality, re.IGNORECASE))
                        if not link:
                            link = curr.find('a', class_=lambda c: c and quality in c)
                        if link:
                            target_href = link.get('href')
                            print(f"   Found link: {target_href[:70] if target_href else 'None'}...")
                            break

            if not target_href:
                print("   Fallback to index search...")
                all_links = soup.find_all('a', string=re.compile(quality, re.IGNORECASE))
                if len(all_links) >= ep:
                    target_href = all_links[ep - 1].get('href')
                    print(f"   Index [{ep-1}]: {(target_href or '')[:70]}...")

            if not target_href:
                return None

            return await self.resolve_link(s, target_href)

        except Exception as e:
            print(f"⚠️ extract_url error: {e}")
            return None

    def _is_valid_url(self, url):
        """Check if URL is a usable direct/resolved download link."""
        if not url:
            return False
        return any(x in url for x in ['r2.dev', 'pixeldrain', 'gdshare.top/instant',
                                        'drivecloud', 'mega.nz'])

    async def extract_all(self, ep, url, msg, name):
        """Extract direct download URLs for all three qualities."""
        urls = {}
        for i, q in enumerate(self.QUALITIES, 1):
            try:
                await msg.edit_text(f"🔍 Extracting {q}... ({i}/3)\n📺 {name} | Ep {ep}")
            except: pass

            purl = await self.extract_url(q, ep, url)
            if purl and self._is_valid_url(purl):
                urls[q] = purl
                print(f"✅ {q}: {purl[:80]}")
            else:
                print(f"❌ {q}: Not found (got: {purl})")

            await asyncio.sleep(0.5)
        return urls

    # ─── DOWNLOAD ───────────────────────────────────────────────────────────────

    async def download_file(self, direct_url, msg, name, ep, quality):
        """Download any direct URL (R2, Pixeldrain API, etc.)."""
        try:
            s = self._session()

            # Pixeldrain — use their API endpoint
            if 'pixeldrain' in direct_url:
                return await self._download_pixeldrain(direct_url, msg, name, ep, quality, s)

            # Direct R2 or other CDN
            return await self._download_direct(direct_url, msg, name, ep, quality, s)

        except Exception as e:
            print(f"❌ download_file error: {e}")
            return None

    async def _download_direct(self, url, msg, name, ep, quality, s):
        """Stream-download from any direct URL with progress updates."""
        try:
            # Get filename from URL or Content-Disposition
            r_head = s.head(url, timeout=15, allow_redirects=True)
            cd = r_head.headers.get('Content-Disposition', '')
            fname_match = re.search(r'filename[^;=\n]*=(["\']?)([^"\';\n]+)\1', cd)
            if fname_match:
                fname = fname_match.group(2).strip()
            else:
                fname = url.split('/')[-1].split('?')[0]
                if not fname or '.' not in fname:
                    fname = f"{name}_Ep{ep}_{quality}.mkv"

            fname = re.sub(r'[<>:"/\\|?*\[\]]', '_', fname)[:200]
            fpath = os.path.join(self.DOWNLOAD_DIR, fname)
            total = int(r_head.headers.get('Content-Length', 0))

            print(f"📥 Downloading: {fname} ({total/(1024**2):.1f} MB)")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None,
                lambda: self._stream_download(s, url, fpath, msg, name, ep, quality, total))

            if os.path.exists(fpath) and os.path.getsize(fpath) > 1024 * 1024:
                print(f"✅ Downloaded: {fname}")
                return fpath
            print(f"❌ Download too small or missing: {fpath}")
            return None

        except Exception as e:
            print(f"❌ _download_direct: {e}")
            return None

    def _stream_download(self, s, url, fpath, msg, name, ep, quality, total):
        """Synchronous chunked download with periodic progress messages."""
        r = s.get(url, stream=True, timeout=60)
        r.raise_for_status()
        downloaded = 0
        last_report = time.time()

        with open(fpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if now - last_report >= 5 and total > 0:
                        pct = int(downloaded / total * 100)
                        mb_done = downloaded / (1024 ** 2)
                        mb_total = total / (1024 ** 2)
                        ep_text = f"Ep {ep}" if ep else ""
                        try:
                            import asyncio as _asyncio
                            loop = _asyncio.new_event_loop()
                        except: pass
                        # Progress logged to console; Telegram edits happen from async context
                        print(f"   ⬇️ {name} {ep_text} {quality}: {mb_done:.1f}/{mb_total:.1f} MB ({pct}%)")
                        last_report = now

    async def _download_pixeldrain(self, purl, msg, name, ep, quality, s):
        """Legacy Pixeldrain download handler."""
        try:
            purl = purl.replace(".dev", ".com")
            if '/u/' in purl:
                fid = purl.split('/u/')[-1].split('?')[0].split('#')[0].split('/')[0]
            else:
                fid = purl.split('/')[-1].split('?')[0]

            api = f"https://pixeldrain.com/api/file/{fid}"
            try:
                info = s.get(f"https://pixeldrain.com/api/file/{fid}/info", timeout=10).json()
                fname = info.get('name', f"{name}_Ep{ep}_{quality}.mkv")
                total = info.get('size', 0)
            except:
                fname = f"{name}_Ep{ep}_{quality}.mkv"
                total = 0

            fname = re.sub(r'[<>:"/\\|?*\[\]]', '', fname)
            fpath = os.path.join(self.DOWNLOAD_DIR, fname)
            print(f"📥 Pixeldrain: {fname}")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None,
                lambda: self._stream_download(s, api, fpath, msg, name, ep, quality, total))

            if os.path.exists(fpath) and os.path.getsize(fpath) > 1024 * 1024:
                print(f"✅ Downloaded: {fname}")
                return fpath
            return None
        except Exception as e:
            print(f"❌ _download_pixeldrain: {e}")
            return None

    # Keep backward-compatible alias
    async def download_pixeldrain(self, purl, msg, name, ep, quality):
        s = self._session()
        return await self.download_file(purl, msg, name, ep, quality)

    # ─── UTILS ──────────────────────────────────────────────────────────────────

    def get_storage_info(self):
        used_mb, count = 0, 0
        for d in [self.DOWNLOAD_DIR, self.THUMB_DIR]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp):
                        used_mb += os.path.getsize(fp)
                        count += 1
        return {"total": "0", "used": "0", "free": "0",
                "bot_used_mb": f"{used_mb/(1024**2):.1f}", "file_count": count}

    async def delete_later(self, files, delay=150):
        await asyncio.sleep(delay)
        for f in files:
            try: os.remove(f)
            except: pass

    async def rti_download(self, url, msg):
        await msg.edit_text("❌ RTI feature is disabled.")
        return []
