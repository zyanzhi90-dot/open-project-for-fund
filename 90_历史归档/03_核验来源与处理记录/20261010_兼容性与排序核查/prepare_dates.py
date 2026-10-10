from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils.datetime import to_excel
import zipfile,xml.etree.ElementTree as E,posixpath,json
H=Path(__file__).parent;R=H.parents[2];p=R/'全国机器人开放课题_个人申报台账_当前申报清理版_20261010.xlsx'
Q='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';O='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
w=load_workbook(p);patches=[]
with zipfile.ZipFile(p) as z:
 rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 for s in E.fromstring(z.read('xl/workbook.xml')).find(Q+'sheets'):
  target=rels[s.get(O+'id')];fn=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl',target))
  for c in E.fromstring(z.read(fn)).iter(Q+'c'):
   if c.get('t')=='d':
    ref=c.get('r');patches.append({'sheet':s.get('name'),'part':fn,'ref':ref,'serial':to_excel(w[s.get('name')][ref].value),'before':c.find(Q+'v').text})
(H/'date_plan.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2),encoding='utf8');print('Native-incompatible date cells:',len(patches));w.close()
