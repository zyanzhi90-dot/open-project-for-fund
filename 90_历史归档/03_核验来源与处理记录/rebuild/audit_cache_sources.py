import pathlib,json,re
ROOT=pathlib.Path(__file__).parent;OUT=ROOT/'audit_all';data=json.load(open(ROOT/'normalized.json',encoding='utf8'))
urls={'M033':'https://slmt.cqu.edu.cn/info/10663/89610.htm','M189':'https://sqtmqz.ecjtu.edu.cn/info/1031/3831.htm','M192':'https://chongjian-lab.cqu.edu.cn/info/1012/2272.htm','M054':'https://seee.qhu.edu.cn/docs/2026-03/fd0e1502a79a4adaa673de1be5de9a97.pdf','M182':'https://www.must.edu.mo/cn/ssi/open'}
for p in data['projects']:
 f=ROOT/'official'/(p['id']+'.json');s=json.load(open(f,encoding='utf8'));u=urls.get(p['id'],s['url'])
 if p['id'] in ['M189']:
  n=json.load(open(OUT/'supplement'/(p['id']+'.json'),encoding='utf8'))
  if n['status']=='ok':n['id']=p['id'];f.write_text(json.dumps(n,ensure_ascii=False,indent=2),encoding='utf8');continue
 candidates=[]
 for src in OUT.glob('web_search_*.txt'):
  for block in src.read_text(encoding='utf8').split('--------------------------------------------------------------------------------'):
   if u in '\n'.join(block.strip().splitlines()[:3]) and 'Failed to fetch' not in block and 'Internal Error' not in block:
    lines=[]
    for line in block.splitlines():
     line=re.sub(r'^L\d+(?:@P\d+(?:-\d+)?)?:\s*','',line)
     line=re.sub(r'[^]*','',line)
     if line.strip():lines.append(line)
    if len(lines)>5:candidates.append(('\n'.join(lines),src.name))
 if candidates and (s['status']!='ok' or p['id'] in urls or len(s['text'])<900 and p['id']=='M112'):
  text,source=max(candidates,key=lambda x:len(x[0]));s.update(url=u,text=text,status='cached_official',cache_source=source,source_limit='浏览工具官网缓存；附件链接及未显示段落另核')
  f.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8');print(p['id'],len(text))
