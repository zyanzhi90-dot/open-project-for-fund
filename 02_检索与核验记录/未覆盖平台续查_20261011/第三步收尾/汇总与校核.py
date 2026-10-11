"""Finalize the named-platform search pass; does not claim nationwide closure."""
import csv,json,re,hashlib,shutil
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'02_检索与核验记录'; BASE=D/'未覆盖平台续查_20261011'; OUT=BASE/'第三步收尾'
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);return list(r),r.fieldnames
def writecsv(p,rs,fs):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rs)
def readjson(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def text(v):return '\n'.join(map(str,v)) if isinstance(v,list) else str(v or '')

inputs=sum((readjson(OUT/f'定向输入_{n}.json') for n in range(1,4)),[])
results=sum((readjson(OUT/f'定向结果_{n}.json') for n in range(1,4)),[])
assert len(inputs)==len(results)==414
assert len({r['id'] for r in results})==414
assert {r['id'] for r in results}=={r['id'] for r in inputs}
motherpath=D/'检索母表_20261011/具名平台母表.csv'
queuepath=D/'检索母表_20261011/后续执行队列.csv'
mother,mfields=readcsv(motherpath); queue,qfields=readcsv(queuepath)
mx={r['平台ID']:r for r in mother}; inputids={r['id'] for r in inputs}
assert {r['平台ID'] for r in mother if r['已有核验分类']=='尚未查'}==inputids
workbooks=[p for p in ROOT.glob('*.xlsx') if not p.name.startswith('~$')]
assert len(workbooks)==1
wb=workbooks[0]; sha=hashlib.sha256(wb.read_bytes()).hexdigest()
assert sha=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
before=json.loads(json.dumps(mother)); evidence_audit=[]; final=[]; missing_audit=[]
for r in results:
    assert text(r.get('query')) and text(r.get('事实及边界'))
    files=r.get('查询证据文件',[])
    if isinstance(files,str):files=[files]
    assert files,r['id']
    paths=[]; existing_files=[]; missing_files=[]
    for name in files:
        p=Path(name)
        if not p.is_absolute():p=(ROOT/p) if (ROOT/p).is_file() else OUT/p
        if p.is_file():
            paths.append(p);existing_files.append(name)
        else:
            missing_files.append(name);missing_audit.append({'平台ID':r['id'],'原引用缺档':name,'处理':'另一次现存原始查询证据可定位；未重搜，缺档不伪造'})
    assert any('证据' in p.name and '索引' not in p.name and len(p.read_text(encoding='utf-8-sig'))>2 for p in paths),r['id']
    # Each output is tied to saved query-ID mapping, not merely a fetched page.
    assert any(r['id'] in p.read_text(encoding='utf-8-sig') for p in paths),r['id']
    evidence_audit.append({'id':r['id'],'query':r['query'],'证据文件':existing_files,'存在及ID映射':True,'原引用缺档':missing_files})
    files=existing_files
    m=mx[r['id']]; judgment=text(r.get('判断')); fact=text(r['事实及边界'])
    deadline=text(r.get('截止原句')); note=''
    status='定向检索已执行·窗口或任务未取得'
    if ('已截止' in judgment or '已过' in judgment or '过期' in judgment) and deadline and re.search(r'20\d\d',deadline):
        status='定向检索已执行·命中公告已截止'
    elif '身份' in judgment or '身份' in fact and '冲突' in fact:
        status='定向检索已执行·来源身份待核'
    elif '无关' in judgment:
        status='定向检索已执行·未有相关任务依据'
        note='不据平台名称或截取片段排除整个机构。'
    if r['id']=='P-5df3b064f9e4':
        status='定向检索已执行·当前公告任务未有相关装备依据'
        fact='主代理读取包头师范学院2026磁学完整公告，10月23日前申报；方向为稀土磁性/功能材料、自旋电子、统计物理和稀土应用器件，未有机器人或相关智能装备实际任务依据。'
        deadline='申报者于2026年10月23日之前将课题申报材料附件1、2报送。'
    if r['id']=='P-b69b34963118':
        status='定向检索已执行·当期窗口成立但任务图片受阻'
        fact='露天煤矿灾害防治与生态保护全国重点实验室2026新公告当前窗口成立；具体任务在7张图片中，首次读取均超时，留缺停止，不计当前相关项目。'
        note='图片URL和首次失败见露天煤矿指南图片取证.json；2025旧公告不能替代2026任务。'
    if r['id']=='P-d0fd22bad1d4':
        status='定向检索已执行·当前公告材料任务未有智能装备依据'
        fact='主代理读海南大学2026正式指南，截止10月31日24:00；任务为材料腐蚀在线监测、数据库、材料表征、深海装备玻璃及材料设计制备等，未有机器人或智能装备感知决策控制等实际任务依据。保留材料及海洋应用边界，不据在线监测泛词收录。'
        deadline='于2026年10月31日24:00前将电子版发送到skltoem@hainanu.edu.cn。'
        note='正文来源https://skltm.hainanu.edu.cn/info/1341/6871.htm；证据海南海洋材料2026指南核验.json。'
    if r['id']=='P-2b84da50a2c1':
        status='定向检索已执行·命中公告已截止'
        fact='主代理读高校科研院转发的2026新能源汽车轻量化铸件实验室公告，申报程序明确8月1日前提交，当前已经截止；停止补取。平台主体为大连科技学院，转发单位沈阳化工大学不冒充依托单位。'
        deadline='申请人根据通知中的申报领域选定研究方向，并在8月1日前将申请书电子版发送至申报邮箱。'
        note='2026年度上下文据正文；证据海南材料与新能源铸件窗口核验.json；不延伸历史结题条款。'
    assert not r.get('候选当前相关'),('unreviewed candidate',r['id'])
    if missing_files:note+=('；' if note else '')+'原结果另有缺档引用：'+text(missing_files)+'；本汇总仅引用另一轮现存证据，未重复请求或伪造。'
    final.append({'平台ID':r['id'],'依托机构':m['依托机构原称'],'平台':m['平台名称原称'],'核查日期':'2026-10-11',
        '实际查询':text(r['query'])+('\n'+text(r['补充查询']) if r.get('补充查询') else ''),'证据分类':status,
        '来源URL':text(r.get('来源URL')),'事实及边界':fact,'截止原句':deadline,'任务原句':text(r.get('任务原句')),
        '明示金额':text(r.get('明示金额')),'关键条件':text(r.get('关键条件')),'已有项目编号':m['已有项目编号'],
        '查询证据文件':text(files),'主代理校核说明':note,'剩余范围':'本轮具体定向搜索已执行；未定位不证明不存在，缺口不反复补取；新年度/新批次及全国未列名平台仍属后续范围。'})
    m['20261011补查前分类']=m['已有核验分类']; m['已有核验分类']=status;m['已有判断依据']=fact
    m['20261011定向补查记录']='未覆盖平台续查_20261011/第三步收尾/平台定向补查汇总.csv'
    m['年度核验范围']='2026-10-11执行具名定向搜索；不以公告年度替代窗口，不把未命中或受阻记为年度穷尽。'
    m['下一步']='本轮定向检索已执行；窗口/任务缺口详见汇总；受阻不重试，新年度及新批次另查。'
status_by_id={r['平台ID']:r['证据分类'] for r in final}
for t in queue:
    if t['关联ID'] in status_by_id:
        t['状态']=status_by_id[t['关联ID']];t['执行动作']='本轮具体平台定向已执行，见第三步收尾/平台定向补查汇总.csv；保留公开证据缺口，不作全国闭环。'
# Add only newly inspected specific platforms, preserving the preceding records.
reviews=readjson(OUT/'类别命中主代理校核.json'); newly_added=[]
for r in reviews:
    if not r.get('依托机构') or r.get('已有编号'):continue
    if any(r['来源URL'] in m['来源URL候选'].splitlines() for m in mother):continue
    pid='P-'+hashlib.sha256((r['依托机构']+'|'+r['平台']).encode()).hexdigest()[:12]
    assert pid not in mx
    m={k:'' for k in mfields};m.update({'平台ID':pid,'依托机构原称':r['依托机构'],'平台名称原称':r['平台'],
        '规范身份状态':'2026公告正文或官方标题取得；具体身份范围见来源','检索顺序依据':'本轮类别交叉检索附带发现',
        '已有核验分类':'类别定向已执行·'+r['判断'],'已有判断依据':r['事实'],'当期可申报结论':'不进入当前相关清单；窗口和任务分别记录',
        '年度核验范围':'2026年度具体公告；已截止停止补取，受阻保留缺口','来源URL候选':r['来源URL'],
        'URL使用限制':'仅本次具体官方来源；不代表机构全部目录和年度穷尽','原记录位置':'第三步收尾/类别命中主代理校核.json',
        '下一步':'已截止不补条款；首次受阻不重试；新年度/新批次按正式公告另核',
        '20261011定向补查记录':'未覆盖平台续查_20261011/第三步收尾/类别命中主代理校核.json'})
    mother.append(m);mx[pid]=m;newly_added.append(pid)
    queue.append({'任务ID':'Y-'+pid,'任务类型':'具名平台年度公告','对象':m['依托机构原称']+'·'+m['平台名称原称'],
        '关联ID':pid,'入口或来源':r['来源URL'],'状态':m['已有核验分类'],'执行动作':m['下一步']})
assert len(mother)==len(before)+len(newly_added)
assert all(old==new for old,new in zip(before,mother) if old['平台ID'] not in inputids)
archive=ROOT/'90_历史归档/02_旧版与输出记录/20261011_第三步收尾前母表';archive.mkdir(exist_ok=True)
for p in (motherpath,queuepath):
    target=archive/p.name;assert not target.exists();shutil.copy2(p,target)
writecsv(OUT/'平台定向补查汇总.csv',final,list(final[0]))
dump(OUT/'查询证据完整性校验.json',evidence_audit)
writecsv(OUT/'重复检索证据缺档说明.csv',missing_audit,['平台ID','原引用缺档','处理'])
writecsv(motherpath,mother,mfields);writecsv(queuepath,queue,qfields)
remaining=[r for r in mother if r['已有核验分类']=='尚未查'];assert not remaining
writecsv(BASE/'剩余未查平台_最新.csv',remaining,mfields)
gaps=[r for r in final if '未取得' in r['证据分类'] or '受阻' in r['证据分类'] or '身份' in r['证据分类']]
writecsv(OUT/'仍未取得窗口任务及身份缺口.csv',gaps,list(final[0]))
assert hashlib.sha256(wb.read_bytes()).hexdigest()==sha
stats={'执行日期':'2026-10-11','原剩余具名平台':414,'逐ID定向查询及保存证据':414,'本轮新增当前受理相关项目':0,
    '本轮新增附带平台名称记录':len(newly_added),'母表条目':len(mother),'现有具名队列尚未执行定向查询':0,
    '本轮逐平台证据状态':dict(Counter(r['证据分类'] for r in final)),'窗口任务身份缺口记录':len(gaps),
    '缺档的重复检索原始文件':len({r['原引用缺档'] for r in missing_audit}),'每条至少一次现存原始检索证据':True,
    '工作簿SHA256':sha,'Excel未修改':True,'第三步现有具名队列及类别检索执行完成':True,
    '全国所有目录与年度穷尽':False,'边界':'目录来源尚未全展开；新年度、批次与清单外平台仍须第四步交叉补漏；未知事实和受阻不因队列执行结束而消失。'}
dump(OUT/'第三步完成校验.json',stats)
print(json.dumps(stats,ensure_ascii=True))
