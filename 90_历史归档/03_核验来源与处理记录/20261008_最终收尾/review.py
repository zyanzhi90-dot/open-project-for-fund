import pathlib,json,re,sys
H=pathlib.Path(__file__).parent;P=H.parent/'20261008_能力筛选核验';O=H.parent/'rebuild'
D=json.loads((P/'input.json').read_text(encoding='utf8'));A=json.loads((O/'audit_all/attachment_index.json').read_text(encoding='utf8'))
ids=sys.argv[1].split(',') if len(sys.argv)>1 else list(D['norm'])
limit=int(sys.argv[2]) if len(sys.argv)>2 else 3000
for ident in ids:
 p=D['norm'][ident];f=H/'sources'/f'{ident}.json'
 if not f.exists():f=P/'sources'/f'{ident}.json'
 if f.exists():sources=json.loads(f.read_text(encoding='utf8'))['sources']
 else:
  b=json.loads((O/'official'/f'{ident}.json').read_text(encoding='utf8'));sources=[{'kind':'官方正文','url':b['url'],'text':b.get('text','')}]+[{'kind':a['name'],'url':a['url'],'text':a['text']} for a in A if ident in a.get('ids',[]) and a.get('text')]
 print('\n###',ident,p['org'],p['lab'])
 if sys.argv[-1]=='tail':
  for s in sources:print(s['kind'],s['url'],s['text'][-limit:])
  continue
 seen=set()
 for s in sources:
  if re.search('申请书|申请表|摘要|信息表|申报表',s['kind']) and not re.search('指南|管理|通知',s['kind']):continue
  if s['url'] in seen:continue
  seen.add(s['url']);t=s['text'];t=re.sub(r'L\d+:\s*','',t)
  if '.pdf' in s['url']:t=t.replace('\n','')
  # Start at published text rather than menus. Show entire short notices; retain specific task sections of long guidelines.
  starts=[m.end() for m in re.finditer(r'发布时间[：:]?[^\n]*|发布日期[：:]?[^\n]*|上传时间[：:]?[^\n]*',t)]
  if starts:t=t[starts[-1]:]
  print('SOURCE',s['kind'],s['url'])
  if limit==0:print(t);continue
  pats=r'(?:[一二三四五六七八九十][、.．]|I{1,3}\.)\s*(?:研究|资助|支持|指南|开放|申报|申请|課題|開放|Introduction|Research)|主要研究方向|拟资助研究方向|揭榜条件|Objectives|Research (?:Areas|Directions)|research topics'
  m=re.search(pats,t,re.I)
  if m:t=t[m.start():]
  print(t[:limit])
  if len(t)>limit:
   for m in list(re.finditer(r'(?:机器人|多传感|多模态|自动控制|智能装备|自动化|人工智能|协同控制|測控|Robotic|Artificial intelligence|feedback|control systems)',t,re.I))[:7]:
    if m.start()>limit:print('TASK',t[max(0,m.start()-50):m.start()+160])
