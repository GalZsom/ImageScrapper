from flask import Flask, request, send_file, Response
import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup

app = Flask(__name__)

def crawl_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    images = []
    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        if "http" not in img_url:
            # make the URL absolute if it's relative
            img_url = f"{url}{img_url}"
        try:
            images.append(img_url)
        except:
            continue
    return images

@app.route("/api/images", methods=['GET'])
def get_images():
    url = request.args.get('url')
    images = crawl_images(url)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, url in enumerate(images):
            print(f"Downloading image {i}: {url}")
            response = requests.get(url)
            with open(f"image_{i}.jpg", "wb") as f:
                f.write(response.content)
            zf.writestr(f"image_{i}.jpg", response.content)
    zip_buffer.seek(0)

    
    response = Response(zip_buffer.getvalue(), content_type='application/zip')
    response.headers["Content-Disposition"] = f"attachment; filename={'images.zip'}"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Content-Type"] = "application/zip"
    return response

if __name__ == "__main__":
    app.run()
