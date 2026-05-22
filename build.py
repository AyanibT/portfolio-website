#!/usr/bin/env python3
import os, shutil, datetime, yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROOT, "templates")
STATIC = os.path.join(ROOT, "static")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def clean_out():
    if os.path.exists(OUT):
        # preserve CNAME if it exists
        cname = None
        cname_path = os.path.join(OUT, "CNAME")
        if os.path.exists(cname_path):
            with open(cname_path, "r", encoding="utf-8") as f:
                cname = f.read()
        shutil.rmtree(OUT)
        ensure_dir(OUT)
        if cname:
            with open(cname_path, "w", encoding="utf-8") as f:
                f.write(cname)
    else:
        ensure_dir(OUT)

def copy_static():
    dest = os.path.join(OUT, "assets")
    shutil.copytree(STATIC, dest, dirs_exist_ok=True)

def main():
    config = load_yaml(os.path.join(ROOT, "config.yaml"))
    projects = load_yaml(os.path.join(DATA, "projects.yaml"))
    publications = load_yaml(os.path.join(DATA, "publications.yaml"))

    base_path = (config.get("base_path") or "").strip()
    if base_path == "/":
        base_path = ""

    def url(path):
        # build site-relative URLs honoring base_path
        p = "/" + path.lstrip("/")
        bp = base_path.rstrip("/")
        return (bp + p) if bp else p

    def full_url(path):
        domain = (config.get("domain") or "").strip()
        if not domain:
            return url(path)
        scheme = "https://" if not domain.startswith(("http://", "https://")) else ""
        return f"{scheme}{domain}{url(path)}"

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"])
    )
    env.globals["url"] = url
    env.globals["full_url"] = full_url
    env.globals["now"] = datetime.date.today

    clean_out()
    copy_static()

    nav = [
        {"label": "Home", "href": url("/")},
        {"label": "Projects", "href": url("/projects/")},
        {"label": "Publications", "href": url("/publications/")},
        {"label": "About", "href": url("/about/")},
        {"label": "Contact", "href": url("/contact/")},
    ]

    pages = [
        {"tpl": "index.html", "out": "index.html", "url": "/"},
        {"tpl": "projects.html", "out": "projects/index.html", "url": "/projects/"},
        {"tpl": "publications.html", "out": "publications/index.html", "url": "/publications/"},
        {"tpl": "about.html", "out": "about/index.html", "url": "/about/"},
        {"tpl": "contact.html", "out": "contact/index.html", "url": "/contact/"},
        {"tpl": "404.html", "out": "404.html", "url": "/404.html"},
    ]

    ctx_common = {
        "site": config,
        "nav": nav,
        "projects": projects,
        "publications": publications,
    }

    for p in pages:
        tpl = env.get_template(p["tpl"])
        out_path = os.path.join(OUT, p["out"])
        ensure_dir(os.path.dirname(out_path))
        html = tpl.render(page_url=p["url"], **ctx_common)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

    # robots.txt
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: " + full_url("/sitemap.xml") + "\n")

    # .nojekyll (so GH Pages doesn’t process with Jekyll)
    with open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    # CNAME if domain is set
    if config.get("domain"):
        with open(os.path.join(OUT, "CNAME"), "w", encoding="utf-8") as f:
            f.write(config["domain"].strip() + "\n")

    # sitemap
    tpl = env.get_template("sitemap.xml.j2")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(tpl.render(pages=pages, full_url=full_url))

if __name__ == "__main__":
    main()