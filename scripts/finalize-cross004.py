"""Persist batch 004 query index and one reviewed existing-window correction."""
import csv, hashlib, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'02_检索与核验记录/第四步交叉补漏_20261011'
MOTHER=ROOT/'02_检索与核验记录/检索母表_20261011/具名平台母表.csv'

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)
def write(p,fields,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    assert not (OUT/'本轮校验_004.json').exists(),'Already persisted'
    index=[];files=[];opens=0
    for directory in ['main004','anhui_fujian004','guangxi_hainan004']:
        for p in (OUT/directory).glob('*.json'):
            o=json.loads(p.read_text(encoding='utf-8-sig'))
            if not isinstance(o,dict) or 'raw_tool_return' not in o:continue
            args=o.get('parameters',o.get('query_parameters',o));qs=args.get('search_query',args.get('queries',[]))
            files.append(str(p.relative_to(OUT)))
            opens+=len(args.get('open',[]))+len(args.get('urls',[]))
            for q in qs:index.append({'分组':directory,'查询':q if isinstance(q,str) else q['q'],'参数及原始返回文件':str(p.relative_to(OUT))})
    assert len(index)==40 and len(files)==21 and opens==6,(len(index),len(files),opens)
    _,baseline=read(ROOT/'02_检索与核验记录/审计记录/项目去重基准_20261011.csv')
    _,external=read(ROOT/'02_检索与核验记录/未覆盖平台续查_20261011/新增正式项目_030.csv')
    _,external2=read(OUT/'新增正式项目_002.csv')
    assert len(baseline)==560 and external[0]['项目编号']=='T030-001' and external2[0]['项目编号']=='T4-002-001'
    sha=hashlib.sha256((ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx').read_bytes()).hexdigest()
    assert sha=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    fields,rows=read(MOTHER);before={r['平台ID']:dict(r) for r in rows};changes=[]
    for r in rows:
        if r['已有项目编号']!='N098':continue
        fact='2026-10-11第四步004：官方域名同9306.htm搜索正文明确当期申请截止2026-09-30，已截止。只复用本次实际返回，未重试原受阻正文、未补历史任务及条款。'
        changes.append({'平台ID':r['平台ID'],'项目编号':'N098','原分类':r['已有核验分类'],'本轮分类':'第四步复用官方搜索正文·当期已截止','事实':fact,'证据':'main004/核心高校与业务费_01.json'})
        r['已有核验分类']='第四步复用官方搜索正文·当期已截止'
        r['已有判断依据']+='\n'+fact
        r['当期可申报结论']='2026批次已截止；不补取历史资料'
        r['年度核验范围']+='\n2026年度；截止2026-09-30'
        r['20261011定向补查记录']+='\n第四步交叉补漏_20261011/main004/核心高校与业务费_01.json'
        r['下一步']='已截止停止补取；原受阻URL不重试；只有新来源/新年度批次再增量核查，不下载申报模板或补结题。'
    assert len(changes)==1
    archive=ROOT/'90_历史归档/02_旧版与输出记录/20261011_第四步004前母表';archive.mkdir(parents=True,exist_ok=True)
    assert not (archive/MOTHER.name).exists();shutil.copy2(MOTHER,archive/MOTHER.name)
    write(MOTHER,fields,rows);write(OUT/'母表增量变化_004.csv',list(changes[0]),changes)
    write(OUT/'查询与证据索引_004.csv',list(index[0]),index)
    _,after=read(MOTHER)
    assert len(after)==1304 and [r['已有项目编号'] for r in after if r!=before[r['平台ID']]]==['N098']
    audit={'日期':'2026-10-11','差异查询':40,'真实响应文件':21,'页面打开':6,'新增当前相关正式公告':0,
      '母表条目':len(after),'修改既有条目':['N098'],'旧母表已归档':True,'Excel未修改':True,'ExcelSHA256':sha,
      '去重含560行基准及Excel外新增':['T030-001','T4-002-001'],'原651队列未重跑':True,'全国覆盖完成':False,
      '边界':'安徽福建广西海南地区及核心入口的局部差异检索；未知窗口/任务不能判无项目，滚动续资助不能判持续新受理。',
      '执行偏差':'安徽福建子批不必要打开了基准已明确截止的M102、M088、M137、M061正文；未取得新批次，保留真实返回及纠正说明，不算新增覆盖；后续使用URL打开前基准检查。'}
    (OUT/'本轮校验_004.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=True))
if __name__=='__main__':main()
