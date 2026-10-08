import pathlib
H=pathlib.Path(__file__).parent;old=H.parent/'20261008_严格重筛'
s=(old/'build_strict.mjs').read_text(encoding='utf8').replace('prepared_strict.json','prepared_regions.json').replace('authored_strict.xlsx','authored_regions.xlsx')
a=s.index("base('90筛选前原始记录'");b=s.index('wb.recalculate();',a)
s=s[:a]+"base('90筛选前原始记录',d.archive_rows,1,Array(d.archive_rows[0].length).fill(190),'Original199',80,false);\nbase('91输入版本留档',d.prior_rows,1,[210,100,400,400,400,400],'PriorInputRows',65,false);\n"+s[b:]
s=s.replace("range:'A1:F13'","range:'A1:F14'")
(H/'build_regions.mjs').write_text(s,encoding='utf8')
s=(old/'finalize_strict.py').read_text(encoding='utf8');s=s[:s.index("assert hashlib.sha256")]
s=s.replace('prepared_strict.json','prepared_regions.json').replace('authored_strict.xlsx','authored_regions.xlsx').replace('全国机器人开放课题_个人申报台账_严格重筛版_20261008.xlsx','全国机器人开放课题_个人申报台账_重点地区补查版_20261008.xlsx')
s+='''
assert hashlib.sha256(pathlib.Path(D['current_input']).read_bytes()).hexdigest()==D['current_input_hash']
w=load_workbook(out,data_only=False);B=json.loads((H/'base_rows.json').read_text(encoding='utf8'))
assert [c.value for c in w['01申报总览'][1]]==['申报状态','截止日期','依托单位·实验室','公告研究方向','资助金额','公告']
assert w['01申报总览'].max_column==6 and w['01申报总览'].max_row==14
assert w['01申报总览'].freeze_panes=='A2' and w['02项目完整详情'].freeze_panes=='E2'
assert w['02项目完整详情'].max_row==149
listed=[]
for name,rows in D['list_maps'].items():
 s=w[name];assert len(s.tables)==1 and s.max_row==len(rows)+1
 for x in rows:
  p=pm[x['id']];r=x['row'];listed.append(p['id']);assert s.cell(r,1).value==p['status']
  assert s.cell(r,3).hyperlink.location==f"'02项目完整详情'!A{detailmap[p['id']]}";assert s.cell(r,6).hyperlink.target==p['url']
  if p['date']:assert s.cell(r,2).value.strftime('%Y-%m-%d')==p['date']
  if name=='01申报总览':assert p['date']>'2026-10-08' and p['kind']=='正式开放课题公告'
assert len(set(listed))==len(listed)==148
norm=lambda v: '' if v is None else (v.strftime('%Y-%m-%d') if hasattr(v,'strftime') else (v[:10] if isinstance(v,str) and 'T00:00:00' in v else v))
for name in ['90筛选前原始记录','91输入版本留档']:
 s=w[name];assert s.sheet_state=='hidden' and s.max_row==len(B[name])
 for i,row in enumerate(B[name],1):
  for j,v in enumerate(row,1):assert norm(s.cell(i,j).value)==norm(v),(name,i,j)
for row in B['02项目完整详情'][1:]:
 r=detailmap[row[0]]
 for j,v in enumerate(row,1):
  if j!=25:assert norm(w['02项目完整详情'].cell(r,j).value)==norm(v),('prior detail',row[0],j)
assert len(D['excluded'])==61
for s in w:
 for row in s:
  for c in row:assert c.data_type!='e',(s.title,c.coordinate)
for group in D['groups']:
 ranks=['P0 南京及周边','P0 澳门','P0 香港','P0 广州及周边','P1 北京及周边','P1 西安及周边','P1 重庆']
 keys=[(ranks.index(pm[i]['region']) if pm[i]['region'] in ranks else 7,pm[i]['date'] or '9999-99-99',pm[i]['org'],i) for i in group['ids']];assert keys==sorted(keys)
report={'output':str(out),'stats':D['stats'],'input_sha256_unchanged':True,'prior_137_tasks_terms_unchanged_regions_updated':True,'original_199_and_hidden_archives_unchanged':True,'home_six_columns_and_13_formal_open_calls':True,'unique_148_ids_dates_links_filters_freeze_and_order_valid':True,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'visual_review':'pending'}
(H/'validation_regions.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
'''
(H/'finalize_regions.py').write_text(s,encoding='utf8')
