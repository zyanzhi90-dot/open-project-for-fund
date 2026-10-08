import pathlib,json,re
H=pathlib.Path(__file__).parent;d=json.loads((H/'prepared.json').read_text(encoding='utf8'))
for p in d['projects']:
 b=json.loads((H/'sources'/f"{p['id']}.json").read_text(encoding='utf8'))
 for s in b['sources'][:1]:
  text=s['text'].replace('\n','')
  hits=re.findall(r'.{0,25}(?:截止|提交申请|申请书.{0,10}于).{0,60}',text)
  for t in hits:
   dt=re.search(r'(20\d\d)\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',t)
   if dt:
    candidate=f'{dt[1]}-{int(dt[2]):02}-{int(dt[3]):02}'
    if p['date']!=candidate:print(p['id'],'old',p['date'],'candidate',candidate,t)
