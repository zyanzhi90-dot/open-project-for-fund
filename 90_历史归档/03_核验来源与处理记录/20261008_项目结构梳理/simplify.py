from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,csv,hashlib,copy
import openpyxl
H=Path(__file__).resolve().parent;R=H.parents[2]
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main';Q='{'+S+'}';O='http://schemas.openxmlformats.org/officeDocument/2006/relationships';P='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('',S);E.register_namespace('r',O)
source=H/'input.xlsx';b=openpyxl.load_workbook(source)
# Worksheet deletion/reordering lacks a documented artifact API in this runtime.
# Keep retained worksheet/native-table XML byte-for-byte; edit only package structure.
with zipfile.ZipFile(source) as z:files={n:z.read(n) for n in z.namelist()}
wb=E.fromstring(files['xl/workbook.xml']);sheets=wb.find(Q+'sheets');oldnodes={s.get('name'):s for s in sheets}
plan=[('01申报总览','01申报总览'),('02项目完整详情','02项目完整详情'),('06历史项目','03历史项目'),('07待核项目','04待核项目'),('08其他资助','05其他资助'),('03机构检索覆盖','06机构检索覆盖')]
retained={x[0] for x in plan};removed=[name for name in b.sheetnames if name not in retained];removed_ids={n.get('{'+O+'}id') for name,n in oldnodes.items() if name in removed}
for n in list(sheets):sheets.remove(n)
for old,new in plan:
 n=oldnodes[old];n.set('name',new);n.set('state','visible');sheets.append(n)
for v in wb.iter(Q+'workbookView'):v.set('activeTab','0');v.set('firstSheet','0')
files['xl/workbook.xml']=E.tostring(wb,encoding='utf-8',xml_declaration=True)
rels=E.fromstring(files['xl/_rels/workbook.xml.rels']);remove_files=[]
for rel in list(rels):
 if rel.get('Id') in removed_ids:
  target=rel.get('Target');fn=target.lstrip('/') if target.startswith('/') else 'xl/'+target
  remove_files.append(fn);rels.remove(rel)
files['xl/_rels/workbook.xml.rels']=E.tostring(rels,encoding='utf-8',xml_declaration=True)
# Keep exact historical cell anchors by redirecting links to the full archived workbook.
archive_target='90_历史归档/02_旧版与输出记录/20261009_结构精简前完整工作簿/全国机器人开放课题_个人申报台账_独立复核合并版_20261009.xlsx'
redirected=0
for old,new in plan:
 idx=b.sheetnames.index(old)+1;fn=f'xl/worksheets/sheet{idx}.xml';tree=E.fromstring(files[fn]);hp=tree.find(Q+'hyperlinks')
 if hp is None:continue
 targets=[x for x in hp if x.get('location','').split('!')[0].strip("'") in removed]
 if not targets:continue
 rf=f'xl/worksheets/_rels/sheet{idx}.xml.rels';rt=E.fromstring(files[rf]) if rf in files else E.Element('{'+P+'}Relationships')
 for i,link in enumerate(targets):
  rid=f'rIdArchiveAnchor{i+1}';link.set('{'+O+'}id',rid)
  E.SubElement(rt,'{'+P+'}Relationship',{'Id':rid,'Type':O+'/hyperlink','Target':archive_target,'TargetMode':'External'})
  redirected+=1
 files[rf]=E.tostring(rt,encoding='utf-8',xml_declaration=True);files[fn]=E.tostring(tree,encoding='utf-8',xml_declaration=True)
for fn in list(remove_files):
 rf=str(Path(fn).parent/'_rels'/(Path(fn).name+'.rels')).replace('\\','/')
 if rf in files:
  rt=E.fromstring(files[rf])
  for rel in rt:
   if rel.get('Type','').endswith('/table'):
    target=rel.get('Target');tf=(Path(fn).parent/target).as_posix() if not target.startswith('/') else target.lstrip('/')
    # Normalize package-relative '..', independent of host filesystem.
    import posixpath
    remove_files.append(posixpath.normpath(tf))
  remove_files.append(rf)
for fn in remove_files:files.pop(fn,None)
ct=E.fromstring(files['[Content_Types].xml'])
for el in list(ct):
 if el.get('PartName','').lstrip('/') in remove_files:ct.remove(el)
E.register_namespace('','http://schemas.openxmlformats.org/package/2006/content-types')
files['[Content_Types].xml']=E.tostring(ct,encoding='utf-8',xml_declaration=True)
E.register_namespace('',S)
if 'docProps/app.xml' in files:
 app=E.fromstring(files['docProps/app.xml']);A='{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}';V='{http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes}'
 titles=app.find(A+'TitlesOfParts')
 if titles is not None:
  vector=titles.find(V+'vector')
  if vector is not None:
   for x in list(vector):vector.remove(x)
   vector.set('size',str(len(plan)))
   for old,new in plan:E.SubElement(vector,V+'lpstr').text=new
 pairs=app.find(A+'HeadingPairs')
 if pairs is not None:
  for x in pairs.iter(V+'i4'):x.text=str(len(plan))
 files['docProps/app.xml']=E.tostring(app,encoding='utf-8',xml_declaration=True)
out=H/'全国机器人开放课题_个人申报台账_结构精简版_20261009.xlsx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for fn,data in files.items():z.writestr(fn,data)
# Export review records as UTF-8 BOM CSV so they remain searchable/filterable in Excel.
csv_outputs=[]
for sheet,name in [('04本轮信息核验日志','项目核验日志_20261009.csv'),('05剔除记录','项目剔除记录_20261009.csv')]:
 dst=H/name
 def literal(v):return '' if v is None else v.isoformat(sep=' ') if hasattr(v,'hour') else str(v)
 expected=[[literal(v) for v in row] for row in b[sheet].values]
 with dst.open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(expected)
 with dst.open(encoding='utf-8-sig',newline='') as f:assert list(csv.reader(f))==expected
 csv_outputs.append({'file':name,'rows':len(expected)-1,'columns':b[sheet].max_column})
w=openpyxl.load_workbook(out);assert w.sheetnames==[x[1] for x in plan]
for old,new in plan:
 assert list(b[old].values)==list(w[new].values),new
 assert b[old].freeze_panes==w[new].freeze_panes
 assert [(t.name,t.ref) for t in b[old].tables.values()]==[(t.name,t.ref) for t in w[new].tables.values()]
 # All cell styles, links and formatting are preserved by exact worksheet bytes.
for s in w:
 for row in s:
  for c in row:
   if c.hyperlink and c.hyperlink.location and not c.hyperlink.target:
    assert c.hyperlink.location.split('!')[0].strip("'") in w.sheetnames,c.hyperlink.location
assert w['01申报总览'].max_column==6
assert w['02项目完整详情'].max_row==167
validation={'input_sheets':10,'output_sheets':6,'sheet_mapping':dict(plan),'removed_to_csv':csv_outputs,'raw_inputs_retained_in_archived_workbook':removed[2:],'all_retained_values_and_formats_unchanged':True,'archive_links_redirected':redirected,'project_count':166,'current':15,'historical':96,'pending':51,'other':4,'output':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(H/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(validation,ensure_ascii=False))
