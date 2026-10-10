from pathlib import Path
H=Path(__file__).parent
s=(H.parent/'20261010_当前申报清理'/'finalize.py').read_text(encoding='utf8')
s=s[:s.index("for name,entries in [('04其他资助'")]
s+='''
name='01申报总览';entries=D['home'];fn=origpaths[name];tree=E.fromstring(files[fn]);sd=tree.find(Q+'sheetData');template=list(sd)[1];templates={c.get('r').rstrip('0123456789'):c for c in template}
at=E.fromstring(auth[authpaths[name]]);arows={int(r.get('r')):r for r in at.find(Q+'sheetData')}
for old in list(sd)[1:]:sd.remove(old)
for n,e in enumerate(entries,2):
 row=E.Element(Q+'row',{**template.attrib,'r':str(n),'ht':arows[n].get('ht','48'),'customHeight':'1'})
 for ac in arows[n]:
  ref=ac.get('r');col=ref.rstrip('0123456789');row.append(translated(ac,templates.get(col),ref))
 sd.append(row)
if tree.find(Q+'dimension') is not None:tree.find(Q+'dimension').set('ref','A1:F22')
rels=replace_links(tree,fn,entries)
for rel in rels:
 if rel.get('Type','').endswith('/table'):
  tf=resolve(fn,rel.get('Target'));t=E.fromstring(files[tf]);t.set('ref','A1:F22');t.find(Q+'autoFilter').set('ref','A1:F22');files[tf]=xml(t)
files[fn]=xml(tree)
book=E.fromstring(files['xl/workbook.xml']);sheets=book.find(Q+'sheets');other=next(x for x in sheets if x.get('name')=='04其他资助');rid=other.get('{'+O+'}id');sheets.remove(other)
for x in sheets:
 if x.get('name')=='05机构检索覆盖':x.set('name','04机构检索覆盖')
for x in book.iter(Q+'definedName'):
 if x.get('localSheetId') and int(x.get('localSheetId'))>3:x.set('localSheetId',str(int(x.get('localSheetId'))-1))
 if x.text:x.text=x.text.replace('05机构检索覆盖','04机构检索覆盖')
for x in book.iter(Q+'workbookView'):x.set('activeTab','0');x.set('firstSheet','0')
files['xl/workbook.xml']=xml(book)
wr=E.fromstring(files['xl/_rels/workbook.xml.rels'])
for x in list(wr):
 if x.get('Id')==rid:wr.remove(x)
files['xl/_rels/workbook.xml.rels']=xml(wr)
delete=[origpaths['04其他资助'],rf(origpaths['04其他资助'])]
for r in E.fromstring(files[delete[1]]):
 if r.get('Type','').endswith('/table'):delete.append(resolve(delete[0],r.get('Target')))
for f in delete:files.pop(f,None)
ct=E.fromstring(files['[Content_Types].xml'])
for x in list(ct):
 if x.get('PartName','').lstrip('/') in delete:ct.remove(x)
files['[Content_Types].xml']=xml(ct)
if 'docProps/app.xml' in files:
 app=E.fromstring(files['docProps/app.xml']);A='{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}';V='{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}'
 titles=app.find(A+'TitlesOfParts')
 if titles is not None:
  v=titles.find(V+'vector')
  if v is not None:
   for x in list(v):v.remove(x)
   v.set('size','4')
   for n in D['new_sheets']:E.SubElement(v,V+'lpstr').text=n
 pairs=app.find(A+'HeadingPairs')
 if pairs is not None:
  for x in pairs.iter(V+'i4'):x.text='4'
 files['docProps/app.xml']=xml(app)
out=H/D['output_name']
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for fn,b in files.items():z.writestr(fn,b)
w=load_workbook(out);old=load_workbook(D['source']);orig=unpack(D['source'])
assert w.sheetnames==D['new_sheets']
for oldname,newname in [('02项目完整详情','02项目完整详情'),('03历史项目','03历史项目'),('05机构检索覆盖','04机构检索覆盖')]:
 assert list(w[newname].values)==list(old[oldname].values)
 assert files[origpaths[oldname]]==orig[origpaths[oldname]]
s=w['01申报总览'];assert s.max_row==22 and s.max_column==6 and s.freeze_panes=='A2' and next(iter(s.tables.values())).ref=='A1:F22'
for n,e in enumerate(D['home'],2):
 for j,v in enumerate(e['values'],1):
  if j!=2:assert s.cell(n,j).value==v
 assert s.cell(n,2).value==old[e['source_sheet']].cell(e['source_row'],2).value
 assert s.cell(n,3).hyperlink.location==f"'02项目完整详情'!A{e['detail_row']}"
 assert s.cell(n,6).hyperlink.target==e['url']
 if isinstance(s.cell(n,2).value,datetime.datetime):assert s.cell(n,2).value.date()>datetime.date(2026,10,10)
for sh in w:
 for t in sh.tables.values():
  row=int(re.search(r'(\\d+)',t.ref)[1]);assert [c.name for c in t.tableColumns]==[sh.cell(row,j).value for j in range(1,len(t.tableColumns)+1)]
 for row in sh:
  for c in row:
   if c.hyperlink and c.hyperlink.location:assert '04其他资助' not in c.hyperlink.location
assert w['02项目完整详情'].max_row==398 and len(D['removed_from_other'])==20
assert hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['source_sha256']
v={'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':D['source'],'source_sha256':D['source_sha256'],'home_count':21,'all_397_details_unchanged':True,'history_and_coverage_unchanged':True,'existing_21_tasks_terms_amounts_and_deadlines_unchanged':True,'date_links_table_headers_verified':True,'order':[e['id'] for e in D['home']],'visual_review':'pending','native_excel_check':'pending'}
(H/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print('21 merged rows and research-task order verified; all 397 detail rows unchanged.');w.close();old.close()
'''
(H/'finalize.py').write_text(s,encoding='utf8')
