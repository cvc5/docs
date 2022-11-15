#!/usr/bin/env python3

from bs4 import BeautifulSoup
from distutils.version import StrictVersion
import copy
import glob
import jinja2
import re

tpl_str = """
<div id="cvc5-versions" class="rst-versions shift-up" data-toggle="rst-versions" role="note" aria-label="versions">
    <span class="rst-current-version" data-toggle="rst-current-version">
        <i class="fas fa-tags"></i> Other versions
    </span>
    <div class="rst-other-versions">
        <dl>
{% for version in versions %}
            <dd>
    {%- if version == curversion %}<strong>{% endif -%}
    {%- if version == "cvc5-main" %}
        <a href="https://cvc5.github.io/docs-ci/docs-main/">cvc5-main</a>
    {%- else -%}
        <a href="%URLROOT%/{{ version }}/">{{ version }}</a>
    {% endif -%}
    {%- if version == curversion %}</strong>{% endif -%}
            </dd>
{% endfor %}
        </dl>
    </div>
</div>
"""
tpl = jinja2.Template(tpl_str)

tpl_redirect_str = """
<!DOCTYPE html>
<meta charset="utf-8">
<title>Redirect to latest release</title>
<meta http-equiv="refresh" content="0; URL={{ release }}/">
<link rel="canonical" href="{{ release }}/">
"""
tpl_redirect = jinja2.Template(tpl_redirect_str)


def put_versions_in_file(filename, newblock):
    """Insert or replace the `cvc5-versions` block with the new block."""
    doc = BeautifulSoup(open(filename).read(), 'lxml')

    # identify nav bar where the `cvc5-version` block shall go
    nav = doc.find('nav', class_='wy-nav-side')
    if not nav:
        return

    # find relative path to root dir
    urlroot = doc.find('script', id='documentation_options')
    if not urlroot:
        return
    urlroot = f'{urlroot["data-url_root"]}..'
    for a in newblock.find_all('a'):
        a['href'] = a['href'].replace('%URLROOT%', urlroot)

    cur = nav.find(id='cvc5-versions')
    if cur:
        cur.replace_with(newblock)
    else:
        nav.append(newblock)
    open(filename, 'w').write(doc.prettify())


def collect_versions():
    """Collect all paths / versions."""
    return glob.glob('cvc5-*.*.*')


def list_files(basepath):
    """List all html files from this base directory."""
    yield from glob.iglob(f'{basepath}/**/*.html', recursive=True)


release_versions = collect_versions()
# map "cvc5-x.y.z" to [x, y, z]
release_versions.sort(key=lambda v: list(
    map(int,
        re.match('cvc5-([0-9]+).([0-9]+).([0-9]+)', v).groups())),
                      reverse=True)
versions = ["cvc5-main"] + release_versions
for version in versions:
    print(f"Process {version}...")
    newvers = tpl.render(curversion=version, versions=versions)
    newvers = BeautifulSoup(newvers, 'html.parser')

    for file in list_files(version):
        put_versions_in_file(file, copy.copy(newvers))

latest_version = release_versions[0]
newindex = tpl_redirect.render(release=latest_version)
open("index.html", 'w').write(newindex)
