from pathlib import Path
from openpyxl import load_workbook
from collections import Counter,defaultdict
import json,re,csv,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).parent
source=next(p for p in R.glob('*.xlsx') if not p.name.startswith('~$'))
sha=hashlib.sha256(source.read_bytes()).hexdigest()
w=load_workbook(source,read_only=True)
coverage=[{'row':i,'v':list(v)} for i,v in enumerate(w.worksheets[3].values,1) if i>=7 and v[1]]
details=list(w.worksheets[2].values)[1:]
block=re.compile(r'验证码|首次.{0,12}(?:超时|失败|受阻|502|503|412)|正文.{0,12}(?:失败|受阻|未取得)|页面受阻|第一次超时|首503|首502|无法打开|访问失败|登录|登陆')
unknown=re.compile(r'未取得|未确认|待核|尚未|不明确|窗口未知|未核实|存在.*冲突')
def txt(x):return str(x or '').replace('\\n','\n')
def norm(x):
 x=clean(x);x=re.sub(r'（(?:20\d\d[^）]*|筹)）|\((?:20\d\d[^)]*|筹)\)','',x)
 x=re.sub(r'（[A-Za-z][^）]*）|\([A-Za-z][^)]*\)','',x)
 return re.sub(r'[\s·：:、，,\-/／（）()“”"\u3000]','',x).replace('国家级重点实验室','全国重点实验室').replace('国家重点实验室','全国重点实验室').replace('中科院','中国科学院')
def clean(x):
 x=txt(x).strip();x=re.sub(r'^(?:实际归属本机构的候选名称|实际归属本机构的候选|候选名称|平台名称)[:：]','',x)
 x=re.sub(r'20\d\d(?:—20\d\d)?(?:年度|年)?$','',x)
 if '；' in x:
  a,b=x.split('；',1)
  if not re.search(r'相关|待核',a):x=a
  else:
   b=re.sub(r'^(?:关于发布|关于申请|关于开展|关于|申请)|20\d\d(?:年度|年)|[〖〗【】]','',b)
   m=re.search(r'(.+?(?:重点实验室|工程研究中心|工程技术研究中心|工程实验室))',b)
   if m:x=m.group(1)
 x=re.sub(r'20\d\d年度线索$|20\d\d年首轮开放课题$','',x)
 return x.strip()
def unit(x):return txt(x).replace('中科院','中国科学院').split('／')[0].split('/')[0].strip()
platforms={};ids={};aliases={}
def add(u,p,origin,region='',id=None):
 u=unit(u);p=clean(p);k=(norm(u),norm(p))
 if k not in platforms:platforms[k]={'unit':u,'platform':p,'region':region,'records':[],'ids':[],'details':[],'exclusions':[],'origin':[]}
 x=platforms[k];x['origin'].append(origin)
 if id:x['ids'].append(id);ids[id]=k
 return k
for i,v in enumerate(details,2):
 if not v[0]:continue
 k=add(v[2],v[3],f'详情!A{i}',v[24],v[0]);platforms[k]['details'].append((i,list(v)))
# Exclusions are evidence, not new research candidates; retain for traceable deduplication.
ep=R/'02_检索与核验记录/审计记录/项目剔除记录_20261009.csv'
with ep.open(encoding='utf-8-sig',newline='') as f:
 for i,v in enumerate(csv.reader(f),1):
  if i==1 or len(v)<6 or v[0].startswith('材料_'):continue
  k=add(v[1],v[2],f'项目剔除记录.csv:{i}',id=v[0]);platforms[k]['exclusions'].append(v)
