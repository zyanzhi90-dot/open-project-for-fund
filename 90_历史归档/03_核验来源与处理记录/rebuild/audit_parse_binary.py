import sys,pathlib,struct,json,io,zipfile,re,subprocess
ROOT=pathlib.Path(__file__).parent;sys.path.insert(0,str(ROOT/'pydeps'));import olefile
from pypdf import PdfReader
from lxml import etree
import openpyxl
def word(b):
 o=olefile.OleFileIO(io.BytesIO(b));w=o.openstream('WordDocument').read();t=o.openstream('1Table' if struct.unpack_from('<H',w,10)[0]&0x200 else '0Table').read()
 fc,lcb=struct.unpack_from('<II',w,0x1a2);c=t[fc:fc+lcb];j=0
 while c[j]==1:j+=3+struct.unpack_from('<H',c,j+1)[0]
 if c[j]!=2:raise ValueError('无CLX piece table')
 ln=struct.unpack_from('<I',c,j+1)[0];p=c[j+5:j+5+ln];n=(ln-4)//12;cp=struct.unpack_from('<'+'I'*(n+1),p,0);a=[]
 for i in range(n):
  x=struct.unpack_from('<I',p,4*(n+1)+8*i+2)[0];count=cp[i+1]-cp[i]
  if x&0x40000000:f=(x&0x3fffffff)//2;a.append(w[f:f+count].decode('cp1252',errors='replace'))
  else:f=x&0x3fffffff;a.append(w[f:f+count*2].decode('utf-16le',errors='replace'))
 return ''.join(a).replace('\r','\n').replace('\x07','\t')
def extract(b):
 if b.startswith(bytes.fromhex('D0CF11E0')):
  o=olefile.OleFileIO(io.BytesIO(b))
  if o.exists('Workbook') or o.exists('Book'):
   import xlrd
   w=xlrd.open_workbook(file_contents=b)
   return '\n'.join(s.name+'\n'+'\n'.join('\t'.join(str(s.cell_value(i,j)) for j in range(s.ncols)) for i in range(s.nrows)) for s in w.sheets())
  return word(b)
 if b.startswith(b'%PDF'):return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(b)).pages)
 if b.startswith(b'PK'):
  z=zipfile.ZipFile(io.BytesIO(b))
  if 'word/document.xml' in z.namelist():return '\n'.join(''.join(p.itertext()) for p in etree.fromstring(z.read('word/document.xml')).xpath('//*[local-name()="p"]'))
  if 'xl/workbook.xml' in z.namelist():
   w=openpyxl.load_workbook(io.BytesIO(b),data_only=False,read_only=True)
   return '\n'.join(s.title+'\n'+'\n'.join('\t'.join(str(x) if x is not None else '' for x in row) for row in s.values) for s in w)
  texts=[]
  for n in z.namelist():
   if re.search(r'\.docx?$|\.pdf$|\.xlsx$',n,re.I):
    try:texts.append(n+'\n'+extract(z.read(n)))
    except Exception as e:texts.append(n+'：解析失败 '+str(e))
  return '\n'.join(texts)
 return ''
result=[]
for m in (ROOT/'audit_all'/'attachments').glob('*.json'):
 d=json.load(open(m,encoding='utf8'));f=pathlib.Path(d.get('file',''))
 if f.is_file() and not d.get('text'):
  try:
   b=f.read_bytes()
   if b.startswith(b'Rar!'):
    dest=f.parent/(f.stem+'_unpack');dest.mkdir(exist_ok=True)
    subprocess.run([str(ROOT/'unrar'/'UnRAR.exe'),'x','-y','-o+',str(f),str(dest)+'\\'],capture_output=True,timeout=45)
    d['text']='\n'.join(str(x.relative_to(dest))+'\n'+extract(x.read_bytes()) for x in dest.rglob('*') if x.is_file() and re.search(r'\.docx?$|\.pdf$|\.xlsx$',x.name,re.I))
   else:d['text']=extract(b)
   if d['text'].strip():d['status']='全文已提取';f.with_suffix('.txt').write_text(d['text'],encoding='utf8')
  except Exception as e:d['parse_error']=str(e)[:200]
  m.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
 result.append(d)
(ROOT/'audit_all'/'attachment_index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print(dict(Counter(a['status'] for a in result)))
