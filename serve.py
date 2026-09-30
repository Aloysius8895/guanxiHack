"""Serve the captured site locally, including clean URLs and video byte ranges."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import json
import io
import re

ROOT = Path(__file__).resolve().parent
TYPES = {}
if (ROOT/'manifest.json').exists():
    TYPES = {x['path']: x['content_type'] for x in json.loads((ROOT/'manifest.json').read_text('utf-8')).values() if x.get('ok')}


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        target = Path(super().translate_path(path))
        if target.is_dir() and (target/'index.html').is_file():
            return str(target/'index.html')
        if target.is_dir() and (target/'index.json').is_file():
            return str(target/'index.json')
        return str(target)

    def guess_type(self, path):
        try:
            rel = Path(path).relative_to(ROOT/'site').as_posix()
            if rel in TYPES: return TYPES[rel]
        except ValueError: pass
        return super().guess_type(path)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def send_head(self):
        self._byte_range = None
        path = Path(self.translate_path(self.path))
        header = self.headers.get('Range')
        if path.is_file() and path.is_relative_to(ROOT/'site'/'_assets'/'tiles.openfreemap.org') and 'json' in self.guess_type(str(path)):
            # MapLibre requires absolute sprite/tile URLs, even for local styles.
            origin = f'http://127.0.0.1:{self.server.server_port}'
            data = path.read_bytes().replace(b'"/_assets/', ('"'+origin+'/_assets/').encode())
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            return io.BytesIO(data)
        if header and path.is_file():
            size = path.stat().st_size
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
            if match and (match[1] or match[2]):
                start = int(match[1]) if match[1] else max(0, size-int(match[2]))
                end = min(int(match[2]), size-1) if match[1] and match[2] else size-1
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{size}')
                    self.end_headers()
                    return None
                f = path.open('rb')
                f.seek(start)
                self._byte_range = end-start+1
                self.send_response(206)
                self.send_header('Content-Type', self.guess_type(str(path)))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length', str(self._byte_range))
                self.end_headers()
                return f
        return super().send_head()

    def copyfile(self, source, outputfile):
        try:
            if self._byte_range is None:
                return super().copyfile(source, outputfile)
            remaining = self._byte_range
            while remaining:
                chunk = source.read(min(65536, remaining))
                if not chunk: break
                outputfile.write(chunk)
                remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError): pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8002)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(ROOT/'site')))
    print(f'CoMinVi local mirror: http://127.0.0.1:{args.port}', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
