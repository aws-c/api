from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_direct_download_link(mediafire_file_id: str) -> str:
    """Get the direct download link from a MediaFire file ID."""
    mediafire_file_url = f"https://www.mediafire.com/file/{mediafire_file_id}/file"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    session = requests.Session()
    
    try:
        response = session.get(mediafire_file_url, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP errors

        soup = BeautifulSoup(response.text, "html.parser")
        download_link = soup.find("a", class_="input popsok")

        if download_link and 'href' in download_link.attrs:
            return download_link['href']
        else:
            raise Exception("Could not find the direct download link.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

@app.route("/<mediafire_file_id>", methods=["GET"])
def get_download_link(mediafire_file_id):
    try:
        direct_link = get_direct_download_link(mediafire_file_id)
        return jsonify({"direct_link": direct_link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
