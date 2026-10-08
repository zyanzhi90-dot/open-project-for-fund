import json,pathlib,sys
H=pathlib.Path(__file__).parent
for ident in sys.argv[1].split(','):
 b=json.loads((H/'sources'/f'{ident}.json').read_text(encoding='utf8'))
 print('\n',ident)
 for s in b['sources']:
  if '正文' not in s['kind']:print(s['kind'],s['url'],s['text'][-5000:])
