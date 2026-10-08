import pathlib,json,zipfile,copy,hashlib,collections,re
from xml.etree import ElementTree as E
import openpyxl
R=pathlib.Path(__file__).parent;W=R.parents[1]
d=json.loads((R/'data.json').read_text(encoding='utf8'))
src=pathlib.Path(d['source'])
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
RID='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
E.register_namespace('',NS);E.register_namespace('r',RID)
q=lambda name:'{'+NS+'}'+name
def xml(b):return E.fromstring(b)
def dump(t):return E.tostring(t,encoding='utf-8',xml_declaration=True)
def package(f):
 with zipfile.ZipFile(f) as z:return {n:z.read(n) for n in z.namelist()}
def sheets(p):
 rels={x.get('Id'):x.get('Target') for x in xml(p['xl/_rels/workbook.xml.rels'])}
 return [(s.get('name'),('xl/'+rels[s.get('{'+RID+'}id')]).replace('xl//','')) for s in xml(p['xl/workbook.xml']).find(q('sheets'))]
def relpath(path):return str(pathlib.PurePosixPath(path).parent/'_rels'/(pathlib.PurePosixPath(path).name+'.rels'))
def resolve(path,target):
 import posixpath
 return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(path),target))
p=package(src);fresh=package(R/'homepage.xlsx')
sp=sheets(p);np=sheets(fresh);homepath=sp[0][1];detailpath=sp[1][1];newhome=xml(fresh[np[0][1]])
# Add only the styles needed by the authored homepage; all existing style indices remain intact.
oldstyles=xml(p['xl/styles.xml']);newstyles=xml(fresh['xl/styles.xml'])
offsets={}
for tag in ['fonts','fills','borders','cellStyleXfs','dxfs']:
 a=oldstyles.find(q(tag));b=newstyles.find(q(tag))
 if a is None:
  a=E.Element(q(tag),count='0')
  successors={'dxfs':['tableStyles','colors','extLst'],'cellStyleXfs':['cellXfs','cellStyles','dxfs','tableStyles']}.get(tag,[])
  i=next((i for i,x in enumerate(oldstyles) if x.tag in [q(z) for z in successors]),len(oldstyles));oldstyles.insert(i,a)
 offsets[tag]=len(a)
 if b is not None:
  for item in b:
   it=copy.deepcopy(item)
   if tag=='cellStyleXfs':
    for attr,t in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
     if attr in it.attrib:it.set(attr,str(int(it.get(attr))+offsets[t]))
   a.append(it)
 a.set('count',str(len(a)))
nf=oldstyles.find(q('numFmts'))
if nf is None:nf=E.Element(q('numFmts'),count='0');oldstyles.insert(0,nf)
nextnum=max([163]+[int(x.get('numFmtId')) for x in nf])+1;num_map={}
for x in newstyles.find(q('numFmts')) or []:
 it=copy.deepcopy(x);num_map[int(it.get('numFmtId'))]=nextnum;it.set('numFmtId',str(nextnum));nextnum+=1;nf.append(it)
nf.set('count',str(len(nf)))
oldx=oldstyles.find(q('cellXfs'));styleoffset=len(oldx)
for x in newstyles.find(q('cellXfs')):
 it=copy.deepcopy(x)
 for attr,t in [('fontId','fonts'),('fillId','fills'),('borderId','borders'),('xfId','cellStyleXfs')]:
  if attr in it.attrib:it.set(attr,str(int(it.get(attr))+offsets[t]))
 if int(it.get('numFmtId','0')) in num_map:it.set('numFmtId',str(num_map[int(it.get('numFmtId'))]))
 oldx.append(it)
oldx.set('count',str(len(oldx)));p['xl/styles.xml']=dump(oldstyles)
shared=xml(fresh['xl/sharedStrings.xml']) if 'xl/sharedStrings.xml' in fresh else []
for c in newhome.iter(q('c')):
 if c.get('s'):c.set('s',str(int(c.get('s'))+styleoffset))
 if c.get('t')=='s':
  idx=int(c.find(q('v')).text);c.remove(c.find(q('v')));c.set('t','inlineStr');ins=E.SubElement(c,q('is'))
  for child in shared[idx]:ins.append(copy.deepcopy(child))
for cf in newhome.iter(q('cfRule')):
 if cf.get('dxfId'):cf.set('dxfId',str(int(cf.get('dxfId'))+offsets['dxfs']))
# Keep the original table identity so workbook references remain valid.
oldrels=xml(p[relpath(homepath)])
table_rel=next(x for x in oldrels if x.get('Type','').endswith('/table'))
tablepath=resolve(homepath,table_rel.get('Target'))
newrels=xml(fresh[relpath(np[0][1])]);nt=next(x for x in newrels if x.get('Type','').endswith('/table'))
table=xml(fresh[resolve(np[0][1],nt.get('Target'))]);oldtable=xml(p[tablepath])
for attr in ['id','name','displayName']:table.set(attr,oldtable.get(attr))
p[tablepath]=dump(table)
if table.find(q('autoFilter')) is None:
 table.insert(0,E.Element(q('autoFilter'),ref='A1:F200'))
