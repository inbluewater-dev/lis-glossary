#!/usr/bin/env python3
"""문헌정보학 용어사전 — 사이트 생성기.

정본은 data/terms.yaml 과 data/sources.yaml 두 개뿐이다.
이 스크립트가 docs/ 아래 모든 파일(HTML·JSON·Markdown·llms.txt·sitemap)을 새로 만든다.
docs/ 안의 파일은 손으로 고치지 않는다 — 고치면 다음 빌드에서 덮인다.

    python3 build.py
"""
import html
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"

BASE_URL = "https://inbluewater-dev.github.io/lis-glossary/"
TITLE = "문헌정보학 용어사전"
TITLE_EN = "Korean Glossary of Library and Information Science"
VERSION = "1.6"
# 갱신일은 빌드할 때 자동으로 오늘 날짜(한국 시간)가 들어간다.
# 판(VERSION)은 용어를 크게 묶어 더하거나 체계를 바꿀 때만 손으로 올린다 — 작은 수정·추가는 판을 그대로 둔다.
import datetime as _dt
from zoneinfo import ZoneInfo as _ZI
UPDATED = _dt.datetime.now(_ZI("Asia/Seoul")).date().isoformat()
# 용어 추가 요청 설문지(구글 설문지 「미리 채워진 링크」). __TERM__ 자리에 검색어가 들어간다.
# 비어 있으면 요청 버튼을 보이지 않는다.
REQUEST_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfghdBqrsx0y2jgNalFOiJ4OHsbCj_-v5tXqyRdIrBE1ugS1Q/viewform?usp=pp_url&entry.1852569616=__TERM__"
LICENSE_NAME = "CC BY 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/deed.ko"
LICENSE_URL_EN = "https://creativecommons.org/licenses/by/4.0/"
DESCRIPTION = (
    "도서관과 정보에 관한 핵심 용어 {N}개를 누구나 이해할 수 있는 말로 풀어 쓴 문헌정보학 용어사전입니다. "
    "모든 정의는 새로 썼으며, 각 용어마다 영어 표제어·관련어·근거 자료를 함께 적었습니다."
)

esc = html.escape


def load():
    data = yaml.safe_load((ROOT / "data/terms.yaml").read_text(encoding="utf-8"))
    sources = yaml.safe_load((ROOT / "data/sources.yaml").read_text(encoding="utf-8"))
    cats = data["categories"]
    terms = data["terms"]
    for t in terms:
        t["definition"] = " ".join(t["definition"].split())
        t.setdefault("aka", [])
        t.setdefault("related", [])
        t.setdefault("sources", [])
        t.setdefault("example", "")
    cname = {c["id"]: c["name"] for c in cats}
    for t in terms:
        t["_catname"] = cname[t["category"]]
    return cats, terms, {s["id"]: s for s in sources}, sources


def term_url(t):
    return f"{BASE_URL}terms/{t['id']}/"


# ---------- 공통 조각 ----------

