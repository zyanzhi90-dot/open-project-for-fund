import json,pathlib,zipfile,xml.etree.ElementTree as E,posixpath
H=pathlib.Path(__file__).parent
ROOT=H.parents[2]
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_book(p):
 with zipfile.ZipFile(p) as z:
  ss=[''.join(t.itertext()) for t in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)] if 'xl/sharedStrings.xml' in z.namelist() else []
  rel={r.attrib['Id']:r.attrib['Target'] for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  out={}
  for s in E.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
   t=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
   root=E.fromstring(z.read(t.lstrip('/') if t.startswith('/') else posixpath.normpath('xl/'+t)))
   rows=[]
   for row in root.findall('m:sheetData/m:row',NS):
    cells=[]
    for c in row:
     letters=''.join(i for i in c.attrib['r'] if i.isalpha()); n=0
     for i in letters:n=n*26+ord(i)-64
     while len(cells)<n:cells.append(None)
     cells[n-1]=ss[int(c.find('m:v',NS).text)] if c.attrib.get('t')=='s' else ''.join(c.find('m:is',NS).itertext()) if c.attrib.get('t')=='inlineStr' else c.findtext('m:v',None,NS)
    rows.append(cells)
   out[s.attrib['name']]=rows
  return out
if __name__=='__main__':
 p=next(ROOT.glob('*.xlsx')); book=read_book(p)
 (H/'base_rows.json').write_text(json.dumps(book,ensure_ascii=False),encoding='utf8')
 print('Existing project ID | institution | lab | year | state | URL')
 for r in book['02项目完整详情'][1:]:print(' | '.join(str(r[i] or '') for i in [0,2,3,5,4,19]))
