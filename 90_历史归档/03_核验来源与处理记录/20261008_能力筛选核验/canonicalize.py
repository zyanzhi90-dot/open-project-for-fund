import pathlib,json
f=pathlib.Path(__file__).parent/'corrections.json'
def combine(pairs):
 d={}
 for k,v in pairs:
  if k in d and isinstance(d[k],dict) and isinstance(v,dict):d[k].update(v)
  else:d[k]=v
 return d
d=json.loads(f.read_text(encoding='utf8'),object_pairs_hook=combine)
f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