CSS = r"""
:root{
  --bg:#fbfaf7;--surface:#ffffff;--ink:#1d1b18;--muted:#6b665d;--line:#e6e1d6;
  --accent:#1f5f5b;--accent-soft:#e3efed;--mark:#fff2b3;
  --radius:14px;--maxw:860px;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#141413;--surface:#1c1b19;--ink:#ece8df;--muted:#a39d91;--line:#2f2d29;
        --accent:#7cc4bb;--accent-soft:#1f302e;--mark:#5a4a12;}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;
  line-height:1.75;font-size:17px;word-break:keep-all;overflow-wrap:anywhere}
a{color:var(--accent);text-underline-offset:3px}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 16px}
header.site{border-bottom:1px solid var(--line);background:var(--surface)}
header.site .wrap{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding-top:14px;padding-bottom:14px;flex-wrap:wrap}
header.site a.brand{font-weight:700;color:var(--ink);text-decoration:none;font-size:18px}
header.site nav a{margin-left:14px;font-size:15px;color:var(--muted)}
.hero{padding:44px 0 20px}
.hero h1{font-size:clamp(28px,6vw,40px);line-height:1.25;margin:0 0 6px;letter-spacing:-.02em}
.hero .en{color:var(--muted);margin:0 0 18px;font-size:15px}
.hero p.lead{margin:0;color:var(--ink);max-width:640px}
.meta{color:var(--muted);font-size:14px;margin-top:14px}
.tools{position:sticky;top:0;z-index:5;background:var(--bg);padding:14px 0 10px;border-bottom:1px solid var(--line)}
.search{width:100%;font:inherit;padding:12px 16px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink)}
.search:focus{outline:2px solid var(--accent);outline-offset:1px}
.chips{display:flex;gap:8px;overflow-x:auto;padding:10px 0 2px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;font-size:14px;padding:5px 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--muted);text-decoration:none;white-space:nowrap}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.count{color:var(--muted);font-size:14px;margin:8px 0 0}
section.cat{padding-top:26px}
section.cat h2{font-size:21px;margin:0 0 12px;scroll-margin-top:140px}
section.cat h2 small{color:var(--muted);font-weight:400;font-size:14px;margin-left:6px}
article.term{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin:0 0 12px;scroll-margin-top:140px}
article.term:target{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
article.term h3{margin:0;font-size:19px;line-height:1.4}
article.term h3 a{color:var(--ink);text-decoration:none}
article.term h3 a:hover{text-decoration:underline}
.en-term{color:var(--muted);font-size:14.5px;margin:2px 0 0}
.aka{color:var(--muted);font-size:14px;margin:2px 0 0}
.def{margin:10px 0 0}
.example{margin:10px 0 0;padding:10px 14px;background:var(--accent-soft);border-radius:10px;font-size:15.5px}
.example b{color:var(--accent);font-weight:600;margin-right:4px}
dl.extra{margin:12px 0 0;font-size:14.5px;display:grid;grid-template-columns:auto 1fr;gap:4px 12px}
dl.extra dt{color:var(--muted)}
dl.extra dd{margin:0}
.rel a{margin-right:10px;white-space:nowrap}
.src{color:var(--muted)}
mark{background:var(--mark);color:inherit;border-radius:3px}
.empty{display:none;padding:30px 0;color:var(--muted)}
.empty p{margin:0 0 8px}
.catlabel{display:none;margin:0 0 4px;font-size:13px;color:var(--accent)}
#results{padding-top:18px}
#results .catlabel{display:block}
a.req{display:inline-block;padding:8px 16px;border-radius:999px;background:var(--accent);color:var(--bg);text-decoration:none;font-weight:600}
.index-az{columns:3 180px;column-gap:24px;font-size:15px}
.index-az a{display:block;color:var(--ink);text-decoration:none;padding:2px 0}
.index-az a:hover{color:var(--accent)}
.box{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px}
.box h2{font-size:20px;margin-top:0}
footer{margin:48px 0 0;padding:24px 0 48px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
footer a{color:var(--muted)}
.crumb{font-size:14px;color:var(--muted);margin:24px 0 8px}
.single h1{font-size:clamp(26px,6vw,34px);margin:0;line-height:1.3}
.pager{display:flex;justify-content:space-between;gap:12px;margin:20px 0 0;font-size:15px}
.machine{font-size:14px;color:var(--muted)}
code{font-size:.92em;background:var(--accent-soft);padding:1px 5px;border-radius:5px}
@media (max-width:520px){body{font-size:16px}article.term{padding:16px}dl.extra{grid-template-columns:1fr}dl.extra dt{margin-top:6px}}
"""

FONT = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'


