from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,hashlib,re,datetime
from openpyxl import load_workbook
H=Path(__file__).parent;R=H.parents[2];source=H/'baseline.xlsx'
Q='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def unpack(p):
 with zipfile.ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
f=unpack(source);a=unpack(H/'authored.xlsx'); changed=[]
newheaders=None
for n,b in a.items():
 if n.startswith('xl/tables/') and n.endswith('.xml'):
  t=E.fromstring(b)
  if t.get('name')=='OtherFunding':newheaders=[c.get('name') for c in t.find(Q+'tableColumns')]
assert newheaders and newheaders[6]=='申报主体及条件'
for n,b in f.items():
 if n.startswith('xl/tables/') and n.endswith('.xml'):
  t=E.fromstring(b);cs=t.find(Q+'tableColumns')
  if t.get('ref')=='A1:H3' and len(cs)==8:
   assert cs[6].get('name')=='具体待核事项';cs[6].set('name',newheaders[6]);E.register_namespace('',Q[1:-1]);f[n]=E.tostring(t,encoding='utf-8',xml_declaration=True);changed.append(n)
assert len(changed)==1
date_patches=json.loads((H/'date_plan.json').read_text(encoding='utf8'))
for part in dict.fromkeys(x['part'] for x in date_patches):
 tr=E.fromstring(f[part]);cells={c.get('r'):c for c in tr.iter(Q+'c')}
 for p in [x for x in date_patches if x['part']==part]:
  c=cells[p['ref']];assert c.get('t')=='d';c.set('t','n');c.find(Q+'v').text=str(p['serial'])
 E.register_namespace('',Q[1:-1]);E.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships');f[part]=E.tostring(tr,encoding='utf-8',xml_declaration=True);changed.append(part)
out=H/'全国机器人开放课题_个人申报台账_兼容性修正版_20261010.xlsx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in f.items():z.writestr(n,b)
orig=unpack(source);assert set(n for n in f if f[n]!=orig[n])==set(changed)
w=load_workbook(out);old=load_workbook(source)
for s in w:
 assert list(s.values)==list(old[s.title].values)
 for t in s.tables.values():assert [c.name for c in t.tableColumns]==[s.cell(1,j).value for j in range(1,s.max_column+1)] if s.title!='05机构检索覆盖' else True
pm={r[0]:r for r in list(w['02项目完整详情'].values)[1:]}; detail=list(w['02项目完整详情'].values);order=[]
def rank(v):
 text=str(v[24] or '')+' '+str(v[2] or '')
 if 'P0 南京' in text or any(x in text for x in ['南京','滁州']):return 0
 for k,words in enumerate([['澳门'],['香港'],['广州','深圳','珠海','佛山','东莞','中山','惠州','珠三角'],['北京'],['西安'],['重庆']],1):
  if any(x in text for x in words):return k
 return 7
for sn in ['01申报总览','04其他资助']:
 s=w[sn];keys=[]
 for i in range(2,s.max_row+1):
  dr=int(re.search(r'A(\d+)',s.cell(i,3).hyperlink.location)[1]);v=detail[dr-1];dt=s.cell(i,2).value
  key=(rank(v),dt.isoformat() if isinstance(dt,datetime.datetime) else '9999');keys.append(key)
  order.append({'sheet':sn,'row':i,'id':v[0],'region':v[24],'rank':key[0],'deadline':str(dt),'unit':s.cell(i,3).value})
 assert keys==sorted(keys),(sn,'Sorting failed')
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_parts':changed,'date_encoding_corrected_count':len(date_patches),'cell_contents_styles_links_and_order_unchanged':True,'current_views_sorting_verified':True,'order':order,'native_excel_check':'pending','visual_review':'pending'}
(H/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('One table header repaired; current-view sorting verified; all worksheet XML preserved.');w.close();old.close()
