from http.server import BaseHTTPRequestHandler
import urllib.parse
import tempfile
import subprocess
import os
import zipfile
import shutil


class handler(BaseHTTPRequestHandler):

    def send_text(self, code, text):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode())

    def do_GET(self):
        try:
            query = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )

            url = query.get("url", [None])[0]

            if not url:
                self.send_text(400, "Missing URL")
                return

            with tempfile.TemporaryDirectory() as tmp:

                # Run hdporncomics downloader
                result = subprocess.run(
                    [
                        "hdporncomics",
                        "--directory",
                        tmp,
                        url
                    ],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    self.send_text(
                        500,
                        result.stderr or "Download failed"
                    )
                    return


                zip_path = "/tmp/comic.zip"

                with zipfile.ZipFile(
                    zip_path,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as zipf:

                    for root, dirs, files in os.walk(tmp):
                        for file in files:
                            path = os.path.join(root, file)

                            zipf.write(
                                path,
                                os.path.relpath(path, tmp)
                            )


                with open(zip_path, "rb") as f:
                    data = f.read()


            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/zip"
            )
            self.send_header(
                "Content-Disposition",
                'attachment; filename="comic.zip"'
            )
            self.send_header(
                "Content-Length",
                str(len(data))
            )
            self.end_headers()

            self.wfile.write(data)


        except Exception as e:
            self.send_text(
                500,
                "Server error: " + str(e)
            )