def head(title, desc, canonical, jsonld, prefix=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="license" href="{LICENSE_URL_EN}">
<link rel="alternate" type="application/json" href="{BASE_URL}glossary.json" title="용어사전 전체 (JSON)">
<link rel="alternate" type="text/markdown" href="{BASE_URL}llms-full.txt" title="용어사전 전체 (Markdown)">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="ko_KR">
{FONT}
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="{prefix}./">{TITLE}</a>
<nav><a href="{prefix}./#index-az">가나다순</a><a href="{prefix}./#about">이 사전에 대해</a><a href="{prefix}./#for-ai">AI·개발자</a></nav>
</div></header>
"""


def footer():
    return f"""<footer><div class="wrap">
<p>{TITLE} · 판 {VERSION} · 마지막 갱신 {UPDATED}<br>
AI(Claude)의 도움으로 작성하고 검수했습니다. 본문은 <a href="{LICENSE_URL}" rel="license">크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스(CC BY 4.0)</a>로 공개합니다. 출처를 밝히면 누구나 자유롭게 쓸 수 있습니다.<br>
기계용 데이터: <a href="{BASE_URL}glossary.json">glossary.json</a> · <a href="{BASE_URL}llms.txt">llms.txt</a> · <a href="{BASE_URL}llms-full.txt">llms-full.txt</a></p>
</div></footer>
</body>
</html>
"""


def defined_term_ld(t, cat_name):
    d = {
        "@type": "DefinedTerm",
        "@id": term_url(t),
        "name": t["term"],
        "alternateName": [t["en"]] + t["aka"],
        "description": t["definition"],
        "url": term_url(t),
        "termCode": t["id"],
        "inDefinedTermSet": BASE_URL,
        "inLanguage": "ko",
    }
    return d


def term_set_ld(terms, cats_by_id):
    return {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "@id": BASE_URL,
        "name": TITLE,
        "alternateName": TITLE_EN,
        "description": DESCRIPTION,
        "url": BASE_URL,
        "inLanguage": "ko",
        "license": LICENSE_URL_EN,
        "version": VERSION,
        "dateModified": UPDATED,
        "hasDefinedTerm": [defined_term_ld(t, cats_by_id[t["category"]]) for t in terms],
    }


def sources_text(t, src):
    names = []
    for sid in t["sources"]:
        s = src[sid]
        if s.get("url"):
            names.append(f'<a href="{esc(s["url"])}" rel="noopener">{esc(s["name"])}</a>')
        else:
            names.append(esc(s["name"]))
    return " · ".join(names) if names else "새로 쓴 설명(특정 표준에 기대지 않음)"


def term_card(t, by_id, src, link_prefix, heading="h3", anchor=True):
    rel = "".join(
        f'<a href="{link_prefix}#{r}">{esc(by_id[r]["term"])}</a>' for r in t["related"]
    )
    aka = f'<p class="aka">다른 이름: {esc(", ".join(t["aka"]))}</p>' if t["aka"] else ""
    ex = f'<p class="example"><b>예</b>{esc(t["example"])}</p>' if t["example"] else ""
    idattr = f' id="{t["id"]}"' if anchor else ""
    search = esc(" ".join([t["term"], t["en"], *t["aka"], t["definition"]]).lower())
    names = esc("|".join(x.lower() for x in [t["term"], t["en"], *t["aka"]]))
    return f"""<article class="term"{idattr} data-search="{search}" data-term="{esc(t['term'].lower())}" data-names="{names}">
<p class="catlabel">{esc(t.get('_catname',''))}</p>
<{heading}><a href="terms/{t['id']}/" class="t">{esc(t['term'])}</a></{heading}>
<p class="en-term" lang="en">{esc(t['en'])}</p>
{aka}
<p class="def">{esc(t['definition'])}</p>
{ex}
<dl class="extra">
<dt>관련어</dt><dd class="rel">{rel or '—'}</dd>
<dt>근거</dt><dd class="src">{sources_text(t, src)}</dd>
</dl>
</article>"""


# ---------- 페이지 ----------

def build_index(cats, terms, by_id, src, sources):
    cats_by_id = {c["id"]: c for c in cats}
    chips = "".join(
        f'<a class="chip" href="#cat-{c["id"]}">{esc(c["name"])}</a>' for c in cats
    )
    body = []
    for c in cats:
        ts = [t for t in terms if t["category"] == c["id"]]
        cards = "\n".join(term_card(t, by_id, src, "") for t in ts)
        body.append(
            f'<section class="cat" data-cat="{c["id"]}"><h2 id="cat-{c["id"]}">{esc(c["name"])}<small>{len(ts)}개</small></h2>\n{cards}\n</section>'
        )
    az = "".join(
        f'<a href="#{t["id"]}">{esc(t["term"])}</a>'
        for t in sorted(terms, key=lambda x: x["term"])
    )
    src_list = "".join(
        f'<li>{"<a href=" + chr(34) + esc(s["url"]) + chr(34) + ">" + esc(s["name"]) + "</a>" if s.get("url") else esc(s["name"])}</li>'
        for s in sources
    )
    if REQUEST_FORM:
        request_box = (f'<p><a class="req" id="req" data-form="{esc(REQUEST_FORM)}" href="{esc(REQUEST_FORM.replace("__TERM__", ""))}" '
                       'target="_blank" rel="noopener">이 용어 추가 요청하기 →</a></p>'
                       '<p class="machine">요청은 사전 관리자에게 전달되어 검토 뒤 반영 여부가 정해집니다. 이름·연락처 같은 개인정보는 적지 마세요.</p>')
        request_about = (f'<p><b>찾는 용어가 없나요?</b> <a href="{esc(REQUEST_FORM.replace("__TERM__", ""))}" target="_blank" rel="noopener">용어 추가 요청</a>을 남겨 주세요. '
                         '모인 요청은 정기적으로 검토하며, 정의를 새로 쓰고 사실관계를 확인한 뒤에만 사전에 싣습니다.</p>\n')
    else:
        request_box = request_about = ""
    page = head(
        f"{TITLE} — {TITLE_EN}", DESCRIPTION, BASE_URL, term_set_ld(terms, cats_by_id)
    )
    page += f"""<main class="wrap">
<section class="hero">
<h1>{TITLE}</h1>
<p class="en" lang="en">{TITLE_EN}</p>
<p class="lead">도서관과 정보를 다루는 학문, 문헌정보학의 핵심 용어 {len(terms)}개를 누구나 이해할 수 있는 말로 풀었습니다. 용어마다 영어 표제어, 관련어, 근거 자료를 함께 적었습니다.</p>
<p class="meta">판 {VERSION} · {UPDATED} · <a href="{LICENSE_URL}">CC BY 4.0</a></p>
</section>
<div class="tools">
<input class="search" id="q" type="search" placeholder="용어·영어·설명으로 찾기 (예: 분류, ISBN, recall)" aria-label="용어 찾기" autocomplete="off">
<nav class="chips" aria-label="분야">{chips}</nav>
<p class="count" id="count" aria-live="polite">{len(terms)}개 용어</p>
</div>
{chr(10).join(body)}
<section id="results" hidden></section>
<div class="empty" id="empty"><p>찾는 용어가 없습니다. 다른 낱말로 찾아보세요.</p>{request_box}</div>

<section class="cat"><h2 id="index-az">가나다순 찾아보기</h2>
<div class="index-az">{az}</div></section>

<section class="cat" id="about"><div class="box">
<h2>이 사전에 대해</h2>
<p><b>누구를 위한 사전인가요?</b> 도서관을 이용하는 누구나, 그리고 문헌정보학에 처음 관심을 가진 사람을 위해 썼습니다. 전문 용어는 되도록 쉬운 말로 풀고, 필요한 곳에는 예를 달았습니다.</p>
<p><b>정의는 어디서 왔나요?</b> 모든 정의는 이 사전을 위해 새로 쓴 문장입니다. 기존 사전의 문장을 옮겨 오지 않았습니다. 대신 각 용어 아래 「근거」에 정의를 쓸 때 기댄 국제 표준·법령·기관 자료를 적어 두었으니, 더 정확한 내용은 그 자료에서 확인할 수 있습니다.</p>
<p><b>AI가 썼나요?</b> 네, 밝혀 둡니다. 이 사전의 정의는 AI(Anthropic의 Claude)의 도움을 받아 작성했으며, 별도의 검수 과정에서 연도·법령·기관명 등 사실관계를 근거 자료와 대조했습니다. 그래도 틀린 곳이 있을 수 있으니, 중요한 내용은 각 용어의 「근거」 자료에서 한 번 더 확인해 주세요.</p>
{request_about}<p><b>써도 되나요?</b> 네. <a href="{LICENSE_URL}">CC BY 4.0</a>으로 공개합니다. 수업 자료, 블로그, 앱, AI 학습·검색 등 어디에 쓰든 「{TITLE} ({BASE_URL})」처럼 출처만 밝혀 주세요.</p>
<details><summary>근거 자료 전체 목록 ({len(sources)}건)</summary><ul>{src_list}</ul></details>
</div></section>

<section class="cat" id="for-ai"><div class="box">
<h2>AI·개발자를 위한 안내</h2>
<p>같은 내용을 기계가 읽기 쉬운 형태로도 제공합니다. 모두 같은 정본(<code>data/terms.yaml</code>)에서 만들어지므로 내용이 서로 같습니다.</p>
<ul>
<li><a href="{BASE_URL}llms.txt">llms.txt</a> — AI용 사이트 안내 (<a href="https://llmstxt.org/">llms.txt 형식</a>)</li>
<li><a href="{BASE_URL}llms-full.txt">llms-full.txt</a> — 용어 {len(terms)}개 전체를 한 파일에 담은 Markdown</li>
<li><a href="{BASE_URL}glossary.json">glossary.json</a> — 구조화된 JSON (용어·영어·다른 이름·분야·정의·예·관련어·근거)</li>
<li><code>terms/&lt;id&gt;/</code> — 용어마다 고유 주소를 가진 페이지, <code>terms/&lt;id&gt;.md</code> — 같은 내용의 Markdown</li>
<li>모든 페이지에 schema.org <code>DefinedTermSet</code> / <code>DefinedTerm</code> JSON-LD가 들어 있습니다.</li>
</ul>
<p class="machine">인용 예: 「문헌정보학 용어사전, ‘재현율’, {BASE_URL}terms/recall/ (CC BY 4.0)」</p>
</div></section>
</main>
<script>
(function(){{
  var q=document.getElementById('q'),cards=[].slice.call(document.querySelectorAll('article.term')),
      secs=[].slice.call(document.querySelectorAll('section.cat[data-cat]')),
      count=document.getElementById('count'),empty=document.getElementById('empty'),total=cards.length;
  var res=document.getElementById('results'),home=cards.map(function(c){{return [c,c.parentNode,c.nextSibling];}});
  function restore(){{for(var i=home.length-1;i>=0;i--){{home[i][1].insertBefore(home[i][0],home[i][2]);}}}}
  function score(c,v,w){{
    // 띄어쓰기는 무시하고 비교한다(「연속 간행물」 = 「연속간행물」)
    var sp=/[\\s\\-·]+/g;
    var t=c.getAttribute('data-term').replace(sp,''),ns=c.getAttribute('data-names').split('|').map(function(x){{return x.replace(sp,'');}}),d=c.getAttribute('data-search');
    v=v.replace(sp,'');var vs=v.replace(/s$/,'');
    if(t===v)return 1000;
    if(ns.indexOf(v)>-1||ns.indexOf(vs)>-1)return 900;
    if(t.indexOf(v)===0)return 800;
    if(t.indexOf(v)>-1)return 700;
    for(var i=0;i<ns.length;i++){{if(ns[i].indexOf(v)===0)return 600;}}
    for(var j=0;j<ns.length;j++){{if(ns[j].indexOf(v)>-1||ns[j].indexOf(vs)>-1)return 500;}}
    var hit=w.every(function(x){{return d.indexOf(x)>-1||d.indexOf(x.replace(/s$/,''))>-1;}});
    return hit?100:0;
  }}
  function run(){{
    var v=q.value.trim().toLowerCase(),w=v.split(/\\s+/).filter(Boolean);
    restore();
    if(!v){{
      cards.forEach(function(c){{c.hidden=false;}});secs.forEach(function(s){{s.hidden=false;}});
      res.hidden=true;count.textContent=total+'개 용어';empty.style.display='none';
    }}else{{
      var hits=[];cards.forEach(function(c,i){{var sc=score(c,v,w);if(sc>0)hits.push([sc,i,c]);}});
      hits.sort(function(a,b){{return b[0]-a[0]||a[1]-b[1];}});
      hits.forEach(function(h){{h[2].hidden=false;res.appendChild(h[2]);}});
      secs.forEach(function(s){{s.hidden=true;}});
      res.hidden=!hits.length;count.textContent=hits.length+'개 찾음 / 전체 '+total+'개 · 맞는 정도 순';
      empty.style.display=hits.length?'none':'block';
    }}
    var rq=document.getElementById('req');if(rq){{rq.href=rq.getAttribute('data-form').replace('__TERM__',encodeURIComponent(q.value.trim()));}}
  }}
  q.addEventListener('input',run);
  [].slice.call(document.querySelectorAll('.chips a,.index-az a')).forEach(function(a){{a.addEventListener('click',function(){{if(q.value){{q.value='';run();}}}});}});
  if(location.search){{var m=location.search.match(/[?&]q=([^&]+)/);if(m){{q.value=decodeURIComponent(m[1].replace(/\\+/g,' '));run();}}}}
}})();
</script>
"""
    page += footer()
    (OUT / "index.html").write_text(page, encoding="utf-8")


def build_term_pages(cats, terms, by_id, src):
    cats_by_id = {c["id"]: c for c in cats}
    for i, t in enumerate(terms):
        d = OUT / "terms" / t["id"]
        d.mkdir(parents=True, exist_ok=True)
        ld = {"@context": "https://schema.org", **defined_term_ld(t, cats_by_id[t["category"]])}
        ld["inDefinedTermSet"] = {"@type": "DefinedTermSet", "@id": BASE_URL, "name": TITLE}
        ld["license"] = LICENSE_URL_EN
        prev_t = terms[i - 1] if i > 0 else None
        next_t = terms[i + 1] if i + 1 < len(terms) else None
        card = term_card(t, by_id, src, "../../", heading="h2", anchor=False)
        # 개별 페이지에서는 관련어를 각 용어 페이지로 잇는다
        for r in t["related"]:
            card = card.replace(f'href="../../#{r}"', f'href="../{r}/"')
        card = card.replace(f'href="terms/{t["id"]}/" class="t"', 'href="./" class="t"')
        page = head(
            f'{t["term"]} ({t["en"]}) — {TITLE}',
            t["definition"][:150],
            term_url(t),
            ld,
            prefix="../../",
        )
        pager = '<nav class="pager">'
        pager += f'<a href="../{prev_t["id"]}/">← {esc(prev_t["term"])}</a>' if prev_t else "<span></span>"
        pager += f'<a href="../{next_t["id"]}/">{esc(next_t["term"])} →</a>' if next_t else "<span></span>"
        pager += "</nav>"
        cat = cats_by_id[t["category"]]
        page += f"""<main class="wrap single">
<p class="crumb"><a href="../../">{TITLE}</a> › <a href="../../#cat-{cat['id']}">{esc(cat['name'])}</a></p>
<h1>{esc(t['term'])}</h1>
{card.replace('<h2><a href="./" class="t">' + esc(t['term']) + '</a></h2>', '')}
<p class="machine">이 용어의 Markdown: <a href="../{t['id']}.md">{t['id']}.md</a> · 고유 주소: <code>{term_url(t)}</code></p>
{pager}
</main>
"""
        page += footer()
        (d / "index.html").write_text(page, encoding="utf-8")
        (OUT / "terms" / f'{t["id"]}.md').write_text(term_md(t, by_id, src, cats_by_id, level=1), encoding="utf-8")


def term_md(t, by_id, src, cats_by_id, level=2):
    h = "#" * level
    lines = [f'{h} {t["term"]} ({t["en"]})', ""]
    lines.append(f'- 분야: {cats_by_id[t["category"]]["name"]}')
    lines.append(f'- 주소: {term_url(t)}')
    if t["aka"]:
        lines.append(f'- 다른 이름: {", ".join(t["aka"])}')
    lines += ["", t["definition"], ""]
    if t["example"]:
        lines += [f'예: {t["example"]}', ""]
    if t["related"]:
        lines.append("관련어: " + ", ".join(f'{by_id[r]["term"]}({r})' for r in t["related"]))
    srcs = [src[s]["name"] + (f' <{src[s]["url"]}>' if src[s].get("url") else "") for s in t["sources"]]
    lines.append("근거: " + ("; ".join(srcs) if srcs else "새로 쓴 설명(특정 표준에 기대지 않음)"))
    lines.append("")
    return "\n".join(lines)


def build_machine(cats, terms, by_id, src, sources):
    cats_by_id = {c["id"]: c for c in cats}
    # glossary.json
    data = {
        "name": TITLE,
        "name_en": TITLE_EN,
        "description": DESCRIPTION,
        "url": BASE_URL,
        "version": VERSION,
        "updated": UPDATED,
        "language": "ko",
        "license": {"name": LICENSE_NAME, "url": LICENSE_URL_EN},
        "attribution": f"{TITLE} ({BASE_URL}), {LICENSE_NAME}",
        "note": "모든 정의는 이 사전을 위해 새로 쓴 문장이다. sources는 정의를 쓸 때 기댄 자료이며 문장을 옮겨 온 출처가 아니다.",
        "ai_assisted": True,
        "ai_disclosure": "이 사전의 정의는 AI(Anthropic의 Claude)의 도움을 받아 작성했으며, 별도의 검수 과정에서 연도·법령·기관명 등 사실관계를 근거 자료와 대조했습니다.",
        "categories": cats,
        "sources": sources,
        "terms": [
            {
                "id": t["id"],
                "url": term_url(t),
                "term": t["term"],
                "en": t["en"],
                "aka": t["aka"],
                "category": t["category"],
                "category_name": cats_by_id[t["category"]]["name"],
                "definition": t["definition"],
                "example": t["example"] or None,
                "related": t["related"],
                "sources": t["sources"],
            }
            for t in terms
        ],
    }
    (OUT / "glossary.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # llms-full.txt
    full = [
        f"# {TITLE} ({TITLE_EN})",
        "",
        f"> {DESCRIPTION}",
        "",
        f"- 주소: {BASE_URL}",
        f"- 판: {VERSION} ({UPDATED})",
        f"- 이용 허락: {LICENSE_NAME} <{LICENSE_URL_EN}> — 출처「{TITLE} ({BASE_URL})」를 밝히면 자유롭게 이용 가능",
        "- 정의는 모두 새로 쓴 문장이며, '근거'는 정의를 쓸 때 기댄 표준·법령·기관 자료입니다.",
        "- 이 사전의 정의는 AI(Anthropic의 Claude)의 도움을 받아 작성했으며, 별도의 검수 과정에서 연도·법령·기관명 등 사실관계를 근거 자료와 대조했습니다.",
        "",
    ]
    for c in cats:
        full += [f'## {c["name"]}', ""]
        for t in terms:
            if t["category"] == c["id"]:
                full.append(term_md(t, by_id, src, cats_by_id, level=3))
    (OUT / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")

    # llms.txt
    l = [
        f"# {TITLE}",
        "",
        f"> {DESCRIPTION} 이용 허락은 {LICENSE_NAME}이며, 출처를 밝히면 AI 답변·검색·학습에 자유롭게 인용할 수 있습니다.",
        "",
        "한국어 문헌정보학(도서관학·정보학) 기본 용어사전입니다. 일반인 눈높이로 쓰였으며, 용어마다 영어 표제어·다른 이름·관련어·근거 자료가 있습니다.",
        "각 용어는 고유 주소 `terms/<id>/`(HTML)와 `terms/<id>.md`(Markdown)를 가집니다.",
        "이 사전의 정의는 AI(Anthropic의 Claude)의 도움을 받아 작성했으며, 별도의 검수 과정에서 연도·법령·기관명 등 사실관계를 근거 자료와 대조했습니다.",
        "",
        "## 전체 데이터",
        "",
        f"- [llms-full.txt]({BASE_URL}llms-full.txt): 용어 {len(terms)}개 전체 (Markdown, 한 파일)",
        f"- [glossary.json]({BASE_URL}glossary.json): 같은 내용의 구조화 JSON",
        "",
    ]
    for c in cats:
        l += [f'## {c["name"]}', ""]
        for t in terms:
            if t["category"] == c["id"]:
                short = t["definition"].split("다. ")[0].rstrip(".") + ("다." if "다. " in t["definition"] else "")
                l.append(f'- [{t["term"]} ({t["en"]})]({BASE_URL}terms/{t["id"]}.md): {short}')
        l.append("")
    (OUT / "llms.txt").write_text("\n".join(l), encoding="utf-8")

    # robots, sitemap
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8"
    )
    urls = [BASE_URL] + [term_url(t) for t in terms]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc><lastmod>{UPDATED}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


def main():
    cats, terms, src, sources = load()
    global DESCRIPTION
    DESCRIPTION = DESCRIPTION.replace("{N}", str(len(terms)))  # 용어 수는 자동으로 센다
    by_id = {t["id"]: t for t in terms}
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    build_index(cats, terms, by_id, src, sources)
    build_term_pages(cats, terms, by_id, src)
    build_machine(cats, terms, by_id, src, sources)
    print(f"built {len(terms)} terms -> {OUT}")


if __name__ == "__main__":
    main()
