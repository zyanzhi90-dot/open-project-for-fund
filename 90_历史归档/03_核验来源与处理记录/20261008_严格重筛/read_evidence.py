import json,pathlib,re,sys
B=pathlib.Path(__file__).parent.parent/'20261008_最终收尾'
D=json.loads((B/'prepared_final.json').read_text(encoding='utf8'))
for ident in sys.argv[1:]:
 p=next(x for x in D['projects'] if x['id']==ident)
 print('\n###',ident,p['lab'],'\nFIELDS:',json.dumps(p['fields'],ensure_ascii=False))
 s=json.loads((B/'sources'/f'{ident}.json').read_text(encoding='utf8'))
 seen=set()
 for q in s['sources']:
  if q['url'] in seen:continue
  seen.add(q['url']);t=q.get('text','')
  print('SOURCE',q['url'],q.get('kind'),len(t))
  # Prefer announcement body over menus and related-article/footer matches.
  starts=[m.start() for m in re.finditer(r'(?:一[、．.]|1[、．.]|（一）).{0,18}(?:方向|内容|对象|要求|资助|申报|申请)|(?:二[、．.]|（二）).{0,12}(?:方向|内容)|资助领域|重点研究方向|开放课题研究方向',t)]
  print(t[starts[0]:starts[0]+6500] if starts else t[:6500])
 print('LINKS',json.dumps(s.get('links',[]),ensure_ascii=False))
