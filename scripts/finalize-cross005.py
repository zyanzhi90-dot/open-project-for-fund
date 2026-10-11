"""Persist reviewed partial Shanghai/Jiangsu directory increment, with evidence gaps explicit."""
import csv, hashlib, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'02_检索与核验记录/第四步交叉补漏_20261011'
BASE=ROOT/'02_检索与核验记录/检索母表_20261011'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)
def write(p,fields,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'本轮校验_005.json').exists(),'Already persisted'
    fields,rows=read(BASE/'具名平台母表.csv');before={r['平台ID']:dict(r) for r in rows}
    dfields,dirs=read(BASE/'新增官方目录名称底册.csv')
    sfields,sources=read(BASE/'全国目录来源母表.csv')
    qfields,queue=read(BASE/'后续执行队列.csv')
    assert len(rows)==1304 and len(dirs)==2634
    excel=ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
    assert digest(excel)=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    _,baseline=read(ROOT/'02_检索与核验记录/审计记录/项目去重基准_20261011.csv')
    _,ex1=read(ROOT/'02_检索与核验记录/未覆盖平台续查_20261011/新增正式项目_030.csv')
    _,ex2=read(OUT/'新增正式项目_002.csv')
    assert len(baseline)==560 and ex1[0]['项目编号']=='T030-001' and ex2[0]['项目编号']=='T4-002-001'
    index=[];raw_files=[];raw_opens=0
    for group in ['main005','shanghai005','jiangsu005']:
        for p in sorted((OUT/group).glob('*.json')):
            o=json.loads(p.read_text(encoding='utf-8-sig'))
            if 'raw_tool_return' not in o and 'returned' not in o:continue
            args=o.get('parameters',o.get('query_parameters',o))
            raw_files.append(str(p.relative_to(OUT)))
            raw_opens+=len(args.get('open',[]))+len(args.get('click',[]))
            for q in args.get('search_query',args.get('queries',[])):
                index.append({'分组':group,'查询':q if isinstance(q,str) else q['q'],'证据文件':str(p.relative_to(OUT)),'证据状态':'查询参数及真实原始返回；定位01仅保存查询字符串'})
    js=json.loads((OUT/'jiangsu005/jiangsu005_证据包.json').read_text(encoding='utf-8-sig'))
    for c in js['web_calls']:
        assert 'raw_return' not in c and 'summary_not_raw' in c
        for q in c.get('queries',[]):
            index.append({'分组':'jiangsu005','查询':q,'证据文件':'jiangsu005/jiangsu005_证据包.json','证据状态':'子代理报告参数与摘要；完整真实返回缺档，不作充分覆盖证明'})
    assert len(raw_files)==12 and len(index)==42 and raw_opens==2,(len(raw_files),len(index),raw_opens)
    new=[];changed=[];newdir=[]
    def add(name,unit,url,status,fact,scope,location,identity='官方正文平台/公告名称；不凭相似名称归并'):
        assert not any(r['平台名称原称']==name and r['依托机构原称']==unit for r in rows)
        pid='P-'+hashlib.sha256((unit+'|'+name).encode()).hexdigest()[:12]
        assert pid not in {r['平台ID'] for r in rows}
        oldunit=next((r['机构ID'] for r in rows if r['依托机构原称']==unit),None)
        r={f:'' for f in fields}
        r.update({'平台ID':pid,'机构ID':oldunit or 'I-'+hashlib.sha256(unit.encode()).hexdigest()[:12],
          '依托机构原称':unit,'平台名称原称':name,'规范身份状态':identity,'检索顺序依据':'005目录增量或当期新公告线索；名称不判任务相关性',
          '已有核验分类':status,'已有判断依据':fact,'当期可申报结论':'不作个人可申报判定；'+status,
          '年度核验范围':scope,'来源URL候选':url,'URL使用限制':'已截止停止补取；首次受阻不重试；筹建/转载摘要不证明正式受理',
          '原记录位置':location,'下一步':'只在新年度/批次/来源证据或明确目录缺口下增量核查；不重扫旧队列，不下载申请表、邮件咨询或补结题',
          '别名及重组处理':'筹建与现行运行身份分开；共同依托不冒充独立平台',
          '20261011定向补查记录':location})
        rows.append(r);new.append(r)
    _,sh=read(OUT/'shanghai005/候选对账.csv')
    assert len(sh)==10
    pdf='https://stcsm.sh.gov.cn/cmsres/ef/ef6b458ee2a44514b6e303cbef9f66fe/618ac5a44cb7950d9593e10caa41c2f3.pdf'
    for i,a in enumerate(sh,1):
        d={f:'' for f in dfields};d.update({'目录来源':'上海2025高水平机构重点实验室筹建立项专项名单','目录年度':'2025','地域':'上海','序号':str(i),
         '平台类别':'市重点实验室（筹）','平台名称':a['平台'],'依托机构':a['单位'],'来源URL':pdf,'来源定位':f'官方附件序号{i}；shanghai005/查询证据_01.json完整返回',
         '目录性质':'仅该专项批次10家筹建身份；非上海全量或正式运行证明','取证日期':'2026-10-11','执行分组':'005目录增量',
         '来源核验限制':'附件名称来自完整搜索真实返回；未另行下载；当前窗口及任务未核清'})
        dirs.append(d);newdir.append(d)
        core=a['平台'].replace('上海市','').replace('重点实验室（筹）','')
        hits=[r for r in rows if core in r['平台名称原称']]
        if hits:
            assert len(hits)==1 and core=='多模态具身智能'
            r=hits[0];r['已有判断依据']+='\n005复用官方专项名单：复旦大学、上海电气自动化集团有限公司共同筹建；名单身份不能证明当期开放窗口。'
            r['20261011定向补查记录']+='\n第四步交叉补漏_20261011/shanghai005/查询证据_01.json'
            changed.append(r['平台ID']);continue
        add(a['平台'],a['单位'],pdf,'新筹建目录平台·窗口未取得',
            '官方专项名单列入筹建；005原始窗口查询未取得当期开放公告；不据名称判无关。',
            '2026窗口查询；原子/铸锻/光计算等子批另含2027；不声称年度穷尽',
            '第四步交叉补漏_20261011/shanghai005/候选对账.csv；main005/上海目录未查名称窗口_04.json；main005/新增筹建平台窗口_05.json',
            '上海市2025专项重点实验室（筹）；非已认定或运行证明')
    _,jsc=read(OUT/'jiangsu005/江苏目录增量D-P10_平台候选.csv')
    assert len(jsc)==2
    for a in jsc:
        add(a['平台名称'],a['依托/牵头单位'],a['目录来源'],'筹建报道线索·原始证据缺档·窗口未知',
            '子代理官方报道摘要记载筹建名称及合作单位：'+a['合作单位']+'；完整真实返回未落盘，身份事实尚待主代理有原始来源时核实。主代理005首次新窗口查询未取得公告。',
            '主代理2026新增名称窗口定向查询；原始返回main005/新增筹建平台窗口_05.json',
            '第四步交叉补漏_20261011/jiangsu005/江苏目录增量D-P10_平台候选.csv；jiangsu005/jiangsu005_证据包.json；main005/新增筹建平台窗口_05.json',
            '子代理报道摘要中的筹建候选；缺完整真实返回，不作官方身份已核清证明')
    add('化工过程强化山西省重点实验室','中北大学','https://www.nuc.edu.cn/info/1014/62373.htm','窗口成立·公开任务未见相关装备依据',
      '2026-09-23发布，2026-10-12截止。实际方向为化工过程强化新装置、流动传热传质、超重力污染物控制、电化学强化及功能材料；未有明确机器人或相关智能装备任务依据，停止后续字段补取。',
      '2026年度公告','第四步交叉补漏_20261011/main005/中北化工过程强化首次正文_02.json')
    add('云南省高原温泉医康养重点实验室','昆明医科大学','https://www.kmmc.cn/Pages_188_60744.aspx','2026公告已截止·停止补取',
      '官方搜索正文明确2026-08-15截止，已过期。不补历史任务、金额或申请条款。','2026年度公告',
      '第四步交叉补漏_20261011/main005/行业窗口交叉_03.json')
    add('汽车标准化公益性开放课题','全国汽车标准化技术委员会／中国汽车技术研究中心有限公司','https://www.catarc.org.cn/xwdt/hytz/850881198276677.html','2026公告已截止·停止补取',
      '官方搜索正文明确2026-09-30前提交，已截止；不因涉及具身装卸装置而展开历史任务列表或资助条款。','2026年度公告',
      '第四步交叉补漏_20261011/main005/行业窗口交叉_03.json')
    add('肿瘤早期筛查与智能诊疗体系构建科研资助项目','广东省钟南山医学基金会','https://www.znsmf.org/news/1945.html','公告窗口至11月13日或满额提前结束·任务依据不足',
      '公开方向为肿瘤早筛标志物、人工智能辅助诊断、智能诊疗体系和临床研究，未明确机器人/相关智能装备任务。公告期限2026-11-13 24:00，累计资助达到上限会提前结束；当前满额状态未核。非个人申报推荐。',
      '2026—2028专项公告','第四步交叉补漏_20261011/main005/行业窗口交叉_03.json')
    tea=next(r for r in rows if r['平台ID']=='P-cac0c651fdb2')
    tea['已有核验分类']='新当期转载线索·官方窗口未核实·首次正文受阻'
    tea['已有判断依据']+='\n005：泛研网2026-10-09转载题为2026开放基金指南，页面标示至10月15日，摘录茶叶种植智慧感知与分析、茶机械智能化；未取得官方原公告，转载正文首次不可访问即停止，不能升级正式受理。'
    tea['来源URL候选']+='\nhttps://www.funresearch.cn/grant/ZDBkZWQyM2YtM2JjYS00MDNkLTlhMTItYzZiNGIzZDM5MmI5'
    tea['年度核验范围']+='\n005新当期转载来源线索；主办截止、明确任务、明示金额仍缺'
    tea['当期可申报结论']='官方当期受理未核实；仅保留转载线索，非新增正式项目'
    tea['20261011定向补查记录']+='\n第四步交叉补漏_20261011/main005/茶产业当期新线索官方定位_06.json；茶产业官方域名纠正_07.json；茶产业转载首次正文_08.json'
    tea['下一步']='受阻转载不重试；没有新原始官方来源前留缺，不反复搜索同窗口。'
    changed.append(tea['平台ID'])
    assert len(new)==15 and len(rows)==1319 and len(dirs)==2644
    for r in sources:
        if r['目录ID']=='D-P09':
            r['目录状态']='005部分展开：2025市重点实验室筹建专项10家；非全市目录'
            r['入口依据']+='\n005官方附件：'+pdf
            r['当前公告完成状态']='专项10名称窗口查询留证；未取得新正式相关公告；不能代表上海全部机构或类别'
            r['下一步']='补其他专项/年度及高校、工程中心目录；新名称先对账。筹建身份与实际运行、开放窗口分开；既有平台同范围不重复查询。'
        if r['目录ID']=='D-P10':
            r['目录状态']='005目录定位已执行：报道摘要称39家企业筹建；完整名单未取得；摘要原始返回缺档'
            r['当前公告完成状态']='2条新筹建候选主代理已查2026窗口，未取得公告；身份摘要待原始来源核实'
            r['下一步']='继续完整企业筹建名单、高校实验室、工程中心目录增量；已有受阻及相同查询不重复；未列出的名称不推测。'
    for r in queue:
        if r['任务ID']=='D-P09':r['状态']='005局部名单10家已展开并对账；上海全目录未完成'
        if r['任务ID']=='D-P10':r['状态']='005定位报道摘要及2具名候选；全名册未取得，原始返回缺档'
    archive=ROOT/'90_历史归档/02_旧版与输出记录/20261011_第四步005前母表'
    archive.mkdir(parents=True,exist_ok=True)
    for name in ['具名平台母表.csv','新增官方目录名称底册.csv','全国目录来源母表.csv','后续执行队列.csv']:
        assert not (archive/name).exists();shutil.copy2(BASE/name,archive/name)
    write(BASE/'具名平台母表.csv',fields,rows);write(BASE/'新增官方目录名称底册.csv',dfields,dirs)
    write(BASE/'全国目录来源母表.csv',sfields,sources);write(BASE/'后续执行队列.csv',qfields,queue)
    write(OUT/'母表新增平台_005.csv',fields,new);write(OUT/'新增目录身份_005.csv',dfields,newdir)
    write(OUT/'查询与证据索引_005.csv',list(index[0]),index)
    after=read(BASE/'具名平台母表.csv')[1]
    assert {r['平台ID'] for r in after if r['平台ID'] in before and r!=before[r['平台ID']]}==set(changed)
    assert digest(excel)=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    audit={'日期':'2026-10-11','查询总数含子代理报告':42,'完整真实返回对应查询':34,'仅摘要参数对应查询':8,'完整原始文件':12,
      '有完整返回页面打开':2,'子代理报告另打开':1,'缺档调用数':3,'母表':1319,'新增平台及线索':15,'目录底册':2644,
      '新增官方专项名单身份':10,'新增当前相关正式项目':0,'修改既有ID':changed,'ExcelSHA256':digest(excel),'旧版归档':str(archive.relative_to(ROOT)),
      '去重包含':['560行基准','T030-001','T4-002-001'],'全国完成':False,
      '偏差':'上海12查询超10上限，交大同平台同范围重复查询不计新覆盖；江苏3调用完整返回缺档已改为摘要，不能作充分覆盖证明；主代理06文件site.操作符误写已在07纠正。'}
    (OUT/'本轮校验_005.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=True))
if __name__=='__main__':main()
