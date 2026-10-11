"""只整合检索入口与已有证据；不查年度公告、不写工作簿。"""
from pathlib import Path
import csv, re, json, hashlib, html
from urllib.parse import urlparse
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OLD = ROOT / '02_检索与核验记录/覆盖进度审计_20261011'
def read(name):
    with (OLD/name).open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def write(name, rows):
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def uid(prefix, value): return prefix+hashlib.sha256(value.encode()).hexdigest()[:12]
def clean(s): return re.sub(r'\s+', '', s or '').replace('中国科学院中国科学院','中国科学院')
def institution_name(s):
    s=clean(s)
    # 已有单校目录的描述后缀与单位名称分离；共同依托不强行拆分。
    if any(v in s for v in ['共同依托','联合','共建','、','；','依托单位见']):return s
    m=re.match(r'^(.+?(?:大学|学院))(.*)$',s)
    if m and re.search('平台|目录|补漏|机制|正确官网',m.group(2)):return m.group(1)
    if s.startswith('中国科学院自动化所尚未核'):return '中国科学院自动化研究所'
    return s
def urls(s): return list(dict.fromkeys(re.findall(r'https?://[^\s；;]+',s or '')))
def queue_hint(s):
    # 仅分派目录查阅顺序，不据名称判定项目相关/无关。
    if re.search('机器人|具身|人机|医工|生物医学工程|自动化|智能装备|机械|机电|感知|视觉|导航|测控|系统科学|控制|智能制造|人工智能',s): return '先查实际任务；名称仅为检索线索'
    return '目录补漏；先看任务摘要，有实际联系再查年度公告'
platforms=read('具名平台去重分类.csv')
base_platform_count=len(platforms)
directory_file=OUT/'新增官方目录名称底册.csv'
directory_rows=[];added=0;matched=0
if directory_file.exists():
    with directory_file.open(encoding='utf-8-sig',newline='') as f:directory_rows=list(csv.DictReader(f))
    index={(clean(r['依托机构']),clean(r['具名平台'])):r for r in platforms}
    for r in directory_rows:
        if r['执行分组']!='先看实际任务':continue
        inst=r['依托机构'] or '归属待核';name=r['平台名称'];key=(clean(inst),clean(name))
        evidence=r['来源URL']+'\n'+r['平台详情入口']
        if key in index:
            target=index[key];target['官方入口/来源']+='\n'+evidence;target['原记录位置']+='；'+r['来源定位'];matched+=1
            continue
        target={'依托机构':inst,'具名平台':name,'分类':'尚未查','判断依据':'官方目录具名身份；实际任务、开放机制及年度窗口未查','剩余动作或说明':'先看实际任务摘要及存续/更名；有联系后定位2026/2027开放入口；历史目录不能推定当前受理','关联编号':'','原记录位置':r['来源定位'],'官方入口/来源':evidence,'证据行':r['目录来源']+'；'+r['目录性质']}
        platforms.append(target);index[key]=target;added+=1
gaps=read('机构目录未闭环.csv')
institutions={}
def add(n, source='', entry='', basis='已有记录；名称和归属待目录复核'):
    n=institution_name(n)
    if not n or n in ['归属待核','依托单位待核','未知','未明确']: return ''
    if n not in institutions: institutions[n]={'机构ID':uid('I-',n),'机构名称':n,'机构类型':'高校' if '大学' in n or '学院' in n else '科研院所/其他依托机构待复核','入口候选':[],'记录来源':[],'身份依据':basis,'关联平台ID':[],'目录缺口':[]}
    x=institutions[n];x['入口候选']+=urls(entry);x['记录来源'].append(source)
    if basis.startswith('中科院官方'): x['身份依据']=basis
    return x['机构ID']
for r in platforms:
    n=r['依托机构']
    if '待核' not in n and n!='':add(n,'原平台审计',r['官方入口/来源'])
for r in gaps:
    n=r['机构或原查询范围']
    # 不将跨机构搜索范围和具名实验室伪装为独立机构。
    if re.search('大学|学院|研究所|研究院',n) and not re.search('[；;、]|全国|省级平台|高校群|等高校|相关高校',n):
        add(n,'原机构目录审计',r['已有入口']);institutions[institution_name(n)]['目录缺口'].append(r['具体缺口（保留原文）'])

