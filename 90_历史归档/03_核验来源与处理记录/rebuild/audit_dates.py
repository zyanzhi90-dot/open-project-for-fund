import json,re,pathlib
root=pathlib.Path(__file__).parent;raw=json.load(open(root/'original.json',encoding='utf8'))
for r in raw['02项目完整详情'][6:]:
 if not r[0]:continue
 t=json.load(open(root/'official'/f'{r[0]}.json',encoding='utf8')).get('text','')
 t=re.split('上一篇|下一篇|上一条|下一条|最新动态',t)[0]
 found=[]
 for m in re.finditer('截止|申请时间|受理时间|申报时间',t):
  piece=t[max(0,m.start()-65):m.end()+150]
  ds=re.findall(r'(202\d)\s*[年./-]\s*(\d{1,2})\s*[月./-]\s*(\d{1,2})',piece)
  for y,mo,da in ds:
   date=f'{y}-{int(mo):02d}-{int(da):02d}'
   if date not in [x[0] for x in found]:found.append((date,piece.replace('\n',' ')))
 if found and (r[4] not in [x[0] for x in found] or '未核' in str(r[4])):
  print(r[0],r[4],found)
