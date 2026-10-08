import pathlib,json,urllib.request,ssl,re,html
H=pathlib.Path(__file__).parent; O=H/'sources';O.mkdir(exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
requests_to_get=[('F004','https://www.nsfc.gov.cn/p1/3381/2824/142425.html','正式指南发布通告'),('M100','https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041515','附件1申报指南'),('M100','https://news.cqjtu.edu.cn/system/_content/download.jsp?owner=1252782971&urltype=news.DownloadAttachUrl&wbfileid=15041517','附件3管理办法')]
for ident,url,label in requests_to_get:
 fn=O/f'{ident}.json';d=json.loads(fn.read_text(encoding='utf8')) if fn.exists() else {'id':ident,'fetch_date':'2026-10-08','sources':[]}
 if any(x['url']==url for x in d['sources']):continue
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:raw=r.read().decode('utf-8','replace');code=r.status
  raw=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',raw,flags=re.I|re.S)
  t=html.unescape(re.sub(r'<[^>]+>','\n',raw));t='\n'.join(x.strip() for x in t.splitlines() if x.strip())
  d['sources'].append({'url':url,'kind':label,'text':t,'status':'验证码限制，附件未取得' if '验证码' in t else '已取得正文','http_status':code})
 except Exception as e:d['sources'].append({'url':url,'kind':label,'text':'','status':'未取得：'+type(e).__name__})
 fn.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
 print(ident,label,d['sources'][-1]['status'])