casfile=OUT/'来源快照/cas.html'
cas=[]
if casfile.exists():
    s=casfile.read_text(encoding='utf8');a=s.find('>物理研究所</a>');b=s.find('id="content"',a)
    # 限定在研究单位正文；其后的新闻/导航不作为院所。
    segment=s[max(0,a-100):] if b<0 else s[max(0,a-100):b]
    for u,n in re.findall(r'<a[^>]+href=["\x27]([^"\x27]+)["\x27][^>]*>(.*?)</a>',segment,re.S):
        n=clean(html.unescape(re.sub('<[^>]+>','',n)))
        if not re.fullmatch(r'[\u4e00-\u9fff（）()·—]{2,45}',n):continue
        if not re.search('研究所$|研究院$|科学中心$|技术中心$|授时中心$|天文台$|植物园$|创新研究院$',n):continue
        if not u.startswith('https://'):continue
        if 'cas.cn' not in urlparse(u).netloc and 'ac.cn' not in urlparse(u).netloc:continue
        full=n if n.startswith('中国科学院') else '中国科学院'+n
        if any(x['机构名称']==full for x in cas):continue
        i=add(full,'中科院研究单位官网目录20261011',u,'中科院官方研究单位目录；单位站点未逐站访问')
        cas.append({'机构ID':i,'机构名称':full,'官网入口':u,'目录来源':'https://www.cas.cn/zz/jg/ys/yj/','查阅日期':'2026-10-11','年度公告状态':'未在本轮检索','后续范围':queue_hint(full)})
write('中科院官方院所底册.csv',cas)

pr=[]
for r in platforms:
    inst=clean(r['依托机构']);name=clean(r['具名平台']);pid=uid('P-',inst+'|'+name)
    key=institution_name(inst);iid=institutions.get(key,{}).get('机构ID','')
    if iid:institutions[key]['关联平台ID'].append(pid)
    pr.append({'平台ID':pid,'机构ID':iid,'依托机构原称':r['依托机构'],'平台名称原称':r['具名平台'],'规范身份状态':'待官方目录确认；不凭相似名称合并','检索顺序依据':queue_hint(name),'已有核验分类':r['分类'],'已有判断依据':r['判断依据'],'当期可申报结论':'本母表不作申报判定','年度核验范围':'复用原证据；未明确覆盖的2026/2027/延期/滚动仍须查','已有项目编号':r['关联编号'],'来源URL候选':r['官方入口/来源'],'URL使用限制':'旧表混有跨机构来源；查阅前核对页面单位及平台，不将全部URL认作本平台官网','原记录位置':r['原记录位置'],'原证据行':r['证据行'],'下一步':r['剩余动作或说明'] or '定位本平台官网通知/开放基金栏，先核窗口再核实际任务','别名及重组处理':'国家/全国重点实验室及省部共建旧称，取得官方更名/重组证据后才归并'})
write('具名平台母表.csv',pr)
ir=[]
for n,x in sorted(institutions.items()):
    ir.append({'机构ID':x['机构ID'],'机构名称':n,'机构类型':x['机构类型'],'身份依据':x['身份依据'],'相关平台数量':len(x['关联平台ID']),'关联平台ID':'；'.join(x['关联平台ID']),'官方入口候选':'\n'.join(dict.fromkeys(x['入口候选'])),'入口核验状态':'已有来源候选；具体目录与通知栏目待定位','目录完成状态':'尚未证明目录完整','原目录缺口':'\n'.join(dict.fromkeys(x['目录缺口'])),'记录来源':'；'.join(dict.fromkeys(x['记录来源'])),'目录检索范围':'科研院/科技处平台目录→机械、自动化、信息、医工等学院→国家/部委/省级平台交叉对账；中央高校另查校外开放业务费入口','公告检索模板':f'"{n}" (开放课题 OR 开放基金 OR 开放研究) (2026 OR 2027 OR 延期 OR 滚动)','检索顺序依据':queue_hint(n)})
write('机构母表.csv',ir)
write('机构目录原缺口.csv',gaps)
write('其他渠道及范围原记录.csv',read('其他渠道及名称不明范围_不计平台分母.csv'))

