import pathlib,json,re,concurrent.futures,urllib.parse,urllib.request,time,io,html
from html.parser import HTMLParser
from pypdf import PdfReader
from docx import Document
H=pathlib.Path(__file__).parent; O=H.parent/'rebuild'; D=json.loads((H/'input.json').read_text(encoding='utf8')); decisions=json.loads((H/'decisions.json').read_text(encoding='utf8'))
keep=[r[0] for r in D['rows'] if r[0] not in decisions['exclude']]; (H/'sources').mkdir(exist_ok=True)
ai=json.loads((O/'audit_all/attachment_index.json').read_text(encoding='utf8'))
overrides={'M055':'https://kjc.qhnu.edu.cn/info/1062/2234.htm','M166':'https://ihealth.ccnu.edu.cn/info/1061/1751.htm'}
def htmlparse(content,url):
 content=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',content,flags=re.S|re.I)
 links=[]
 for href,name in re.findall(r'<a[^>]+href=[\"\x27]([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>',content,re.S|re.I):
  name=html.unescape(re.sub('<[^>]+>','',name)).strip()
  if re.search(r'附件|指南|管理办法|申请书|\.pdf|\.doc|DownloadAttachUrl',name+' '+href,re.I):links.append({'name':name,'url':urllib.parse.urljoin(url,html.unescape(href))})
 content=re.sub(r'</?(?:p|div|br|li|tr|h[1-6]|table)\b[^>]*>','\n',content,flags=re.I)
 text=html.unescape(re.sub('<[^>]+>','',content));text='\n'.join(x.strip() for x in text.splitlines() if x.strip())
 return text,links
def get(url,referer=''):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':referer or url})
 with urllib.request.urlopen(req,timeout=15) as r:b=r.read();typ=r.headers.get('Content-Type','');actualurl=r.url
 if b[:4]==b'%PDF':return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages),[],'PDF全文'
 if b[:2]==b'PK' and ('.docx' in url or 'word' in typ):
  doc=Document(io.BytesIO(b));t='\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(' | '.join(c.text for c in row.cells) for tab in doc.tables for row in tab.rows);return t,[],'DOCX全文'
 if b[:4]==bytes.fromhex('d0cf11e0'):return '',[],'旧DOC需原生解析'
 if 'text' in typ or b.lstrip().startswith(b'<'):
  encoding='utf-8';m=re.search(br'charset[=\"\x27\s]+([a-zA-Z0-9_-]+)',b[:5000])
  if m:encoding=m.group(1).decode('ascii')
  try:content=b.decode(encoding)
  except (UnicodeDecodeError,LookupError):content=b.decode('gb18030',errors='replace')
  t,links=htmlparse(content,actualurl)
  if re.search('验证码|无权访问|访问验证|Access Denied|CAPTCHA|Forbidden',t,re.I) and len(t)<1600:return '',links,'访问验证/受限'
  return t,links,'网页正文'
 return '',[],'未识别附件'
def one(ident):
 target=H/'sources'/f'{ident}.json'
 if target.exists():return json.loads(target.read_text(encoding='utf8'))
 p=D['norm'][ident];src=[];old=json.loads((O/'official'/f'{ident}.json').read_text(encoding='utf8'))
 if old.get('text'):src.append({'url':old['url'],'kind':'前轮官方正文存档','text':old['text'],'live':False})
 url=overrides.get(ident,p['url']);result={'id':ident,'url':url,'sources':src,'fetch_date':'2026-10-08','attempts':[]}
 try:
  t,links,status=get(url);result['attempts'].append({'url':url,'status':status})
  if t and len(t)>100:src.insert(0,{'url':url,'kind':'本轮官方正文','text':t,'live':True})
 except Exception as e:links=[];result['attempts'].append({'url':url,'status':str(e)[:160]})
 # Existing full-text attachments are retained with their official URLs; templates are not treated as eligibility evidence.
 for a in ai:
  if ident in a.get('ids',[]) and a.get('text') and re.search('指南|办法|规定|要求|制度|条例|通知|任务书',a.get('name','')):
   src.append({'url':a['url'],'kind':a['name'],'text':a['text'],'live':False})
 for directory in [O/'attachments',O/'audit_all/final_fetch',O/'audit_all/supplement']:
  for f in directory.glob(f'{ident}*.json'):
   try:x=json.loads(f.read_text(encoding='utf8'))
   except:continue
   if x.get('text') and x.get('url') not in [s['url'] for s in src]:src.append({'url':x['url'],'kind':f.stem,'text':x['text'],'live':False})
 # Fetch every linked guideline/rule that was unavailable in the source archive.
 todo=[l for l in links if re.search('指南|管理办法|制度|条例|申报通知',l['name']) and l['url'] not in [s['url'] for s in src] and l['url']!=url]
 for l in todo[:8]:
  try:
   t,_,status=get(l['url'],url);result['attempts'].append({'url':l['url'],'name':l['name'],'status':status})
   if t and len(t)>60:src.append({'url':l['url'],'kind':l['name'],'text':t,'live':True})
  except Exception as e:result['attempts'].append({'url':l['url'],'name':l['name'],'status':str(e)[:160]})
 result['links']=links
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');return result
if __name__=='__main__':
 allres=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
  for x in pool.map(one,keep):
   allres.append(x)
   print(x['id'],len(x['sources']),x['attempts'][0]['status'][:70] if x['attempts'] else '',flush=True)
 (H/'source_index.json').write_text(json.dumps(allres,ensure_ascii=False,indent=2),encoding='utf8')
 print('RETAIN',len(keep),'EXCLUDE',len(decisions['exclude']),'FRESH',sum(any(s['live'] for s in x['sources']) for x in allres),flush=True)
