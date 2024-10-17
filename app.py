from flask import Flask, jsonify
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import aiocache

app = Flask(__name__)

# Set up cache for faster access to recently fetched links (optional)
cache = aiocache.SimpleMemoryCache()

async def get_direct_download_link(mediafire_file_id: str) -> str:
    """Get the direct download link from a MediaFire file ID asynchronously."""
    cached_link = await cache.get(mediafire_file_id)
    
    if cached_link:
        return cached_link

    mediafire_file_url = f"https://www.mediafire.com/file/{mediafire_file_id}/file"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(mediafire_file_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    download_link = soup.find("a", class_="input popsok")

                    if download_link and 'href' in download_link.attrs:
                        direct_link = download_link['href']
                        # Cache the result to reduce load on MediaFire
                        await cache.set(mediafire_file_id, direct_link, ttl=3600)  # Cache for 1 hour
                        return direct_link
                    else:
                        raise Exception("Could not find the direct download link.")
                else:
                    raise Exception(f"Error: Received HTTP {response.status}")
        except aiohttp.ClientError as e:
            raise Exception(f"Request failed: {str(e)}")

@app.route("/<mediafire_file_id>", methods=["GET"])
async def get_download_link(mediafire_file_id):
    try:
        direct_link = await get_direct_download_link(mediafire_file_id)
        return jsonify({"direct_link": direct_link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # Production server should be run with an ASGI server like uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=963)