province_names='北京 天津 河北 山西 内蒙古 辽宁 吉林 黑龙江 上海 江苏 浙江 安徽 福建 江西 山东 河南 湖北 湖南 广东 广西 海南 重庆 四川 贵州 云南 西藏 陕西 甘肃 青海 宁夏 新疆 香港 澳门'.split()
domains='kw.beijing.gov.cn kxjs.tj.gov.cn kjt.hebei.gov.cn kjt.shanxi.gov.cn kjt.nmg.gov.cn kjt.ln.gov.cn kjt.jl.gov.cn kjt.hlj.gov.cn stcsm.sh.gov.cn kxjst.jiangsu.gov.cn kjt.zj.gov.cn kjt.ah.gov.cn kjt.fujian.gov.cn kjt.jiangxi.gov.cn kjt.shandong.gov.cn kjt.henan.gov.cn kjt.hubei.gov.cn kjt.hunan.gov.cn gdstc.gd.gov.cn kjt.gxzf.gov.cn dost.hainan.gov.cn kjj.cq.gov.cn kjt.sc.gov.cn kjt.guizhou.gov.cn kjt.yn.gov.cn sti.xizang.gov.cn kjt.shaanxi.gov.cn kjt.gansu.gov.cn kjt.qinghai.gov.cn kjt.nx.gov.cn kjt.xinjiang.gov.cn www.itc.gov.hk www.dsedt.gov.mo'.split()
sources=[]
def source(k,area,name,u,evidence,scope,state='入口已取得；目录内容尚待展开'):
    sources.append({'目录ID':k,'地域/层次':area,'来源名称':name,'官方入口':u,'入口依据':evidence,'应展开范围':scope,'目录状态':state,'下一步':'取得具名目录→与机构及平台ID对账→只新增缺项；目录旧年份只作名称底册，须核撤销/重组/新增','当前公告完成状态':'本轮未检索；目录入口不算年度公告核验完成'})
e='https://kw.beijing.gov.cn/sy/zddt/ 省（区市）科技部门网站；2026-10-11网页查阅'
for num,(n,d) in enumerate(zip(province_names,domains),1):
    source(f'D-P{num:02}',n,n+'科技主管部门','https://'+d+'/',e,'省重点/省部共建实验室、工程技术研究中心、新型研发机构；另经省教育主管部门展开高校重点实验室，经发改主管部门展开工程研究中心' if n not in ['香港','澳门'] else '高校及政府科研平台、内地合作开放课题；核实内地校外申请/合作入口')
national=[
('教育部高校名册','https://www.moe.gov.cn/jyb_xxgk/s5743/s5744/202606/t20260618_1441074.html','2026官方名单；教育部中国大学生在线 https://dxs.moe.gov.cn/zx/a/sy_xzsd/260618/2045120.shtml 可核发布事实；主站及附件访问受阻，尚未导入全量高校；勿用2025名册冒充现行名单'),
('中科院研究单位','https://www.cas.cn/zz/jg/ys/yj/','官方研究单位正文已提取；其余共建单位需交叉核对'),
('教育部科研基地平台','https://www.moe.gov.cn/jyb_xxgk/xxgk/neirong/fenlei/sxml_kxyj/kxyj_jdptgl/','教育部重点实验室及工程研究中心；各批次建设/评估/撤销目录交叉核对'),
('科技部全国重点实验室','https://www.most.gov.cn/','全国/原国家重点实验室、省部共建、工程技术研究中心；完整现行名单未取得，不能称全量'),
('发改委国家工程研究中心','https://www.ndrc.gov.cn/','国家工程研究中心新序列名单；与原国家工程实验室别名交叉核对'),
('工业和信息化部科研平台','https://www.miit.gov.cn/','工信部重点实验室、制造业创新中心、部属高校及科研机构目录'),
('农业农村部科研平台','https://www.moa.gov.cn/','农业机器人、智能农机、农业感知/装备任务平台；农业科研院所目录'),
('交通运输部科研平台','https://www.mot.gov.cn/','无人系统、智能装备、交通感知控制任务平台及院所目录'),
('自然资源部科研平台','https://www.mnr.gov.cn/','海洋无人装备、机器人测量任务平台；行业通用建模不能直接保留'),
('卫生健康科研平台','https://www.nhc.gov.cn/','医疗机器人、交互/医工装备任务平台；纯临床项目不展开'),
('国资委科研院所与企业平台','https://www.sasac.gov.cn/','央企科研院所、公开机器人/装备实验室；涉密或内部申报入口不列可申请'),
('市场监管科研平台','https://www.samr.gov.cn/','计量、检测、机器人与智能装备任务平台及科研机构'),
('水利科研平台','https://www.mwr.gov.cn/','无人巡检、智能装备任务平台；水文通用模型不足以认定相关'),
('应急管理科研平台','https://www.mem.gov.cn/','应急机器人、无人作业/感知装备平台'),
('中央高校校外开放业务费','https://www.moe.gov.cn/','按机构母表高校逐一查科研管理及平台开放入口；工信部/其他部属高校也纳入；普通校内业务费不收录'),
]
for num,(n,u,s) in enumerate(national,1):source(f'D-N{num:02}','国家/部委',n,u,e if num>3 else '官方网页检索/查阅2026-10-11',s)
source('D-BT','新疆兵团','兵团科技局','https://kjj.xjbt.gov.cn/c/2026-04-01/8477891.shtml','复用原覆盖记录','兵团重点实验室、工程技术研究中心及院所；与新疆自治区清单分别对账')
source('D-ZJ','浙江','浙江平台具名目录','https://stbrain.kjt.zj.gov.cn/CarrierList.aspx?Code=SYS','官方目录网页检索2026-10-11','重点实验室及工程技术研究中心具名、依托单位对账')
source('D-LN','辽宁','辽宁省2023重点实验室目录','https://kjt.ln.gov.cn/kjt/attachDir/2023/03/2023032915181664879.pdf','官方目录检索2026-10-11','历史具名底册；查新增、撤销、重组后再逐平台执行')
source('D-GD','广东','广东2022考核学科及企业类重点实验室名单','https://gdstc.gd.gov.cn/attachment/0/503/503027/4019700.pdf','复用旧来源URL；2026-10-11取得附件','历史具名底册；查新增、撤销及重组，不当作现行全量')
config=OUT/'补充目录配置.json'
if config.exists():
    for num,c in enumerate(json.loads(config.read_text(encoding='utf8')),1):
        state='整份具名目录已提取；当期公告及现行存续未核' if c['download_status']=='已取得' else '访问受阻；'+c.get('error','')
        source('D-X'+str(num),c['province'],c['name'],c['url'],'官方目录检索2026-10-11','具名平台及依托机构对账；历史及拟立项身份不代表当前受理',state)
