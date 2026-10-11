"""Persist batch 002 reviewed facts without editing the workbook."""
import csv, hashlib, json, shutil
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '02_检索与核验记录/第四步交叉补漏_20261011'
MOTHER = ROOT / '02_检索与核验记录/检索母表_20261011/具名平台母表.csv'
URL = 'https://10.cetc.com.cn/10/338217/338193/2128632/index.html'

def read_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)

def write_csv(p, fields, rows):
    with p.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

def main():
    if (OUT/'本轮校验_002.json').exists():
        raise SystemExit('Batch 002 already persisted.')
    baseline_fields, baseline = read_csv(ROOT/'02_检索与核验记录/审计记录/项目去重基准_20261011.csv')
    _, external = read_csv(ROOT/'02_检索与核验记录/未覆盖平台续查_20261011/新增正式项目_030.csv')
    assert len(baseline) == 560 and any(r['项目编号']=='T030-001' for r in external)
    names = ['信息智能获取与处理学科与技术中心', '智能测控与天基信息应用四川省重点实验室', '敏捷智能计算四川省重点实验室']
    keys = ['中电天奥', '2128632'] + names
    assert not any(any(k in str(r) for k in keys) for r in baseline + external)
    fields, rows = read_csv(MOTHER)
    assert not any(r['平台名称原称'] in names for r in rows)
    before = len(rows)
    archive = ROOT/'90_历史归档/02_旧版与输出记录/20261011_第四步002前母表'
    archive.mkdir(parents=True, exist_ok=True)
    assert not (archive/MOTHER.name).exists()
    shutil.copy2(MOTHER, archive/MOTHER.name)
    changes = []
    for i, name in enumerate(names, 1):
        related = i == 2
        fact = ('2026开放基金，截止2026-10-20；官方任务图明确面向天基测控通信无人机的灵巧干扰生成与感知博弈、测控地面站任务解析与流程自主技术、卫星前向散射空中目标运动参数测量；每项不高于20万元。保留天基测控与电磁应用边界。'
                if related else '2026开放基金，截止2026-10-20；官方任务图已取得。方向为电磁信号处理/模型协同或电磁环境中的检测识别、参数估计等；当前图片未充分明确机器人或相关智能装备实际对象，不因智能泛词将本专题列为新增相关项目。')
        row = dict.fromkeys(fields, '')
        row.update({'平台ID':'P-'+hashlib.sha256(name.encode()).hexdigest()[:12],
            '依托机构原称':'中电天奥有限公司', '平台名称原称':name,
            '规范身份状态':'官方2026实验室专题公告明确平台名称；不推定与相似平台合并',
            '检索顺序依据':'第四步近期公告及企业/省级平台类别交叉补漏',
            '已有核验分类':'第四步核验·当前正式受理且任务相关' if related else '第四步核验·窗口成立/任务图片未充分明确相关装备对象',
            '已有判断依据':fact, '当期可申报结论':'当前相关正式公告；个人资格另核' if related else '仅保留专题事实；不计新增相关项目',
            '年度核验范围':'2026年度中电天奥创新理论技术群基金（实验室专题）；2026-09-18发布',
            '已有项目编号':'T4-002-001' if related else '', '来源URL候选':URL,
            'URL使用限制':'公告正文及任务图片一次取得；未扫码、未下载申报模板',
            '原记录位置':'第四步交叉补漏_20261011/main002',
            '原证据行':f'中电天奥公告正文摘录.txt；中电天奥任务{i}.png',
            '下一步':'本批次证据保留，不重复补取；经费外拨未载，不将研究经费上限当个人现金额度',
            '20261011定向补查记录':f'第四步交叉补漏_20261011/main002/中电天奥任务{i}.png'})
        rows.append(row)
        changes.append({'平台ID':row['平台ID'],'项目编号':row['已有项目编号'],'变化':'新增具名专题平台','事实':fact})
    for row in rows:
        if row.get('已有项目编号') != 'M074': continue
        fact = '第四步002：2026-01-17转载称基础创新类全年开放、2月15日为第一批集中受理；尚缺对应官方原公告佐证全年机制，官方立项通知不补足此缺口。不升级当前受理结论，不将集中批次日期直接作为全年截止。'
        row['已有判断依据'] += '\n'+fact
        row['20261011定向补查记录'] += '\n第四步交叉补漏_20261011/main002/新窗口来源检索原始返回_04.json'
        changes.append({'平台ID':row['平台ID'],'项目编号':'M074','变化':'附加转载滚动线索及官方证据缺口','事实':fact})
    write_csv(MOTHER, fields, rows)
    write_csv(OUT/'母表增量变化_002.csv', list(changes[0]), changes)
    new = {'项目编号':'T4-002-001','平台名称':names[1], '依托单位':'中电天奥有限公司',
        '年度批次':'2026创新理论技术群基金（实验室专题）共享公告', '公告日期':'2026-09-18',
        '受理截止':'2026-10-20','截止时刻':'正文未载',
        '实际相关任务':'面向天基测控通信无人机的灵巧干扰生成与感知博弈；测控地面站任务解析与流程自主技术；卫星前向散射空中目标运动参数测量。保留天基测控场景。',
        '明示金额':'专题02各方向研究经费不高于20万元；外拨及具体获资助额度未载，不是个人现金额度承诺',
        '关键申请条件':'中国国籍，高校教师或科研机构及企事业单位正式员工，博士学历或副高以上；同批次只能申请1项，承担本实验室未结题课题者不能申报；只支持一家单位，不支持联合申报；材料公开不涉密，须本单位保密审查证明',
        '来源URL':URL, '任务证据':'main002/中电天奥任务2.png', '核验日期':'2026-10-11',
        '去重结果':'560行基准及Excel外新增T030-001无同平台、来源、年度批次命中；共享公告只计1项，不将方向数当项目数',
        '缺口':'公告未载具体截止时刻、经费外拨口径；二维码所链接指南细则未展开。个人条件后续判断；不补结题条款。'}
    write_csv(OUT/'新增正式项目_002.csv', list(new), [new])
    parser = TextParser(); parser.feed((ROOT/'.sync/cross002-cache/cetc2128632.html').read_text(encoding='utf-8'))
    text = '\n'.join(parser.parts)
    begin = text.index('发布时间：2026年09月18日'); end = text.index('编审 |', begin)
    (OUT/'main002/中电天奥公告正文摘录.txt').write_text(text[begin:end], encoding='utf-8')
    queries = []; raw_count = 0; opens = 0
    for directory in ['main002','north002','west002','southwest002']:
        for f in (OUT/directory).glob('*.json'):
            obj = json.loads(f.read_text(encoding='utf-8-sig'))
            if not isinstance(obj, dict) or not any(k in obj for k in ['raw_tool_return','returned','result']): continue
            raw_count += 1
            for q in obj.get('queries', []):
                if (isinstance(q,str) and not q.startswith(('https://','http://'))) or (isinstance(q,dict) and 'q' in q):
                    queries.append({'分组':directory,'查询':q if isinstance(q,str) else q['q'],'原始返回文件':str(f.relative_to(OUT))})
                else: opens += 1
            opens += len(obj.get('urls', []))
    assert len(queries) == 59 and opens == 12
    write_csv(OUT/'查询与证据索引_002.csv', list(queries[0]), queries)
    workbook = ROOT/'全国机器人开放课题_个人申报台账_检索补充版_20261010.xlsx'
    sha = hashlib.sha256(workbook.read_bytes()).hexdigest()
    assert sha == '086c51eb7e89e802e41bef3790c84d7638d6632f78c31c50022caab79cf55a46'
    audit = {'日期':'2026-10-11','查询数':len(queries),'原始工具响应文件':raw_count,'定向页面打开':opens,
        '母表修改前':before,'母表修改后':len(rows),'新增当前相关共享公告':1,'新增平台名称':3,
        '去重基准行数':len(baseline),'包含Excel外T030-001':True,'Excel未修改':True,'ExcelSHA256':sha,
        '全国覆盖完成':False,'地区': ['河北','天津','内蒙古','吉林','黑龙江','甘肃','宁夏','青海','新疆含兵团','西藏','江西','贵州','云南'],
        '剩余范围':'各地机构及平台目录未逐项展开；M074全年转载缺官方原公告；吉林及包头新URL窗口批次关系首次受阻，不重试。'}
    (OUT/'本轮校验_002.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=True))

if __name__ == '__main__': main()
