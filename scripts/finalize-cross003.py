"""Archive and consolidate directory-gap search evidence; never edit Excel."""
import csv, hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'02_检索与核验记录/第四步交叉补漏_20261011'
MOTHER=ROOT/'02_检索与核验记录/检索母表_20261011/具名平台母表.csv'

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def write(p,fields,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    assert not (OUT/'本轮校验_003.json').exists(),'Already persisted'
    _,inputs=read(OUT/'目录增量输入_003.csv')
    _,a=read(OUT/'directory003a/平台核查结果.csv')
    _,b=read(OUT/'directory003b/逐平台结果.csv')
    assert len(inputs)==23 and len(a)==12 and len(b)==11
    result={r['平台名称']:r for r in a+b}
    assert set(result)=={r['平台名称'] for r in inputs}
    index=[];raw_files=[];open_count=0
    for directory in ['main003','directory003a','directory003b']:
        for p in (OUT/directory).glob('*.json'):
            obj=json.loads(p.read_text(encoding='utf-8-sig'))
            if directory=='directory003a' and p.name.startswith('query_'):
                qlist=obj['search_query'];raw=p.with_name(p.name.replace('query_','raw_'))
                assert raw.exists();json.loads(raw.read_text(encoding='utf-8-sig'))
                late=p.name!='query_04.json';raw_files.append(str(raw.relative_to(OUT)))
            elif directory=='directory003a': continue
            else:
                assert isinstance(obj,dict) and 'raw_tool_return' in obj
                args=obj.get('query_parameters',obj);qlist=args.get('search_query',args.get('queries',[]));raw=p;late=False
                raw_files.append(str(raw.relative_to(OUT)))
                open_count+=len(args.get('urls',[]))+len(args.get('open',[]))+int('click' in args)
            for q in qlist:
                text=q if isinstance(q,str) else q['q']
                index.append({'分组':directory,'查询':text,'原始响应文件':str(raw.relative_to(OUT)),
                              '参数记录文件':str(p.relative_to(OUT)),'参数即时保存':'否；参数后补，真实返回即时保存' if late else '是'})
    assert len(index)==48 and len(raw_files)==18 and open_count==5,(len(index),len(raw_files),open_count)
    workbook=ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
    sha=hashlib.sha256(workbook.read_bytes()).hexdigest()
    assert sha=='086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    fields,rows=read(MOTHER);before=len(rows);original={r['平台ID']:dict(r) for r in rows}
    names={r['平台名称原称'] for r in rows};assert all(r['平台名称'] not in names for r in inputs)
    _,rootfacts=read(OUT/'main003/主代理候选核查.csv');assert all(r['平台名称'] not in names for r in rootfacts)
    new=[]
    for source in inputs:
        name=source['平台名称'];r=result[name];group='directory003a' if name in {x['平台名称'] for x in a} else 'directory003b'
        evidence='平台核查结果.csv' if group.endswith('a') else '逐平台结果.csv'
        fact=r.get('年度批次及受理窗口',r.get('结果与受理窗口',''))
        gap=r.get('缺口/边界',r.get('具体缺口',''))
        if '辽宁省医疗系统专业' in name:fact+=' 初轮查询单位“沈阳开普”与输入“辽宁开普”不一致；主代理已用目录所载单位补一次纠正查询，未取得该平台当前窗口，结果见main003/开普单位错称纠正查询_08.json；两公司身份不自动归并。'
        row=dict.fromkeys(fields,'');row.update({'平台ID':'P-'+hashlib.sha256((source['依托机构']+'|'+name).encode()).hexdigest()[:12],
          '依托机构原称':source['依托机构'],'平台名称原称':name,'规范身份状态':source['目录性质']+'；当期身份及别名按具体证据，不自动合并',
          '检索顺序依据':'第三步目录底册尚未关联母表名称的明确增量；只作选择线索',
          '已有核验分类':'增量定向检索已执行·当前窗口未取得/部分单位身份待核',
          '已有判断依据':fact+' '+gap,'当期可申报结论':'未知；不把查询未命中判为不存在','年度核验范围':'2026/2027定向查询；既有历史身份目录不证明当期受理',
          '来源URL候选':source['来源URL'],'URL使用限制':'历史目录来源仅复用；首次受阻停止；当期公告未知',
          '原记录位置':'检索母表_20261011/新增官方目录名称底册.csv','原证据行':source['来源定位'],
          '下一步':'保留具体窗口/身份缺口，不重跑本次查询；新来源或新批次再增量核查',
          '20261011定向补查记录':f'第四步交叉补漏_20261011/{group}/{evidence}'})
        new.append(row)
    for r in rootfacts:
        name=r['平台名称'];row=dict.fromkeys(fields,'');row.update({'平台ID':'P-'+hashlib.sha256((r['依托机构']+'|'+name).encode()).hexdigest()[:12],
          '依托机构原称':r['依托机构'],'平台名称原称':name,'规范身份状态':'官方受理公告/官方转发或搜索证据；证据缺口逐条保留',
          '检索顺序依据':'第四步中部与山东近期、新年度及延期交叉查询',
          '已有核验分类':'第四步核验·已截止' if '已截止' in r['窗口结论'] else '第四步核验·窗口或相关任务依据未闭环',
          '已有判断依据':r['窗口结论']+'；'+r['实际任务结论']+'；'+r['本轮处理'],'当期可申报结论':'不计新增当前相关公告',
          '年度核验范围':'2026公告；不把校内递交截止当主办全国截止','来源URL候选':r['来源URL'],
          'URL使用限制':'首次受阻停止；已截止停止补取；没有下载申请模板/咨询邮件',
          '原记录位置':'第四步交叉补漏_20261011/main003/主代理候选核查.csv','原证据行':r['证据文件'],
          '下一步':'保留具体缺口，不重复本批受阻URL或已截止资料；新来源/新批次另核',
          '20261011定向补查记录':'第四步交叉补漏_20261011/main003/'+r['证据文件']})
        new.append(row)
    assert len(new)==28 and len({r['平台ID'] for r in rows+new})==len(rows)+len(new)
    archive=ROOT/'90_历史归档/02_旧版与输出记录/20261011_第四步003前母表';archive.mkdir(parents=True,exist_ok=True)
    assert not (archive/MOTHER.name).exists();shutil.copy2(MOTHER,archive/MOTHER.name)
    write(MOTHER,fields,rows+new)
    write(OUT/'母表新增平台_003.csv',fields,new)
    write(OUT/'查询与证据索引_003.csv',list(index[0]),index)
    _,after=read(MOTHER)
    assert all(r==original[r['平台ID']] for r in after if r['平台ID'] in original)
    _,baseline=read(ROOT/'02_检索与核验记录/审计记录/项目去重基准_20261011.csv')
    _,t030=read(ROOT/'02_检索与核验记录/未覆盖平台续查_20261011/新增正式项目_030.csv')
    _,t002=read(OUT/'新增正式项目_002.csv')
    assert len(baseline)==560 and t030[0]['项目编号']=='T030-001' and t002[0]['项目编号']=='T4-002-001'
    audit={'日期':'2026-10-11','目录底册输入':23,'逐平台结果':23,'搜索查询':47,'真实响应文件':17,'主代理页面打开含点击':5,
      '本轮新增当前相关正式公告':0,'母表修改前':before,'母表修改后':len(after),'原条目保持不变':True,
      '包含Excel外新增去重':True,'Excel未修改':True,'ExcelSHA256':sha,
      '审计偏差':'directory003a前三组12条查询参数后补；真实返回即时保存。漏查1平台已单独补查；单位查询错称另1平台已由主代理用正确目录单位补查，窗口仍未知。directory003b原始JSON多余patch前缀已去除，真实内容保留。',
      '完成范围':'23条候选有检索记录，非全部窗口核验完成；未宣称全部目录或全国完整覆盖',
      '原651队列重跑':False,'全国覆盖完成':False}
    (OUT/'本轮校验_003.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=True))

if __name__=='__main__':main()