for r in sources:
    if r['目录ID'] in ['D-LN','D-GD']:r['目录状态']='整份历史目录已提取具名身份；现行存续与其他目录待对账'
    if r['目录ID']=='D-ZJ':r['目录状态']='仅首屏20条已提取；更多入口访问受阻，未闭环'
write('全国目录来源母表.csv',sources)
tasks=[]
for s in sources: tasks.append({'任务ID':s['目录ID'],'任务类型':'目录展开补漏','对象':s['来源名称'],'关联ID':s['目录ID'],'入口或来源':s['官方入口'],'状态':s['目录状态'],'执行动作':s['应展开范围']})
for i in ir:tasks.append({'任务ID':'T-'+i['机构ID'],'任务类型':'机构目录对账','对象':i['机构名称'],'关联ID':i['机构ID'],'入口或来源':i['官方入口候选'],'状态':i['目录完成状态'],'执行动作':i['目录检索范围']})
for p in pr:tasks.append({'任务ID':'T-'+p['平台ID'],'任务类型':'具名平台年度公告','对象':p['依托机构原称']+'·'+p['平台名称原称'],'关联ID':p['平台ID'],'入口或来源':p['来源URL候选'],'状态':p['已有核验分类'],'执行动作':p['下一步']})
write('后续执行队列.csv',tasks)
wb=ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
stats={'建立日期':'2026-10-11','平台候选':len(pr),'原有平台候选':base_platform_count,'目录名称底册行数':len(directory_rows),'本轮目录新增候选':added,'本轮目录对应已有候选':matched,'机构名称条目':len(ir),'中科院目录提取单位':len(cas),'全国目录来源':len(sources),'省级地域入口':len(province_names),'机构或查询范围原缺口':len(gaps),'执行队列':len(tasks),'平台证据状态':dict(Counter(p['已有核验分类'] for p in pr)),'工作簿SHA256':hashlib.sha256(wb.read_bytes()).hexdigest(),'全国全量具名平台是否建齐':False,'未闭环':'高校全量附件未导入；大部分国家/部委/省级目录尚未展开；现有候选别名及部分归属待证据确认','全国完成率':None}
assert len(pr)==base_platform_count+added and len(set(p['平台ID'] for p in pr))==len(pr)
assert len(set(i['机构ID'] for i in ir))==len(ir)
assert len(province_names)==33 and len(tasks)==len(pr)+len(ir)+len(sources)
assert stats['工作簿SHA256']=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
(OUT/'建立及对账检查.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(stats,ensure_ascii=False))
