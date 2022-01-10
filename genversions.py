#!/usr/bin/env python3

from bs4 import BeautifulSoup
import copy
import glob
import jinja2

tpl_str = """
<div id="cvc5-versions" class="rst-versions shift-up" data-toggle="rst-versions" role="note" aria-label="versions">
    <span class="rst-current-version" data-toggle="rst-current-version">
        <i class="fas fa-tags"></i> Other versions
    </span>
    <div class="rst-other-versions">
        <dl>
{% for version in versions %}
            <dd>
    {%- if curversion == version %}<strong>{% endif -%}
            <a href="%URLROOT%/docs-{{ version }}/">{{ version }}</a>
    {%- if curversion == version %}</strong>{% endif -%}
            </dd>
{% endfor %}
        </dl>
    </div>
</div>
"""
tpl = jinja2.Template(tpl_str)


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
    return ['master', *glob.iglob('cvc5-*')]


def list_files(basepath):
    """List all html files from this base directory."""
    yield from glob.iglob(f'{basepath}/**/*.html', recursive=True)


versions = collect_versions()
for version in versions:
    print(f"Process {version}...")
    newvers = tpl.render(curversion=version, versions=versions)
    newvers = BeautifulSoup(newvers, 'html.parser')

    for file in list_files(f'docs-{version}'):
        put_versions_in_file(file, copy.copy(newvers))