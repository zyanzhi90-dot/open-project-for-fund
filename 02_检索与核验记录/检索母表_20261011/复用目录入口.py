from pathlib import Path
import json,re,csv,hashlib
R=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
found={};evidence={}
def strings(v):
    if isinstance(v,str):return [v]
    if isinstance(v,dict):return [s for x in v.values() for s in strings(x)]
    if isinstance(v,list):return [s for x in v for s in strings(x)]
    return []
for file in ['resume_sources.json','catalog_sources_tail.json','near_sources_tail.json']:
    q=R/'.sync'/file
    if not q.exists():continue
    j=json.loads(q.read_text(encoding='utf8'))
    for kind,records in j.items():
        if not isinstance(records,list):continue
        for idx,r in enumerate(records):
            if not isinstance(r,dict):continue
            for s in strings(r.get('result','')):
                for block in s.split('--------------------------------------------------------------------------------'):
                    first=next((x.strip() for x in block.splitlines() if x.strip()),'')
                    m=re.search(r'^(.*?)\s*\((https?://[^)]+)\)',first)
                    if not m:continue
                    title,url=m.groups()
                    if not re.search('科研平台|科技平台|科研机构|重点实验室.*(?:名单|名录)|(?:名单|名录).*重点实验室|工程.*中心.*(?:名单|名录)|创新平台.*(?:名单|名录)|科研基地|科学研究.*平台',title):continue
                    if re.search('申请|招聘|开放基金|开放课题|申报指南|管理办法|采购|项目立项',title):continue
                    if not re.search(r'\.(?:gov|edu|cas|ac)\.cn',url):continue
                    k='R-'+hashlib.sha256(url.encode()).hexdigest()[:12]
                    if url in found and len(block.strip())<=len(evidence[k]['原结果块']):continue
                    found[url]={'来源ID':k,'目录标题':title,'来源URL':url,'机构或范围原标签':r.get('unit',r.get('phase','')),'地域原标签':r.get('region',''),'原证据定位':f'{file}:{kind}[{idx}]','复用状态':'已有取证结果；须核目录范围，非本轮新增访问','后续动作':'先读取复用目录证据摘录，再提取平台；与现行目录及母表对账，不重复检索'}
                    evidence[k]={'url':url,'title':title,'原结果块':block.strip()}
rows=list(found.values())
if rows:
    with (P/'复用目录入口候选.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'复用目录证据摘录.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')
print('复用官方目录入口候选',len(rows))
