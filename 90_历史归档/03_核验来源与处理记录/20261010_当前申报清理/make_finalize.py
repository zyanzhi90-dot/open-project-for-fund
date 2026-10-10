from pathlib import Path
H=Path(__file__).parent
s=(H.parent/'20261010_分类与排序调整'/'finalize.py').read_text(encoding='utf8')
s=s[:s.index('# Worksheet deletion/renaming')]
s=s.replace("for name,entries in [('01申报总览',D['home']),('03历史项目',D['history'])]:", "for name,entries in [('04其他资助',D['others']),('03历史项目',D['history'])]:")
s=s.replace("fn=origpaths[name];tree=", "last='H' if name=='04其他资助' else 'F';fn=origpaths[name];tree=")
s=s.replace("f'A1:F{len(entries)+1}'", "f'A1:{last}{len(entries)+1}'")
s=s.replace("files[fn]=xml(tree)\nfn=origpaths['02项目完整详情']", "\n if name=='04其他资助':\n  header=next(c for c in sd[0] if c.get('r')=='G1');ah=next(c for c in arows[1] if c.get('r')=='G1');idx=list(sd[0]).index(header);sd[0].remove(header);sd[0].insert(idx,translated(ah,header,'G1'))\n files[fn]=xml(tree)\nfn=origpaths['02项目完整详情']")
s+='''
out=H/D['output_name']
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for fn,b in files.items():z.writestr(fn,b)
source=load_workbook(D['source']);w=load_workbook(out)
assert w.sheetnames==D['new_sheets']
patch={(p['row'],p['col']):p['value'] for p in D['patches']}
for r in source['02项目完整详情']:
 for c in r:
  nc=w['02项目完整详情'][c.coordinate]
  assert nc.value==patch.get((c.row,c.column_letter),c.value),(c.coordinate,'Out-of-scope value change')
  assert nc.style_id==c.style_id
  if c.hyperlink:assert nc.hyperlink==c.hyperlink
orig=unpack(D['source'])
for name in ['01申报总览','05机构检索覆盖']:
 assert files[origpaths[name]]==orig[origpaths[name]]
for name,entries in [('04其他资助',D['others']),('03历史项目',D['history'])]:
 s=w[name];last='H' if name=='04其他资助' else 'F'
 assert s.max_row==len(entries)+1 and s.freeze_panes=='A2' and len(s.tables)==1
 assert next(iter(s.tables.values())).ref==f'A1:{last}{s.max_row}'
 for n,e in enumerate(entries,2):
  for j,value in enumerate(e['values'],1):
   if j!=2:assert s.cell(n,j).value==value,(e['id'],j)
  assert s.cell(n,2).value==source[e['source_sheet']].cell(e['source_row'],2).value
  assert s.cell(n,3).hyperlink.location==f"'02项目完整详情'!A{e['detail_row']}"
  assert s.cell(n,6).hyperlink.target==e['url']
  dt=s.cell(n,2).value
  if isinstance(dt,datetime.datetime):
   assert (dt.date()<datetime.date(2026,10,10)) if name=='03历史项目' else (dt.date()>datetime.date(2026,10,10))
assert w['02项目完整详情'].max_row==398
assert {e['id'] for e in D['others']}=={'F002','F022'}
assert len({r[0] for r in list(w['02项目完整详情'].values)[1:]})==397
assert hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['sha256']
report={'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'stats':D['stats'],'all_397_retained':True,'substantive_terms_and_sources_unchanged':True,'home_and_coverage_xml_unchanged':True,'links_filters_dates_verified':True,'visual_review':'pending','old_sha256':D['sha256']}
(H/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False));source.close();w.close()
'''
(H/'finalize.py').write_text(s,encoding='utf8')
