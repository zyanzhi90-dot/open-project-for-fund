import json,pathlib,sys
H=pathlib.Path(__file__).parent
D=json.loads((H/'prepared.json').read_text(encoding='utf8'))
for ident in sys.argv[1].split(','):
 p=next(x for x in D['projects'] if x['id']==ident)
 print('\n',ident,p['url'])
 b=json.loads((H/'sources'/f'{ident}.json').read_text(encoding='utf8'))
 for s in b['sources']:print(s['kind'],s['url'],len(s['text']),s['text'][:180].replace('\n',' '))
for p in D['projects']:
 if len(p['amount'])>30:print('LONG MONEY',p['id'],p['amount'])