formal=re.compile(r'(?:实验室|工程研究中心|工程技术研究中心|研究院|研究所|创新中心|工程中心|技术中心|研发中心|工程实验室|研究中心|RCUAS|RISUD|RIAM|RIAIoT)$')
for r in coverage:
 v=r['v'];u=txt(v[1]);d=txt(v[3]);names=[]
 if '实际可读且归属本机构的候选：' in d and '此入口未取得' not in d:
  names=d.split('候选：',1)[1].split('；')
 elif v[0]=='2026-10-10具名平台年度补查':names=[d.split('；查询：',1)[0]]
 elif formal.search(u) and len(u)<95 and not re.search(r'目录|科研平台|母表|等|专项|查询',u):
  # Names in B without a separate institution are retained as a named candidate, avoiding guessed ownership.
  names=[u];u='归属待核（见原记录）'
 elif '查询：' not in d and '检索' not in d[:12]:
  for part in re.split(r'\n|；',d):
   p=part.split('｜')[0].strip()
   if formal.search(p) and len(p)<90 and not re.search(r'目录|入口|全文|已读|年度|完整|已核|机制|介绍|https|结果|须|其他',p):names.append(p)
 for name in names:
  name=name.strip()
  if len(name)>4 and len(name)<105 and not re.search(r'此入口|查询|年度：|http|；|通知|指南|新闻|招募|关于|仅列|已核|取得|确认',name):add(u,name,f'覆盖!第{r["row"]}行',v[2])
# Non-platform funding calls are accounted for separately, not mixed into the platform denominator.
channels=[]
for k,x in list(platforms.items()):
 if re.search(r'相关.{0,6}(?:平台|实验室)|全称待核|未知|目录',x['platform']) or not re.search(r'实验室|工程研究中心|工程技术研究中心|研究院|研究所|创新中心|工程中心|技术中心|研发中心|研究中心|平台|RCUAS|RISUD|RIAM|RIAIoT|SKL',x['platform']):channels.append(platforms.pop(k))
# Recover institution prefixes only when that institution already exists in the input.
known_units=sorted({x['unit'] for x in platforms.values() if not x['unit'].startswith('归属待核') and re.search(r'大学|学院|研究所|科学院',x['unit'])},key=len,reverse=True)
for k,x in list(platforms.items()):
 if x['unit'].startswith('归属待核'):
  p=x['platform'].replace('港理工/','香港理工大学/').replace('港理工／','香港理工大学／')
  u=next((u for u in known_units if p.startswith(u)),None)
  if u:
   name=p[len(u):].lstrip('/／· ');name=name or u
   nk=(norm(u),norm(name));x['unit']=u;x['platform']=name
   if nk!=k:
    old=platforms.pop(k)
    if nk in platforms:
     for f in ['origin','ids','details','exclusions']:platforms[nk][f].extend(old[f])
    else:platforms[nk]=old
# Merge ownership-unknown exact platform names only when there is one known institution.
byname=defaultdict(list)
for k,x in platforms.items():byname[norm(x['platform'])].append(k)
for name,ks in list(byname.items()):
 known=[k for k in ks if k[0]!=norm('归属待核（见原记录）')];unk=[k for k in ks if k[0]==norm('归属待核（见原记录）')]
 if len(known)==1:
  for k in unk:
   x=platforms.pop(k);dest=platforms[known[0]]
   for f in ['origin','ids','details','exclusions']:dest[f].extend(x[f])
# Attach direct-ID rows, exact named platform rows, and explicit mentions; never transfer institutional status to all platforms.
for k,x in list(platforms.items()):
 if (norm(x['unit'])==norm(x['platform']) and re.search(r'研究所|科学院$',x['platform']) and not x['details'] and not x['exclusions']) or x['platform'] in ['各全国重点实验室','内地研究院','南京/无锡研究院']:channels.append(platforms.pop(k))
for k,x in list(platforms.items()):
 if x['unit']=='香港理工大学' and x['platform']=='RCUAS':
  nk=(norm(x['unit']),norm('无人自主系统研究中心'));old=platforms.pop(k)
  if nk in platforms:
   for f in ['origin','ids','details','exclusions']:platforms[nk][f].extend(old[f])
  else:old['platform']='无人自主系统研究中心';platforms[nk]=old
ids={id:k for k,x in platforms.items() for id in x['ids']}
for r in coverage:
 v=r['v'];t=' '.join(txt(q) for q in v);keys=set()
 for id in re.findall(r'\b(?:M|N|R|F|S|E)\d{3}\b',txt(v[3])):
  if id in ids and ids[id] in platforms:keys.add(ids[id])
 nd=norm(v[3]);nb=norm(v[1])
 for k,x in platforms.items():
  p=norm(x['platform'])
  if f'覆盖!第{r["row"]}行' in x['origin']:keys.add(k)
  if len(p)>7 and (p in nd or p==nb):
   if x['unit'].startswith('归属待核') or norm(x['unit']) in nb or nb in norm(x['unit']) or p==nb:keys.add(k)
 for k in keys:platforms[k]['records'].append(r)
