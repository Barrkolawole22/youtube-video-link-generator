import os
import yt_dlp
import random
import logging
import json
import tempfile
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Directories
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Define cookies file path
COOKIES_FILE = "youtube_cookies.txt"

def generate_youtube_cookies():
    """Generate a minimal cookies file that might help with YouTube access.
    This creates a basic cookie file that can help bypass some restrictions."""
    
    try:
        logging.info("Generating YouTube cookies file")
        
        # Create a cookies file
        cookies = [
            {
                "domain": ".youtube.com",
                "expirationDate": (datetime.now() + timedelta(days=365)).timestamp(),
                "hostOnly": False,
                "httpOnly": False,
                "name": "CONSENT",
                "path": "/",
                "sameSite": "no_restriction",
                "secure": False,
                "session": False,
                "storeId": "0",
                "value": "YES+cb",
                "id": 1
            },
            {
                "domain": ".youtube.com",
                "expirationDate": (datetime.now() + timedelta(days=365)).timestamp(),
                "hostOnly": False,
                "httpOnly": False,
                "name": "VISITOR_INFO1_LIVE",
                "path": "/",
                "sameSite": "no_restriction",
                "secure": True,
                "session": False,
                "storeId": "0",
                "value": "random_string_here",
                "id": 2
            }
        ]
        
        # Write temp cookies file
        with open(COOKIES_FILE, "w") as f:
            for cookie in cookies:
                domain = cookie["domain"]
                flag = "TRUE" if not cookie["hostOnly"] else "FALSE"
                path = cookie["path"]
                secure = "TRUE" if cookie["secure"] else "FALSE"
                expiration = int(cookie["expirationDate"]) if "expirationDate" in cookie else 0
                name = cookie["name"]
                value = cookie["value"]
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
        
        logging.info(f"Generated cookies file at {COOKIES_FILE}")
        return True
    except Exception as e:
        logging.error(f"Failed to generate cookies file: {str(e)}")
        return False

# List of user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

