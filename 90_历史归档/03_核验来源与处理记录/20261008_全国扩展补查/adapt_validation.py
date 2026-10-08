import pathlib
H=pathlib.Path(__file__).resolve().parent;P=H.parent/'20261008_重点地区补查'
s=(P/'finalize_regions.py').read_text(encoding='utf8')
s=s.replace('全国机器人开放课题_个人申报台账_重点地区补查版_20261008.xlsx','全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx')
s=s.replace("w['01申报总览'].max_row==14","w['01申报总览'].max_row==D['stats']['current']+1")
s=s.replace("w['02项目完整详情'].max_row==149","w['02项目完整详情'].max_row==D['stats']['total']+1")
s=s.replace("p['date']>'2026-10-08'","p['date']>='2026-10-09'")
s=s.replace("len(set(listed))==len(listed)==148","len(set(listed))==len(listed)==D['stats']['total']")
start=s.index("for row in B['02项目完整详情'][1:]:")
end=s.index('for s in w:',start)
s=s[:start]+'''prior=load_workbook(D['current_input'],read_only=True,data_only=False)
changed=set(D['national_changes']['updated_ids'])
for row in prior['02项目完整详情'].iter_rows(min_row=2,values_only=True):
 if row[0] in changed:continue
 r=detailmap[row[0]]
 for j,v in enumerate(row,1):assert norm(w['02项目完整详情'].cell(r,j).value)==norm(v),('unchanged prior detail',row[0],j)
assert set(detailmap).issuperset(row[0] for row in B['02项目完整详情'][1:])
assert len(D['excluded'])==D['stats']['excluded']
for p in D['projects']:
 r=detailmap[p['id']]
 for j,v in enumerate(p['details'],1):
  actual=w['02项目完整详情'].cell(r,j).value
  if j==7 and not v:assert actual=='未取得'
  else:assert norm(actual)==norm(v),(p['id'],j)
for g in D['groups']:
 if g is D['groups'][1]:
  for id in g['ids']:
   if pm[id]['date']:assert pm[id]['date']<'2026-10-09',(id,pm[id]['date'])
assert [c.value for c in w['03机构检索覆盖'][6]]==B['03机构检索覆盖'][5]
assert w['04本轮信息核验日志'].max_row==len(D['logs'])+1
prior.close()
''' +s[end:]
s=s.replace("'prior_137_tasks_terms_unchanged_regions_updated':True","'input_150_preserved_except_seven_documented_updates':True")
s=s.replace("'home_six_columns_and_13_formal_open_calls':True","'home_six_columns_and_15_formal_open_calls':True")
s=s.replace("'unique_148_ids_dates_links_filters_freeze_and_order_valid':True","'unique_166_ids_dates_links_filters_freeze_and_order_valid':True")
(H/'finalize_regions.py').write_text(s,encoding='utf8')
r=(P/'render_regions.mjs').read_text(encoding='utf8').replace('全国机器人开放课题_个人申报台账_重点地区补查版_20261008.xlsx','全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx')
r=r.replace("'A8:F14'","'A8:F16'").replace("row('R001')","row('N001')").replace("pr('R005')","pr('N007')")
(H/'render_regions.mjs').write_text(r,encoding='utf8')
