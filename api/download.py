from http.server import BaseHTTPRequestHandler
import subprocess
import tempfile
import os
import zipfile
import urllib.parse

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query
        )

        url = query.get("url",[None])[0]

        if not url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing URL")
            return

        with tempfile.TemporaryDirectory() as tmp:

            subprocess.run([
                "hdporncomics",
                "--directory",
                tmp,
                url
            ], check=True)

            zip_path = tmp + ".zip"

            with zipfile.ZipFile(zip_path,"w") as z:
                for root,dirs,files in os.walk(tmp):
                    for file in files:
                        path=os.path.join(root,file)
                        z.write(
                            path,
                            os.path.relpath(path,tmp)
                        )

            with open(zip_path,"rb") as f:
                data=f.read()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/zip"
        )
        self.send_header(
            "Content-Disposition",
            "attachment; filename=comic.zip"
        )
        self.end_headers()

        self.wfile.write(data)
