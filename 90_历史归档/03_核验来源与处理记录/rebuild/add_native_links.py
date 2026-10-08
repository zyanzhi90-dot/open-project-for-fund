"""Fill a missing artifact-tool export feature using the standard XLSX hyperlink XML.
All workbook data, tables, dates and styling are authored by artifact-tool.
This patch only adds hyperlinks; openpyxl is used separately for read-only QA.
"""
import pathlib,json,zipfile,io,posixpath
from lxml import etree as E
root=pathlib.Path(__file__).parent
out=root.parent.parent/'outputs'/'20261008_robot_fund_rebuild'
path=next(out.glob('*.xlsx'))
links=json.load(open(root/'native_links.json',encoding='utf8'))
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
RN='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PN='http://schemas.openxmlformats.org/package/2006/relationships'
with zipfile.ZipFile(path) as z:files={n:z.read(n) for n in z.namelist()}
work=E.fromstring(files['xl/workbook.xml']);rels=E.fromstring(files['xl/_rels/workbook.xml.rels'])
relmap={x.get('Id'):x.get('Target') for x in rels}
sheetmap={s.get('name'):posixpath.normpath(posixpath.join('xl',relmap[s.get('{'+RN+'}id')])) for s in work.findall('{'+NS+'}sheets/{'+NS+'}sheet')}
for name,sp in sheetmap.items():
 group=[x for x in links if x['sheet']==name]
 if not group:continue
 sp=sp.lstrip('/')
 if sp.startswith('xl/xl/'):sp=sp[3:]
 sheet=E.fromstring(files[sp]);node=E.Element('{'+NS+'}hyperlinks')
 rp=posixpath.join(posixpath.dirname(sp),'_rels',posixpath.basename(sp)+'.rels')
 sr=E.fromstring(files[rp]) if rp in files else E.Element('{'+PN+'}Relationships',nsmap={None:PN})
 targets={}
 for link in group:
  h=E.SubElement(node,'{'+NS+'}hyperlink',ref=link['cell'])
  if link['url'].startswith('#'):h.set('location',link['url'][1:])
  else:
   u=link['url']
   if u not in targets:
    rid='rIdHyperlink'+str(len(targets)+10000)
    targets[u]=rid
    E.SubElement(sr,'{'+PN+'}Relationship',Id=rid,Type=RN+'/hyperlink',Target=u,TargetMode='External')
   h.set('{'+RN+'}id',targets[u])
 after={'printOptions','pageMargins','pageSetup','headerFooter','rowBreaks','colBreaks','customProperties','cellWatches','ignoredErrors','smartTags','drawing','legacyDrawing','legacyDrawingHF','picture','oleObjects','controls','webPublishItems','tableParts','extLst'}
 position=next((i for i,child in enumerate(sheet) if E.QName(child).localname in after),len(sheet))
 sheet.insert(position,node)
 files[sp]=E.tostring(sheet,xml_declaration=True,encoding='UTF-8',standalone=True)
 files[rp]=E.tostring(sr,xml_declaration=True,encoding='UTF-8',standalone=True)
buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,content in files.items():z.writestr(name,content)
path.write_bytes(buffer.getvalue())
print('NATIVE HYPERLINKS',len(links),'OUTPUT',path)