def update_ytdlp():
    """Update yt-dlp to the latest version."""
    try:
        import subprocess
        logging.info("Updating yt-dlp...")
        result = subprocess.run(
            ["pip", "install", "--upgrade", "yt-dlp"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"yt-dlp updated successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to update yt-dlp: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Run when the application starts."""
    # Automatically update yt-dlp on startup
    update_ytdlp()
    
    # Get yt-dlp version
    try:
        ydl_version = yt_dlp.version.__version__
        logging.info(f"Using yt-dlp version: {ydl_version}")
    except Exception as e:
        logging.error(f"Error getting yt-dlp version: {str(e)}")
    
    # Generate YouTube cookies
    generate_youtube_cookies()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

# Add routes for specific HTML pages
@app.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/privacy.html", response_class=HTMLResponse)
async def privacy_page(request: Request):
    """Render the privacy policy page."""
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/terms-of-service.html", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Render the terms of service page."""
    return templates.TemplateResponse("terms-of-service.html", {"request": request})

@app.get("/download-app.html", response_class=HTMLResponse)
async def download_app_page(request: Request):
    """Render the download app page."""
    return templates.TemplateResponse("download-app.html", {"request": request})

@app.get("/more-apps.html", response_class=HTMLResponse)
async def more_apps_page(request: Request):
    """Render the more apps page."""
    return templates.TemplateResponse("more-apps.html", {"request": request})

@app.get("/promotions.html", response_class=HTMLResponse)
async def promotions_page(request: Request):
    """Render the promotions page."""
    return templates.TemplateResponse("promotions.html", {"request": request})

@app.get("/about.html", response_class=HTMLResponse)
async def about_page(request: Request):
    """Render the about page."""
    return templates.TemplateResponse("about.html", {"request": request})

# Add routes for platform-specific video downloader pages
@app.get("/threads-video-downloader.html", response_class=HTMLResponse)
async def threads_page(request: Request):
    """Render the Threads video downloader page."""
    return templates.TemplateResponse("threads-video-downloader.html", {"request": request})

@app.get("/twitter-video-downloader.html", response_class=HTMLResponse)
async def twitter_page(request: Request):
    """Render the Twitter video downloader page."""
    return templates.TemplateResponse("twitter-video-downloader.html", {"request": request})

@app.get("/facebook-video-downloader.html", response_class=HTMLResponse)
async def facebook_page(request: Request):
    """Render the Facebook video downloader page."""
    return templates.TemplateResponse("facebook-video-downloader.html", {"request": request})

@app.get("/instagram-video-downloader.html", response_class=HTMLResponse)
async def instagram_page(request: Request):
    """Render the Instagram video downloader page."""
    return templates.TemplateResponse("instagram-video-downloader.html", {"request": request})

@app.get("/youtube-video-downloader.html", response_class=HTMLResponse)
async def youtube_page(request: Request):
    """Render the YouTube video downloader page."""
    return templates.TemplateResponse("youtube-video-downloader.html", {"request": request})

@app.post("/generate-link")
async def generate_link(url: str = Form(...)):
    """Generate download links for the given URL (YouTube, Facebook, Instagram, Twitter, Threads)."""
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Add http/https prefix if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        # Detect platform from URL
        platform = "unknown"
        if "youtube.com" in url or "youtu.be" in url:
            platform = "youtube"
        elif "facebook.com" in url or "fb.com" in url or "fb.watch" in url:
            platform = "facebook"
        elif "instagram.com" in url:
            platform = "instagram"
        elif "twitter.com" in url or "x.com" in url:
            platform = "twitter"
        elif "threads.net" in url or "threads.com" in url:  # Updated to include threads.com
            platform = "threads"
        
        logging.info(f"Processing {platform} URL: {url}")
        
        # Configure yt-dlp options based on the platform
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,  # Don't download, just get info
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "user_agent": random.choice(USER_AGENTS),
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "socket_timeout": 30,
            "http_headers": {  # Initialize http_headers here
                "User-Agent": random.choice(USER_AGENTS)
            }
        }

        # Platform-specific configurations
        if platform == "youtube":
            ydl_opts.update({
                # Use a very simple format selection
                "format": "best",  # Just get the best combined format
                
                # Essential options that help with YouTube specifically
                "ignore_no_formats_error": True,
                "ignoreerrors": True,
                "no_warnings": True,
                
                # Add multiple retries for network issues
                "retries": 10,
                "fragment_retries": 10,
                "extractor_retries": 10,
                
                # Allow cookies to be created
                "nocookies": False,  # Changed from True to allow cookies
                
                # Use simpler player clients that are less likely to be blocked
                "extractor_args": {
                    'youtube': {
                        'player_client': ['android', 'web', 'android_embedded'],  # Try multiple clients
                        'player_skip': ['webpage', 'js', 'configs'],  # Skip more checks that might fail
                        'compat_opts': ['no-youtube-unavailable-videos'],  # Try to get video info even for "unavailable" videos
                    }
                },
                
                # Bypass geo-restrictions
                "geo_bypass": True,
                "geo_bypass_country": "US",
                
                # Use a simpler format sorting approach
                "format_sort": ["+res", "+br", "+fps", "+audio_br"],
            })
            
            # Add cookies file if it exists
            if os.path.exists(COOKIES_FILE):
                ydl_opts["cookiefile"] = COOKIES_FILE
                logging.info("Using YouTube cookies file")
            
            # Add YouTube-specific headers
            ydl_opts["http_headers"].update({
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Fetch-Mode": "navigate"
            })
        elif platform == "facebook":
            ydl_opts.update({
                "extract_flat": False,
                "no_playlist": True,
                "format": "best[ext=mp4]/best",  # Simplified format string
                "extractor_args": {
                    'facebook': {
                        'prefer_mp4_video': ['true'],
                    }
                },
            })
        elif platform == "instagram":
            ydl_opts.update({
                "extract_flat": False,  # Changed from True to ensure full extraction
                "no_playlist": True,
                "format": "best[ext=mp4]/best",  # Simplified format string
            })
        elif platform == "twitter":
            ydl_opts.update({
                "extract_flat": False,
            })
        elif platform == "threads":  # Added Threads-specific configuration
            ydl_opts.update({
                "extract_flat": False,
                "no_playlist": True,
                "format": "best[ext=mp4]/best",  # Simplified format string for Threads
                # Threads is part of Meta, so use Instagram-like extraction approach
                "http_headers": {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.threads.com/",  # Updated domain
                    "Origin": "https://www.threads.com"  # Updated domain
                }
            })
        
        logging.info(f"Extracting info with yt-dlp for {platform}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle playlist or multi-video content
            if 'entries' in info and info['entries']:
                info = info['entries'][0]
            
            # Special case for YouTube: if no formats are extracted initially
            if platform == "youtube" and (not info or not info.get('formats')):
                logging.warning("Initial YouTube extraction failed, trying fallback method")
                
                try:
                    # Try with a much simpler extractor configuration
                    with yt_dlp.YoutubeDL({
                        "quiet": True,
                        "no_warnings": True,
                        "format": "best",  # Just get any working format
                        "user_agent": random.choice(USER_AGENTS),
                        "extractor_args": {
                            'youtube': {
                                'player_client': ['android_embedded'],  # Try mobile client
                            }
                        },
                        "geo_bypass": True,
                    }) as ydl_fallback:
                        fallback_info = ydl_fallback.extract_info(url, download=False)
                        if fallback_info:
                            info = fallback_info
                            logging.info("YouTube fallback method succeeded")
                except Exception as e:
                    logging.error(f"YouTube fallback extraction failed: {str(e)}")
            
            # Special case for Threads: try Instagram extractor if regular extraction fails
            if platform == "threads" and (not info or not info.get('formats')):
                logging.warning("Initial Threads extraction failed, trying Instagram fallback method")
                
                try:
                    # Try with Instagram extractor since Threads is owned by Meta/Instagram
                    with yt_dlp.YoutubeDL({
                        "quiet": True,
                        "no_warnings": True,
                        "format": "best[ext=mp4]/best",
                        "user_agent": random.choice(USER_AGENTS),
                        "force_generic_extractor": False,  # Try to use Instagram extractor
                        "http_headers": {
                            "User-Agent": random.choice(USER_AGENTS),
                            "Accept-Language": "en-US,en;q=0.9",
                            "Referer": "https://www.instagram.com/",
                        }
                    }) as ydl_fallback:
                        # Try to convert threads URL to potential Instagram URL format
                        if "threads.net/@" in url or "threads.com/@" in url:  # Updated to include threads.com
                            # Extract username from threads URL
                            username = url.split("@")[1].split("/")[0]
                            fallback_url = f"https://www.instagram.com/{username}/"
                            logging.info(f"Trying Instagram fallback URL: {fallback_url}")
                            fallback_info = ydl_fallback.extract_info(fallback_url, download=False)
                            if fallback_info and 'entries' in fallback_info and fallback_info['entries']:
                                info = fallback_info['entries'][0]
                                logging.info("Threads fallback to Instagram succeeded")
                except Exception as e:
                    logging.error(f"Threads Instagram fallback extraction failed: {str(e)}")
            
            if not info:
                logging.error(f"No information extracted for {url}")
                return JSONResponse({
                    "success": False,
                    "error": "Could not extract video information"
                }, status_code=400)
            
            # Get video information
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            logging.info(f"Successfully extracted info for: {title}")
            
            # Format duration as HH:MM:SS
            duration_formatted = "Unknown"
            if duration:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
            
            # Process formats with enhanced filtering
            formats = []
            if 'formats' in info:
                logging.info(f"Processing {len(info['formats'])} available formats")
                
                for f in info['formats']:
                    # Skip formats without url
                    if not f.get('url'):
                        continue
                    
                    # Filter out problematic formats for all platforms
                    protocol = f.get('protocol', '').lower()
                    url = f.get('url', '').lower()
                    
                    # Skip streaming formats that often cause issues on servers
                    if ('m3u8' in protocol or 'dash' in protocol or 
                        'm3u8' in url or '.mpd' in url or 
                        'manifest' in url or 'manifest' in protocol):
                        continue
                    
                    # Skip formats with restricted codecs or DRM
                    if f.get('has_drm', False):
                        continue
                        
                    # Platform-specific format filtering
                    if platform == "youtube":
                        # YouTube-specific: Skip formats without audio stream info
                        if f.get('asr') is None:
                            continue
                    elif platform in ["facebook", "instagram", "threads"]:  # Added Threads here
                        # For Facebook/Instagram/Threads: ensure both video and audio are present
                        if (f.get('acodec') == 'none' or not f.get('acodec') or 
                            f.get('vcodec') == 'none' or not f.get('vcodec')):
                            # Skip formats missing either audio or video
                            continue
                    
                    # Create format details
                    format_id = f.get('format_id', '')
                    ext = f.get('ext', '')
                    resolution = f.get('resolution', '')
                    
                    # Construct resolution from dimensions
                    if not resolution and 'height' in f and 'width' in f:
                        if f['height'] and f['width']:
                            resolution = f"{f['width']}x{f['height']}"
                    
                    if not resolution:
                        resolution = f.get('format_note', '')
                    
                    # Calculate filesize
                    filesize = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    filesize_str = f"{round(filesize / (1024 * 1024), 2)} MB" if filesize else "Unknown"
                    
                    # Detect audio-only formats
                    is_audio_only = (f.get('vcodec') == 'none' or 
                                    "audio only" in f.get('format', '').lower())
                    
                    # Detect video-only formats
                    is_video_only = (f.get('acodec') == 'none' or
                                    "video only" in f.get('format', '').lower())
                    
                    # Only add formats with both audio and video for Facebook/Instagram/Threads
                    if platform in ["facebook", "instagram", "threads"] and (is_audio_only or is_video_only):
                        continue
                    
                    formats.append({
                        "format_id": format_id,
                        "format_name": f"{resolution} ({ext})" if resolution else f"{ext.upper()}",
                        "url": f.get('url', ''),
                        "ext": ext,
                        "resolution": resolution,
                        "filesize": filesize_str,
                        "is_audio_only": is_audio_only,
                        "is_video_only": is_video_only,
                        "has_both": not (is_audio_only or is_video_only)
                    })
            
            # Last-resort direct URL fallback for YouTube
            if platform == "youtube" and not formats:
                logging.warning("No formats found through regular extraction, attempting direct URL extraction")
                try:
                    # Try to extract just a direct playable URL without format processing
                    with yt_dlp.YoutubeDL({
                        "quiet": True,
                        "format": "best[ext=mp4]/best",
                        "user_agent": random.choice(USER_AGENTS),
                        "skip_download": True,
                        "geturl": True,  # Just get the URL
                        "geo_bypass": True,
                        "youtube_include_dash_manifest": False,
                    }) as direct_ydl:
                        # This returns just the URL string instead of info dict
                        direct_url = direct_ydl.extract_info(url, download=False, process=False)
                        if direct_url and isinstance(direct_url, str):
                            formats.append({
                                "format_id": "direct",
                                "format_name": "Original (MP4)",
                                "url": direct_url,
                                "ext": "mp4",
                                "resolution": "Original",
                                "filesize": "Unknown",
                                "is_audio_only": False,
                                "is_video_only": False,
                                "has_both": True
                            })
                            logging.info("Added YouTube direct URL as last resort")
                except Exception as e:
                    logging.error(f"YouTube direct URL extraction failed: {str(e)}")
            
            # Special case for Threads direct URL fallback
            if platform == "threads" and not formats:
                logging.warning("No formats found for Threads video, attempting direct URL extraction")
                try:
                    # Try with a simplified extractor specifically for Threads
                    with yt_dlp.YoutubeDL({
                        "quiet": True,
                        "format": "best[ext=mp4]/best",
                        "user_agent": random.choice(USER_AGENTS),
                        "skip_download": True,
                        "geturl": True,
                        "force_generic_extractor": True,  # Use generic extractor for Threads
                    }) as direct_ydl:
                        direct_url = direct_ydl.extract_info(url, download=False, process=False)
                        if direct_url and isinstance(direct_url, str):
                            formats.append({
                                "format_id": "direct",
                                "format_name": "Original (MP4)",
                                "url": direct_url,
                                "ext": "mp4",
                                "resolution": "Original",
                                "filesize": "Unknown",
                                "is_audio_only": False,
                                "is_video_only": False,
                                "has_both": True
                            })
                            logging.info("Added Threads direct URL as last resort")
                except Exception as e:
                    logging.error(f"Threads direct URL extraction failed: {str(e)}")
            
            # Handle platforms with single-format responses
            if not formats and 'url' in info:
                ext = info.get('ext', 'mp4')
                formats.append({
                    "format_id": "direct",
                    "format_name": f"Original ({ext.upper()})",
                    "url": info['url'],
                    "ext": ext,
                    "resolution": "Original",
                    "filesize": "Unknown",
                    "is_audio_only": False
                })
            
            # If still no formats found, try to get direct URL (for any platform)
            if not formats and info.get('webpage_url'):
                logging.warning(f"No viable formats found for {platform}, trying fallback method")
                # Try to extract a direct URL as fallback
                try:
                    fallback_opts = ydl_opts.copy()
                    fallback_opts.update({
                        "format": "best[ext=mp4]/best",  # Simpler format specification
                        "youtube_include_dash_manifest": False,
                    })
                    
                    # Platform-specific fallback settings
                    if platform in ["facebook", "instagram", "threads"]:
                        fallback_opts.update({
                            "format": "best",  # Just get the best available combined format
                            "extract_flat": False,
                        })
                    
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl_fallback:
                        fallback_info = ydl_fallback.extract_info(info['webpage_url'], download=False)
                        if fallback_info and 'url' in fallback_info:
                            formats.append({
                                "format_id": "direct",
                                "format_name": "Original",
                                "url": fallback_info['url'],
                                "ext": fallback_info.get('ext', 'mp4'),
                                "resolution": "Original",
                                "filesize": "Unknown",
                                "is_audio_only": False
                            })
                except Exception as e:
                    logging.error(f"Fallback extraction failed: {str(e)}")
            
            if not formats:
                logging.error(f"No formats extracted for {url}")
                if platform == "youtube":
                    # Try updating yt-dlp as a last resort
                    update_ytdlp()
                return JSONResponse({
                    "success": False,
                    "error": "No download links available for this media"
                }, status_code=400)
            
            logging.info(f"Extracted {len(formats)} valid formats")
            
            # Sort formats: video first, then audio
            video_formats = [f for f in formats if not f['is_audio_only']]
            audio_formats = [f for f in formats if f['is_audio_only']]
            
            # Special handling for Facebook/Instagram/Threads videos with audio issues
            if platform in ["facebook", "instagram", "threads"] and video_formats:
                # When we get video formats for these platforms, check first few for audio issues
                logging.info(f"Checking {platform} formats for audio compatibility")
                
                # Check if we have formats with audio
                has_audio_formats = any('audio' in f.get('format_name', '').lower() 
                                      or 'audio' in f.get('format_id', '').lower() 
                                      for f in formats)
                
                # If no audio formats, adjust the top video format to prioritize audio
                if not has_audio_formats and len(video_formats) > 0:
                    logging.info(f"No explicit audio formats for {platform}, adjusting format priority")
            
            # Sort video formats by resolution (quality)
            def get_resolution_value(format_item):
                if not format_item['resolution'] or format_item['resolution'] == "Original":
                    return 0
                
                # Try to parse resolution like "1280x720"
                parts = format_item['resolution'].split('x')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    return int(parts[1])  # Height is better for quality comparison
                
                # Try to extract resolution from format notes like "720p"
                res_str = format_item['resolution']
                if 'p' in res_str:
                    # Extract numbers before 'p'
                    num_part = res_str.split('p')[0]
                    if num_part.isdigit():
                        return int(num_part)
                
                return 0
            
            video_formats.sort(key=get_resolution_value, reverse=True)
            
            # Combine sorted formats
            sorted_formats = video_formats + audio_formats
            
            # Limit to 10 formats
            sorted_formats = sorted_formats[:10]
            
            return JSONResponse({
                "success": True,
                "title": title,
                "thumbnail": thumbnail,
                "duration": duration_formatted,
                "uploader": uploader,
                "platform": platform,
                "formats": sorted_formats
            })
    
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error processing URL {url}: {error_message}")
        
        # Enhanced error handling
        if "Unsupported URL" in error_message:
            error_message = "This URL is not supported. Please check that you entered a valid video URL."
        elif "Private video" in error_message:
            error_message = "This video is private and cannot be downloaded."
        elif "age-restricted" in error_message.lower():
            error_message = "This content is age-restricted and cannot be downloaded."
        elif "copyright" in error_message.lower():
            error_message = "This content cannot be downloaded due to copyright restrictions."
        elif "sign in" in error_message.lower() or "log in" in error_message.lower():
            error_message = "This content requires login access and cannot be downloaded."
        elif "429" in error_message:
            error_message = "Too many requests. Please try again later."
            # Try updating yt-dlp on rate limit errors
            update_ytdlp()
        
        return JSONResponse({
            "success": False,
            "error": f"Error: {error_message}. Please enter a valid URL from YouTube, Facebook, Instagram, Twitter, or Threads."
        }, status_code=400)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Get port from Fly.io
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
# Serve static assets (CSS, JS, icons) at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve your PWA (index.html, manifest, service worker) at root
app.mount("/", StaticFiles(directory="templates", html=True), name="templates")