reportproof=defaultdict(list)
report=R/'02_检索与核验记录/全国三类来源补查与覆盖审计_20261010.md'
for ln,line in enumerate(report.read_text(encoding='utf8').splitlines(),1):
 if line.startswith('|') and re.search(r'当前受理|窗口已截止|已截止',line) and re.search(r'2026|2027',line) and not re.search(r'海洋精准感知|尚未|转载页面',line):
  for url in re.findall(r'https?://[^\s)）|]+',line):reportproof[url].append((ln,line))
def classify(x):
 done=[];blocked=[];notes=[]
 for n,v in x['details']:
  ev=txt(v[1]);year=txt(v[5]);date=txt(v[6]);task=txt(v[8]);status=txt(v[4]);url=txt(v[19])
  current=bool(re.search(r'2026|2027',year))
  official=bool(re.search(r'正式|正文.*(?:取得|读取|已读)|全文.*(?:取得|已读)|用户核实',ev)) and not re.search(r'未取得|打开失败|正文.{0,8}失败|首次打开|搜索定位|仅.{0,4}(?:标题|缓存)|转载线索',ev)
  actual=not re.search(r'年度具体.*未取得|具体.*任务.*未取得',task)
  if current and official and url and not unknown.search(date) and actual:
   done.append((n,'正式年度公告/指南已取得；已完成该来源的公告发现及状态判断。'))
  elif current and block.search(ev+' '+status):blocked.append((n,ev))
  else:notes.append((n,'现有为历史年度/机制/线索，或当期窗口、具体任务证据不足。'))
 # The newer search report can fill a discovery gap without editing Excel or losing older evidence.
 urls=re.findall(r'https?://[^\s<>]+',' '.join(txt(r['v'][6]) for r in x['records'])+' '+' '.join(txt(v[19]) for n,v in x['details'])+' '+' '.join(v[5] for v in x['exclusions']))
 for url in urls:
  if url in reportproof:done.append(('补查报告:'+str(reportproof[url][-1][0]),'后续补查报告已取得正式当期公告并给出明确截止/任务；原覆盖缺口已被后续证据解决。'))
 # Explicit complete current-year read in coverage can close a platform search even if excluded.
 for r in x['records']:
  d=txt(r['v'][3]);gap=txt(r['v'][4]);prog=txt(r['v'][5]);t=d+' '+gap
  if re.search(r'2026|2027',d) and re.search(r'(?:正式.*(?:全文|完整).*(?:取得|已读|已核)|2026.*(?:完整.*任务|完整指南.*已读)|逐平台.{0,8}(?:无当期公告|已核完))',d) and not re.search(r'尚未|未取得|待附件|待正文|仅搜索|仅查询',d):done.append((r['row'],'覆盖记录明确取得当前年度正式正文并完成判断。'))
  specific=norm(x['platform']) in norm(gap) or len(re.findall(r'\b(?:M|N|R|F|S|E)\d{3}\b',d))==1 or norm(r['v'][1]).endswith(norm(x['platform']))
  if block.search(t+' '+prog) and specific:blocked.append((r['row'],gap or prog))
 # A later acquisition overrides earlier transport errors, and missing application paperwork does not reopen a closed discovery task.
 if done:return '已逐平台查过',done[-1][1],done[-1][0],'缺失条款/个人合作落实不计为未检索；不代表当前仍受理。'
 if blocked:return '访问受阻','尚未完成当期公告/目录取证；有明确技术障碍记录。',blocked[-1][0],blocked[-1][1]
 return '尚未查','尚未完成具名平台当期年度核查；已有查询或旧资料不算闭环。',None,'需查看该平台官方通知/开放基金栏2026—2027；未命中不推定无公告。'
for x in platforms.values():
 x['status'],x['reason'],x['proof_row'],x['remaining']=classify(x)
 x['urls']=list(dict.fromkeys(re.findall(r'https?://[^\s<>]+',' '.join(txt(r['v'][6]) for r in x['records'])+' '+' '.join(txt(v[19]) for n,v in x['details'])+' '+' '.join(v[5] for v in x['exclusions']))))
 x['ids']=list(dict.fromkeys(x['ids']));x['origin']=list(dict.fromkeys(x['origin']))
