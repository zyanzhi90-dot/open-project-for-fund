from pathlib import Path
import zipfile,hashlib,json
import xml.etree.ElementTree as ET
H=Path(__file__).parent; R=H.parents[2]
source=R/'全国机器人开放课题_个人申报台账_申报合并与方向排序版_20261010.xlsx'
out=H/'全国机器人开放课题_个人申报台账_页签编号调整版_20261010.xlsx'
oldhash=hashlib.sha256(source.read_bytes()).hexdigest()
with zipfile.ZipFile(source) as z: files={n:z.read(n) for n in z.namelist()}
changed=[]
for name,b in list(files.items()):
    if not name.endswith(('.xml','.rels')): continue
    nb=b.replace('02项目完整详情'.encode(),'TMP_完整详情'.encode()).replace('03历史项目'.encode(),'02历史项目'.encode()).replace('TMP_完整详情'.encode(),'03项目完整详情'.encode())
    if nb!=b: files[name]=nb; changed.append(name)
# Put the renamed sheets in the same numeric order as their labels.
wbxml=ET.fromstring(files['xl/workbook.xml'])
ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
sheets=wbxml.find(ns+'sheets')
ordered=sorted(list(sheets),key=lambda x:int(x.get('name')[:2]))
for x in list(sheets): sheets.remove(x)
for x in ordered: sheets.append(x)
ET.register_namespace('',ns[1:-1]);ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
files['xl/workbook.xml']=ET.tostring(wbxml,encoding='utf-8',xml_declaration=True)
if 'xl/workbook.xml' not in changed: changed.append('xl/workbook.xml')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in files.items(): z.writestr(n,b)
report={'source':str(source),'source_sha256':oldhash,'output':str(out),'changed_parts':changed,'rename':'02项目完整详情→03项目完整详情；03历史项目→02历史项目','content_scope':'names and references only'}
(H/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
