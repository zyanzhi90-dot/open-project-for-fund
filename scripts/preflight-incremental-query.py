"""Read-only guard: repeat queries / already-queried platform scopes need explicit new evidence."""
import argparse,csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def normalize(s):return re.sub(r'\s+','',s).lower()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--query',required=True)
    ap.add_argument('--platform-id')
    ap.add_argument('--new-evidence',help='具体新公告/新年度批次/新来源URL；不能只写“继续补查”')
    a=ap.parse_args();hits=[]
    out=ROOT/'02_检索与核验记录/第四步交叉补漏_20261011'
    for p in out.glob('查询与证据索引_*.csv'):
        for r in rows(p):
            if normalize(r.get('查询',''))==normalize(a.query):
                hits.append({'index':str(p.relative_to(ROOT)),'query':r['查询']})
    mother=rows(ROOT/'02_检索与核验记录/检索母表_20261011/具名平台母表.csv')
    platform=next((r for r in mother if r['平台ID']==a.platform_id),None)
    if a.platform_id and platform is None:
        action='unknown_platform_id_check_identity'
    elif hits:
        action='exact_query_reuse_do_not_repeat'
    elif platform and not a.new_evidence:
        action='existing_platform_require_specific_new_scope_or_evidence'
    else:
        action='new_increment_candidate_check_url_baseline_and_first_blocked_links'
    print(json.dumps({'action':action,'query':a.query,'platform_id':a.platform_id,
        'existing_status':platform.get('已有核验分类') if platform else None,'new_evidence':a.new_evidence,
        'exact_query_hits':hits,'limit':'前检不是相关性判定或全国覆盖证明；新来源应具体且主代理复核，不能绕过首次受阻停止规则。'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
