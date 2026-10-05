#!/usr/bin/env python3
"""Builds two files from src/app.html:
  dist/pocket-reader.html  - one self-contained file that works offline (open it in any phone browser)
  dist/artifact.html       - same page loading mammoth from a CDN (used for the hosted link)
  www/index.html           - the offline file, used as the Capacitor app's web content
"""
import pathlib
root = pathlib.Path(__file__).parent
src = (root / "src/app.html").read_text()
mammoth = (root / "vendor/mammoth.browser.min.js").read_text()
(root / "dist").mkdir(exist_ok=True)
import re
offline_src = re.sub(r'<link rel="(preconnect|stylesheet)" href="https://fonts[^>]*>\n', "", src)
head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="theme-color" content="#1f5fae">\n<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Pocket Reader">\n</head>\n<body>\n')
# Standalone/native pages have no host padding, so the toolbar itself clears the notch/status bar.
native_css = ('<style>:root{padding:0}.bar{top:0;padding-top:max(env(safe-area-inset-top,0px),var(--safe-area-inset-top,0px))}'
              'main{padding-bottom:calc(48px + max(env(safe-area-inset-bottom,0px),var(--safe-area-inset-bottom,0px)))}</style>\n')
import base64
def face(family, file, weight):
    b64 = base64.b64encode((root / "node_modules/@fontsource-variable" / file).read_bytes()).decode()
    return f"@font-face{{font-family:'{family}';font-style:normal;font-display:swap;font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
# Bundle the fonts so the app looks the same offline.
fonts = ("<style>" + face("Nunito", "nunito/files/nunito-latin-wght-normal.woff2", "200 1000")
         + face("Literata", "literata/files/literata-latin-wght-normal.woff2", "200 900") + "</style>\n")
inline = "<script>" + mammoth.replace("</script", "<\\/script") + "</script>"
(root / "dist/pocket-reader.html").write_text(head + offline_src.replace("<!--MAMMOTH-->", fonts + native_css + inline) + "\n</body>\n</html>\n")
cdn = '<script src="https://cdn.jsdelivr.net/npm/mammoth@1.13.0/mammoth.browser.min.js"></script>'
(root / "dist/artifact.html").write_text(src.replace("<!--MAMMOTH-->", cdn))
(root / "www").mkdir(exist_ok=True)
(root / "www/index.html").write_text((root / "dist/pocket-reader.html").read_text())
print("built", [p.name for p in (root / "dist").iterdir()])