def rank(x):
 s=x['unit']+' '+txt(x['region']);groups=['南京|东南大学|河海|苏州|无锡|常州|江苏','澳门','香港','华南理工|广州|广东|深圳|珠三角','自动化研究所|北京','西北工业|西安|陕西','重庆']
 return next((i for i,p in enumerate(groups) if re.search(p,s)),7),x['unit'],x['platform']
items=sorted(platforms.values(),key=rank)
# Institution/directory gaps remain separate; they are not one imaginary unnamed platform per institution.
institutions=defaultdict(list)
for r in coverage:
 v=r['v'];u=txt(v[1]);d=txt(v[3]);gap=txt(v[4])
 if re.search(r'目录|未列全|未齐|其他相关平台|逐平台|未逐一|范围尚',gap) and not formal.search(u):institutions[unit(u)].append(r)
out=R/'02_检索与核验记录/覆盖进度审计_20261011';out.mkdir(exist_ok=True)
def writecsv(name,heads,rows):
 with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
  wr=csv.writer(f);wr.writerow(heads);wr.writerows(rows)
heads=['依托机构','具名平台','分类','判断依据','剩余动作或说明','关联编号','原记录位置','官方入口/来源','证据行']
data=lambda x:[x['unit'],x['platform'],x['status'],x['reason'],x['remaining'],'；'.join(x['ids']),'；'.join(x['origin']),'\n'.join(x['urls']),x['proof_row']]
writecsv('具名平台去重分类.csv',heads,[data(x) for x in items])
writecsv('其他渠道及名称不明范围_不计平台分母.csv',['机构','渠道/项目/待拆分范围','原记录位置'],[[x['unit'],x['platform'],'；'.join(x['origin'])] for x in channels])
writecsv('具体剩余平台.csv',heads,[data(x) for x in items if x['status']!='已逐平台查过'])
writecsv('机构目录未闭环.csv',['机构或原查询范围','状态','具体缺口（保留原文）','已有入口','覆盖表行号'],[[u,'访问受阻' if any(block.search(txt(r['v'][4])+' '+txt(r['v'][5])) for r in rs) else '尚未查','\n'.join(dict.fromkeys(txt(r['v'][4]) for r in rs)),'\n'.join(dict.fromkeys(txt(r['v'][6]) for r in rs if r['v'][6])),'；'.join(str(r['row']) for r in rs)] for u,rs in institutions.items()])
raw=[]
for r in coverage:
 matches=[x for x in items if r in x['records']]
 if matches:status='已逐平台查过' if all(x['status']=='已逐平台查过' for x in matches) else ('访问受阻' if any(x['status']=='访问受阻' for x in matches) else '尚未查')
 else:status='访问受阻' if block.search(txt(r['v'][4])+' '+txt(r['v'][5])) else '尚未查'
 raw.append([r['row'],*r['v'],status,'仅查询/目录/条款记录不能单独计为一个已完成平台；分类依据去重平台母表。'])
writecsv('原覆盖记录逐行对账.csv',['原Excel行','覆盖层次','单位/平台','地域','已查范围','原缺口','原进度','原证据','原后续事项','审计分类','说明'],raw)
counts=Counter(x['status'] for x in items);N=len(items);pct=round(counts['已逐平台查过']/N*100,1)
summary={'source':source.name,'source_sha256':sha,'coverage_rows':len(coverage),'named_platforms':N,'counts':dict(counts),'closed_percent':pct,'unfinished_percent':round(100-pct,1),'institution_scope_gaps':len(institutions),'ownership_to_verify':sum(x['unit'].startswith('归属待核') for x in items),'out_of_denominator_channels_or_unclear_scopes':len(channels),'denominator':'从已有详情、剔除记录、具名目录及覆盖记录明确提取并按机构和名称去重的平台候选；别名尚无证据不强行合并；不是全国平台总数','audit_date':'2026-10-11','no_web_search':True,'no_excel_change':True}
(out/'统计与口径.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
(H/'platforms.json').write_text(json.dumps(items,ensure_ascii=False,default=str),encoding='utf8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('REMAINING EXAMPLES')
for x in [x for x in items if x['status']!='已逐平台查过'][:35]:print(x['unit'],x['platform'],x['status'])