p[tablepath]=dump(table)
for t in newhome.iter(q('tablePart')):t.set('{'+RID+'}id',table_rel.get('Id'))
rels=E.Element('{'+REL+'}Relationships')
rels.append(copy.deepcopy(table_rel));hp=E.Element(q('hyperlinks'))
for i,r in enumerate(d['records'],2):
 E.SubElement(hp,q('hyperlink'),ref='C'+str(i),location="'"+d['detail_name'].replace("'","''")+"'!A"+str(r['detail_row']),display=r['row'][2])
 u=str(r['original'][9] or '')
 if re.match(r'https?://',u):
  ident='displayLink'+str(i)
  E.SubElement(hp,q('hyperlink'),ref='F'+str(i),display='公告',attrib={'{'+RID+'}id':ident})
  E.SubElement(rels,'{'+REL+'}Relationship',Id=ident,Type=RID+'/hyperlink',Target=u,TargetMode='External')
late=['printOptions','pageMargins','pageSetup','headerFooter','tableParts','extLst']
idx=next((i for i,x in enumerate(newhome) if x.tag in [q(z) for z in late]),len(newhome));newhome.insert(idx,hp)
p[homepath]=dump(newhome);p[relpath(homepath)]=dump(rels)
# Append the moved information to details without changing its original 26 columns.
dt=xml(p[detailpath]);sd=dt.find(q('sheetData'));rows={int(r.get('r')):r for r in sd}
def cell(rowno,colno,value,style):
 c=E.SubElement(rows[rowno],q('c'),r=openpyxl.utils.get_column_letter(colno)+str(rowno),s=str(style),t='inlineStr')
 t=E.SubElement(E.SubElement(c,q('is')),q('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=str(value)
headerstyle=rows[6][0].get('s','0');bodystyle=rows[7][0].get('s','0')
headers=['原首页类型','原首页优先级','原首页关键条件','原首页下一步动作','原首页完整记录','原首页顶部记录']
for j,h in enumerate(headers,27):cell(6,j,h,headerstyle)
for r in d['records']:
 old=r['original'];rn=r['detail_row']
 vals=[old[0],old[1],old[7],old[8],json.dumps(old,ensure_ascii=False)]
 for j,v in enumerate(vals,27):cell(rn,j,v if v is not None else '',bodystyle)
for i,t in enumerate(d['top_archive'],7):cell(i,32,json.dumps(t,ensure_ascii=False),bodystyle)
dimension=dt.find(q('dimension'))
if dimension is None:
 dimension=E.Element(q('dimension'));dt.insert(0,dimension)
dimension.set('ref','A1:AF205')
cols=dt.find(q('cols'))
if cols is not None:
 for i in range(27,33):E.SubElement(cols,q('col'),min=str(i),max=str(i),width='45',customWidth='1')
p[detailpath]=dump(dt)
dre=xml(p[relpath(detailpath)]);dr=next(x for x in dre if x.get('Type','').endswith('/table'));dp=resolve(detailpath,dr.get('Target'))
tab=xml(p[dp]);tab.set('ref','A6:AF205');af=tab.find(q('autoFilter'))
if af is not None:af.set('ref','A6:AF205')
tc=tab.find(q('tableColumns'))
for i,h in enumerate(headers,27):E.SubElement(tc,q('tableColumn'),id=str(i),name=h)
tc.set('count',str(len(tc)));p[dp]=dump(tab)
out=W/'outputs/20261008_display_revision';out.mkdir(exist_ok=True)
final=out/'全国机器人开放课题_个人申报台账_六列展示版_20261008.xlsx'
with zipfile.ZipFile(final,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in p.items():z.writestr(n,b)
# Reconcile the exported workbook and ensure original facts and source file are intact.
a=openpyxl.load_workbook(src);b=openpyxl.load_workbook(final)
assert a.sheetnames==b.sheetnames
assert b.worksheets[0].max_column==6 and b.worksheets[0].max_row==200
assert [c.value for c in b.worksheets[0][1]]==d['header']
assert b.worksheets[0].freeze_panes=='A2'
assert b.worksheets[0].tables['OpenCallsOverview'].ref=='A1:F200'
for i,rec in enumerate(d['records'],2):
 sh=b.worksheets[0]
 assert sh.cell(i,3).hyperlink.location.endswith('!A'+str(rec['detail_row']))
 assert sh.cell(i,6).hyperlink.target==rec['original'][9]
 assert json.loads(b.worksheets[1].cell(rec['detail_row'],31).value)==rec['original']
 if re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(rec['row'][1])):assert sh.cell(i,2).value.strftime('%Y-%m-%d')==rec['row'][1]
for si in range(1,len(a.worksheets)):
 for row in a.worksheets[si]:
  for c in row:
   n=b.worksheets[si][c.coordinate]
   assert c.value==n.value,(si,c.coordinate,'value changed')
   assert c.style_id==n.style_id,(si,c.coordinate,'style changed')
   if c.hyperlink:
    assert n.hyperlink and (c.hyperlink.target,c.hyperlink.location)==(n.hyperlink.target,n.hyperlink.location)
assert hashlib.sha256(src.read_bytes()).hexdigest()==d['source_sha256']
groups=collections.defaultdict(list)
for i,r in enumerate(d['records']):groups[r['org_key']].append(i)
assert all(max(v)-min(v)+1==len(v) for v in groups.values())
for org in groups:
 seq=[d['records'][i]['state_bucket'] for i in groups[org]];assert seq==sorted(seq)
assert '可申请' not in str([x['row'][0] for x in d['records']])
assert len(set(r['id'] for r in d['records']))==199
rep={'file':str(final),'projects':199,'homepage_columns':6,'detail_existing_cells_unchanged':True,'institutions_and_audit_unchanged':True,'institution_groups_contiguous':True,'status_order_valid':True,'source_unchanged':True,'hyperlinks':398,'native_filter':True,'freeze':'A2'}
(R/'qa.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rep,ensure_ascii=False))
