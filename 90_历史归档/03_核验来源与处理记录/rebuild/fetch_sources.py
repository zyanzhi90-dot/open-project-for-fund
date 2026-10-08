import pathlib,json,concurrent.futures,re,time,urllib.request,urllib.parse,ssl
from lxml import html
ROOT=pathlib.Path(__file__).parent
d=json.loads((ROOT/'original.json').read_text(encoding='utf8'))
rows=[r for r in d['02项目完整详情'][6:] if r[0]]
folder=ROOT/'official';folder.mkdir(exist_ok=True)
def fetch(r):
    ident,url=r[0],r[16]
    dest=folder/(ident+'.json')
    if dest.exists(): return json.loads(dest.read_text(encoding='utf8'))
    out={'id':ident,'url':url,'status':'unread','text':'','links':[]}
    if not url: return out
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        z=urllib.request.urlopen(req,timeout=18,context=ssl._create_unverified_context())
        out['http']=z.status;out['final_url']=z.url
        if z.status==200:
            b=z.read(); match=re.search(rb'charset\s*=\s*[\"\x27]?([a-zA-Z0-9-]+)',b[:4000]); enc=match.group(1).decode() if match else 'utf-8'
            soup=html.fromstring(b.decode(enc,errors='replace'))
            out['links']=[{'text':a.text_content().strip(),'url':urllib.parse.urljoin(z.url,a.get('href'))} for a in soup.xpath('//a[@href]') if re.search(r'附件|申请|指南|办法|\.doc|\.pdf|\.zip|\.rar|\.xls',a.text_content()+' '+a.get('href'),re.I)]
            for x in soup.xpath('//script|//style|//nav|//footer|//header'): x.drop_tree()
            out['text']='\n'.join(x.strip() for x in soup.text_content().splitlines() if x.strip())
            out['status']='ok' if len(out['text'])>120 else 'empty'
        else:out['status']='http_error'
    except Exception as e:out['status']='failed';out['error']=str(e)[:180]
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    return out
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    result=list(pool.map(fetch,rows))
(ROOT/'official_sources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print(dict(Counter(r['status'] for r in result)),flush=True)
