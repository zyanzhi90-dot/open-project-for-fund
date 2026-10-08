import json,pathlib,re,sys
H=pathlib.Path(__file__).parent;O=H.parent/'rebuild';D=json.loads((H/'input.json').read_text(encoding='utf8'));C=json.loads((H/'decisions.json').read_text(encoding='utf8'));a=json.loads((O/'audit_all/attachment_index.json').read_text(encoding='utf8'))
ids=sys.argv[1].split(',') if len(sys.argv)>1 else list(C['exclude'])
for ident in ids:
 p=D['norm'][ident];s=json.loads((O/'official'/f'{ident}.json').read_text(encoding='utf8'));t=s.get('text','');m=re.search(r'一[、.．]\s*(?:研究|资助|指南|课题|主要|支持|申报|开放|基金|实验室)',t)
 if m:t=t[m.start():]
 print('\n###',ident,p['org'],p['lab'],'\n',t[:1500])
 for x in a:
  if ident in x.get('ids',[]) and re.search('指南|方向|选题|研究内容',x['name']):print('附件:',x['name'],'\n',x.get('text','')[:1800])
