import os
import yt_dlp
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Directories
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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

@app.post("/generate-link")
async def generate_link(url: str = Form(...)):
    """Generate download links for the given URL (YouTube, Facebook, Instagram, Twitter)."""
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
        
        # Configure yt-dlp options based on the platform
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,  # Don't download, just get info
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        }

        # Platform-specific configurations
        if platform == "youtube":
            ydl_opts.update({
                "format": "(bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best)",
                "ignore_no_formats_error": True,
            })
        elif platform == "facebook":
            ydl_opts.update({
                "extract_flat": False,
                "socket_timeout": 30,
                "no_playlist": True,
            })
        elif platform == "instagram":
            ydl_opts.update({
                "extract_flat": True,
                "socket_timeout": 30,
                "no_playlist": True,
            })
        elif platform == "twitter":
            ydl_opts.update({
                "extract_flat": False,
                "socket_timeout": 30,
            })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle playlist or multi-video content
            if 'entries' in info and info['entries']:
                info = info['entries'][0]
            
            # Get video information
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            # Format duration as HH:MM:SS
            duration_formatted = "Unknown"
            if duration:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}" if hours else f"{minutes:02}:{seconds:02}"
            
            # Process formats with HLS/DASH filtering
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    # Skip HLS/DASH formats for YouTube
                    if platform == "youtube":
                        protocol = f.get('protocol', '')
                        url = f.get('url', '')
                        if any(x in protocol.lower() for x in ['m3u8', 'dash']) or 'm3u8' in url.lower():
                            continue
                    
                    # Skip formats without url
                    if not f.get('url'):
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
                    is_audio_only = f.get('vcodec') == 'none' or "audio only" in f.get('format', '').lower()
                    
                    formats.append({
                        "format_id": format_id,
                        "format_name": f"{resolution} ({ext})" if resolution else f"{ext.upper()}",
                        "url": f.get('url', ''),
                        "ext": ext,
                        "resolution": resolution,
                        "filesize": filesize_str,
                        "is_audio_only": is_audio_only
                    })
            
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
            
            # Sort formats: video first, then audio
            video_formats = [f for f in formats if not f['is_audio_only']]
            audio_formats = [f for f in formats if f['is_audio_only']]
            
            # Sort by resolution (descending)
            video_formats.sort(key=lambda x: (
                int(x['resolution'].split('x')[0]) if x['resolution'] and x['resolution'].isdigit() else 0,
            ), reverse=True)
            
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
        # Enhanced error handling
        if "Unsupported URL" in error_message:
            error_message = "This URL is not supported. Please check that you entered a valid video URL."
        elif "Private video" in error_message:
            error_message = "This video is private and cannot be downloaded."
        elif "age-restricted" in error_message.lower():
            error_message = "This content is age-restricted and cannot be downloaded."
        elif "copyright" in error_message.lower():
            error_message = "This content cannot be downloaded due to copyright restrictions."
        
        return JSONResponse({
            "success": False,
            "error": error_message
        }, status_code=400)