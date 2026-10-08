import pathlib,json,re,collections
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];D=json.loads((H/'prepared_regions.json').read_text(encoding='utf8'));old=json.loads((H.parent/'20261008_重点地区补查/institutions.json').read_text(encoding='utf8'))
D['coverage']=json.loads((H/'base_rows.json').read_text(encoding='utf8'))['03机构检索覆盖']
records=[]
# Each line names actually discovered official scope; notices already in the ledger are reused.
spec='''江苏|南京信息工程大学|认知计算及智能信息处理平台定向检索|https://www.nuist.edu.cn/kxyj/sbjkypt.htm|M185|复用前轮平台目录；本轮未取得其他平台2026—2027指南
江苏|东南大学|精准医学装备设计制造省重点实验室；移动通信全国重点实验室2027|https://me.seu.edu.cn/2022/0406/c29672a403829/page.htm|E064|前者平台介绍已发现，开放机制未取得；后者正式指南任务为通信，排除
江苏|南京理工大学|高维信息智能感知及自动化实验室定向检索|https://automation.njust.edu.cn/|既有记录复用|年度正式开放任务与可用附件仍缺；域名只作定向入口，不代表目录全核
江苏|扬州大学|机械与信息学院机器人平台发现检索|https://xxgcxy.yzu.edu.cn/__local/0/19/73/0FD2722FFF24F611B51471E36E0_7ADC075C_457E8.pdf|无新增|取得竞赛校内通知，不能当开放基金；独立相关平台目录仍待补
澳门|澳门大学|CAIR机器人研究及IoT2026—2027开放管理文件|https://skliotsc.um.edu.mo/wp-content/uploads/2025/08/IOTSC-Management-Methods-for-ORP-2026-2027.pdf|M165|管理PDF403，官方索引片段不代替全文；CAIR2026招聘不是开放基金；各中心独立外部机制仍缺
香港|香港理工大学|机器人公开研究资助交叉检索；气候韧性沿海城市实验室基金页|https://www.polyu.edu.hk/sklcrcc/research/funding-support/|M122复用|新基金页任务为气候韧性沿海城市，未见具体机器人任务，不入机器人台账；无人系统及联合实验室机制仍缺
广东|光明实验室|2026首轮正式公告及申请模板；第二批去重|https://www.gml.ac.cn/xxgs/923.html|R006、M097|首轮正文与模板已取得，金额/截止/成果补齐；经费科目和外拨管理办法仍缺
广东|华南理工大学|自主系统网络控制、机器人相关年度及附件交叉检索|https://www2.scut.edu.cn/autonlab/2025/0411/c4447a585385/page.htm|R005|复用已取得通知；挂载指南年度不一致，另一官方渠道仍未获适用任务指南
北京|清华大学|信息国家研究中心2026类脑物理智能体；指南与立项结果|https://www.bnrist.tsinghua.edu.cn/info/1110/4271.htm|N001|年度指南PDF已取得；机器人方向6外拨、权属和署名未载；其他群体不能视作全核
北京|中国科学院自动化研究所|多模态人工智能系统全国重点实验室2026；机器人/CAIR官方动态|https://www.ia.cas.cn/qtgn/tzgg/202605/t20260515_8202627.html|M009复用|新命中与已存年度公告去重；院内其他独立平台、2027外部机制尚缺
陕西|西北工业大学|智能机器人增材制造团队目录；空天地海2027—2028；凝固2026|https://soai.nwpu.edu.cn/szdw/jsfc.htm|既有记录复用|团队新闻不是申报；空天地海/凝固任务未因智能建模自动保留，其他机器人重点平台年度机制仍缺
重庆|重庆城市职业学院|工业机器人运维工程中心2026正式公告索引|https://kyc.cqcvc.edu.cn/info.thtml?cid=74479&pn=&t=11322|M103|已在台账，不重增；页面直接访问超时，指南和共建单位资格适用范围按原缺口手动核
重庆|重庆邮电大学|工业物联网网络化控制2025首页线索|https://iot.cqupt.edu.cn/|R009|再次发现索引，主页访问失败；未取得具体年度正文与附件，停止无效尝试
重庆|重庆大学|高端装备机械传动2026原始通知|https://slmt.cqu.edu.cn/info/10663/90052.htm|R008|其他官方渠道仅个人获资助记录，不能代替年度指南；原正文任务和条件仍缺
河北|燕山大学|机械学院科研平台；并联机器人与机电系统；电气机器人控制|https://mec.ysu.edu.cn/yqgl/jgsz/kypt.htm|无新增|目录/平台官方证据已发现；2026—2027各实验室正式外部申报公告未取得
河北|河北科技大学|河北省机器人与具身智能重点实验室；机器人与智能装备交叉中心|https://news.hebust.edu.cn/zhxw/fcbadd9f703c4145b6255f79651d3226.htm|无新增|2026-09-24官方获批平台新闻确认，不是基金；年度外部资助机制未取得
天津|南开大学|科研平台目录；天津市智能机器人技术实验室及微纳操作/无人系统团队|https://std.nankai.edu.cn/37461/list.htm|无新增|目录已读，年度定向结果主要为外单位已获基金及研究简介；独立开放受理未取得
天津|天津大学|水利工程智能建设运维全国重点实验室2026|https://www.tju.edu.cn/info/4732/81752.htm|N016|完整正文已核异质装备群协同及无人装备方向；指南PDF验证码，不能套M017精密测试实验室；其他机械/医工平台完整目录尚缺
山西|中北大学|机器视觉虚拟现实2026、微纳2026、恶劣环境智能装备2023、智能探测2026|https://www.nuc.edu.cn/info/1014/62433.htm|M068、M043、M106、N005|三个10月8日截止项目转历史；智能探测沿用已存完整任务与条款，不因本轮取不到后段倒退；其他平台2027未全核
内蒙古|内蒙古工业大学|自治区机器人与智能装备重点实验室重组平台；机械学院|https://jixiexy.imut.edu.cn/info/1107/5834.htm|无新增|2024重组平台介绍已发现，2026—2027机器人实验室正式开放指南未取得
内蒙古|内蒙古科技大学|机械工程学院机器人感知/认知/执行研究线索|https://sme.imust.edu.cn/info/1092/5973.htm|无新增|人员研究不是开放基金；相关重点实验室完整名单及外部受理机制未取得
辽宁|中国科学院沈阳自动化研究所|机器人与智能系统全国重点实验室目录、2025指南、2026—2027定向|https://rlab.sia.cas.cn/sysjj/sysgk/|M031复用|2025正式年度已存，不重增；2026—2027新公告未检出，不能视为确认不存在
辽宁|大连理工大学|工业装备结构分析优化与CAE全国重点实验室2026|https://www5.zzu.edu.cn/nerc/info/1073/3205.htm|M160复用|2026官方高校转载命中，原当期已收录；其他大连机器人/海工平台完整目录未核
辽宁|辽宁石油化工大学|石油化工智能优化安全运行省重点实验室2025|https://sice.lnpu.edu.cn/__local/6/85/AD/618AB99B1482BA4F1A20906037B_DEDEC0FE_32C8D.pdf|N011|PDF下载失败；机器人巡检个人项目不能推填年度指南，待手动
吉林|吉林大学|工程仿生、汽车底盘集成仿生2026正式年度公告|https://bionic.jlu.edu.cn/info/1041/1693.htm|N012、N013、M116、M117|2026正文读全，与2025分开；工程仿生管理办法验证码；汽车底盘管理文件未取得
吉林|长春理工大学|跨尺度微纳制造教育部重点实验室2025—2026立项线索|https://cmnm.cust.edu.cn/xwdt/4d5276ea31864958966b8a08a60a7226.htm|无新增正式公告|立项公告不是当前受理；原指南及机器人相关任务未取得，不据微纳名称纳入
黑龙江|哈尔滨工业大学|机器人技术系统2026年度及2026两项专项；2027定向|https://robot.hit.edu.cn/xxdt/list.htm|M034、E062、E063|年度复用；两专项明确校内全职教师排除；未取得2027当期，其他航天平台目录未全核
黑龙江|哈尔滨工程大学|智能装备/水下机器人国防平台|https://iip.hrbeu.edu.cn/|无新增|平台及个人项目已发现；2026—2027对外正式开放公告未取得，国防平台不猜公开机制
黑龙江|哈尔滨理工大学|先进制造智能化教育部重点实验室；复杂智能系统省重点实验室|https://amit.hrbust.edu.cn/home/news/100|M047复用|历史机器人医疗装备机制已收；2026命中建设推进会而非新开放通知；其他省平台当期指南仍缺
上海|同济大学|预制装配工程中心2026沈祖炎专项|https://prefabcenter.tongji.edu.cn/c0/f8/c15384a377080/page.htm|N003|定向焊接机器人方向已核，外部非合作单位须资助方事先意向；管理办法/协议仍缺
上海|上海科技大学|智能感知人机协同2026官方索引全文片段|https://klip-humaco.sist.shanghaitech.edu.cn/2026/0914/c14914a1126983/page.htm|M035|10月8日前截止现已过；网页404/TLS受限，保留既有条款，不倒退证据，附件待手动
上海|上海交通大学|柔性医疗机器人省重点实验室长期机制与2026立项|https://imr.sjtu.edu.cn/|M056复用|基金机制与立项页面已发现；某立项100万元不能当作本基金统一额度；当期窗口仍缺
安徽|中国科学技术大学|脑启发智能感知认知2026；先进机器人技术研究中心|https://institution.ustc.edu.cn/BIPCLab/zh_CN/article/994106/content/5479.htm|M041|正文全核不外拨/共享IP，具体机器人任务适用仍待核；ARC年度外部资助未取得
安徽|科大讯飞／中国科学技术大学|认知智能全国重点实验室2026高等教育专项|https://cogskl.iflytek.com/archives/3471|N008|具身场景感知线索，机器人具体任务适用及管理条件缺；已截止
安徽|安徽工程大学|高端装备先进感知智能控制教育部重点实验室|https://cee.ahpu.edu.cn/lapic/yqsb/list.psp|M042复用|机器人导航设施/方向已发现；2025已存，2026—2027新指南未取得
安徽|安徽工业大学|特种重载机器人省重点实验室2026|https://robotlab.ahut.edu.cn/info/1549/1412.htm|M061复用|年度官方命中与既有项目去重；其他独立实验室年度目录未全核
安徽|安徽大学|人机共融系统与智能装备安徽省工程实验室|https://www.ahu.edu.cn/2024/1021/c15129a349758/page.htm|无新增正式公告|平台/外单位已获课题线索已发现，年度指南/外部负责人条件未取得
安徽|江淮实验室|安徽省人形机器人2026指南建议征集|https://www.jhatc.cn/html/mobile/kexue/pingtaichanpin/2098331115939979266.html|M064复用|2026-09指南建议不是项目受理；正式2026课题通知尚未取得
浙江|浙江大学|农业智能感知机器人2025；工业控制2026—2027；流体2026|https://www.nercita.org.cn/infos/detail?id=10341&type=203|N004、M024、M026|农业官方转载读全、不外拨；其他年度复用；各平台2027新增受理未全核
浙江|中国科学院宁波材料所|浙江省机器人智能制造装备技术重点实验室|https://robotics-lab.nimte.ac.cn/view-13552.html|N009|官方明确开放基金/课题机制；2026—2027指南和全部实际条件未取得
福建|阳光学院|空间信息感知智能处理省重点实验室2022|https://isdm.ygu.edu.cn/info/1100/1376.htm|N006|机器人SLAM/路径/ROS任务及全部正文条款已核；2026—2027当期通知未取得
福建|厦门大学|低碳智慧能源装备平台；数字媒体计算中心；超智医疗中心2026|https://cdmc.xmu.edu.cn/info/1002/2413.htm|无新增机器人开放基金|数字媒体招博士后/研发赞助不是外部基金；超智医疗当前实际任务为临床生命数据，不据AI纳入；其他机器人工程平台目录仍缺
福建|福建理工大学|科研管理目录与2026设计创新平台|https://kyc.fjut.edu.cn/|无新增|命中社科设计创新不等于机器人基金；机器人省平台全名单未取得
江西|南昌航空大学|机载智能检测产业技术中心2026|https://www.nchu.edu.cn/xwzx/xngg/content_196002|S001本地输入保留|不重新算新增；外拨和IP正文未载，强制固定合作未落实
江西|江西飞行学院|低空地理信息航路省教育厅重点实验室2026|https://jcxy.jxfu.edu.cn/info/1042/14661.htm|N014|正式正文读全；指南/条例RAR下载受限，另一官方2025指南不能代2026附件
江西|南昌大学／华东交通大学|智能机器人省重点实验室／交通智能运维技术装备平台年度定向|https://www.ncu.edu.cn/|M112、M048复用|2024/2026原条目复用；本轮地区搜索未检出更多正式机器人开放基金；完整平台目录仍缺
山东|山东科技大学|智能感知自主控制省重点实验室2026|https://xindian.sdust.edu.cn/info/1008/7407.htm|M066本地输入保留|正文任务直接感知/控制已核，保留首页；管理ZIP尚未取得，知识产权和外拨仍待补
山东|青岛大学／附属医院|数字医学与计算机辅助手术省重点实验室跨年度指南|https://hdldb.net/news-detail.php?id=MjQwMQ%3D%3D|S002本地输入保留|2025发布列2026，实际2026受理窗口未证实；不进入首页
河南|河南工业大学|超硬磨料磨削装备省重点实验室2026|https://kjc.haut.edu.cn/info/1240/13366.htm|M080复用|明确机器人磨削抛光修整，年度已存；省内其他机器人省属高校完整名单仍缺
河南|郑州工商学院|河南省具身智能系统省重点实验室2026发布新闻|https://www.ztbu.edu.cn/html/1072/2026-06-24/content-12734.html|M049|官方发布事件不是全文指南；六月全国口径与其他批次河南口径不能直接合并，待原批次文件
湖北|武汉软件工程职业学院／武汉开放大学|复杂零件智能检测识别工程中心2026|https://gcyjzx.whvcse.edu.cn/info/1041/3921.htm|N002|任务/资格/金额/权属已核，附件及纸质收件细节缺；另一官方域名访问失败
湖北|华中科技大学|智能制造装备2027；图像信息处理智能控制2026|https://imet.hust.edu.cn/info/1031/2870.htm|M029、M050复用|不同平台年度已存；图像控制校外联合且校内报销不外拨，不能当普通校内业务费；其他完整平台未核
湖南|湖南大学|机器人视觉感知控制国家工程中心、视觉AI及电子制造机器人省重点平台|https://robot.hnu.edu.cn/|无新增正式公告|官方中心/学院介绍及2026研究新闻已定位；2026—2027外部开放基金未取得
湖南|湖南工学院|2026汽车零部件产业链平台专项|https://www.hnit.edu.cn/kjc/info/1134/7693.htm|N015|方向6动力学控制正文全核，管理附件验证码；其他五项育人管理不纳入
湖南|中南大学|自动化科研平台、工业智能系统；高性能复杂制造2025立项|https://soa.csu.edu.cn/info/1031/8984.htm|无新增正式公告|平台目录和人形关节项目立项线索，不是新的受理指南；2026—2027年度外部机制未取得
广西|广西大学|广西农业资源智能检测利用机器人方向|https://acip.gxu.edu.cn/zxgk/szqk.htm|无新增|人员/平台介绍不是基金；2026—2027当期对外机制未取得
广西|广西科技大学|广西汽车零部件与整车技术省重点平台2025成果|https://www.gxust.edu.cn/jxyjt/info/1075/7582.htm|无新增正式公告|机器人协同成果引用2025基金编号，仅立项/成果线索；2026年度指南未取得
海南|中科院深海科学与工程研究所|深海工程平台开放课题年度/立项|https://idsse.cas.cn/xwdt/tzgg/202608/t20260818_8261916.html|M121复用|2026发布页属2025申请结果，不当2026新通知；其他海洋机器人平台目录未全核
四川|西南石油大学|南充机器人智能制造—油气装备联合开放基金2026|https://www.swpu.edu.cn/jdy/info/1040/32450.htm|N007|评审公示有蛇形机器人，原2026联合申报公告未取得；待手动
四川|电子科技大学|智能终端四川省重点实验室；电磁辐射材料工程中心2026|https://yb.uestc.edu.cn/tsgjscszdsys/|无新增机器人基金|智能终端有历史基金机制，具体机器人年度任务未取得；电磁中心完整指南为材料/射频，不纳入
四川|四川大学|山区河流保护治理平台机器人仪器与电气机器人团队|https://skhl.scu.edu.cn/|无新增正式公告|有AUV设备不等于资助机器人任务；特殊环境机器人平台独立指南与目录仍缺
四川|西南交通大学／中铁大桥共同依托单位|桥梁智能绿色建造2026爬壁机器人；轨道交通运载系统2027|https://bridge.swjtu.edu.cn/info/1066/8471.htm|M114、M105复用|M114沿用完整已核条款，10月8日日期已过转历史；M105当期复用；各分室年度与完整平台目录仍缺
四川|成都信息工程大学|无人工程平台2024、应用支撑软件2026|https://kzgcxy.cuit.edu.cn/info/2046/4494.htm|无新增正式公告|2024机器人原页访问失败，年度条款未取得；2026软件任务文化内容及舆情，不因大模型收录
贵州|贵州大学|山地农业机械省重点平台；科学技术处公告目录|https://st.gzu.edu.cn/tzgg/list.htm|M089复用|2025指南/2026立项不混为2026新受理；其他机器人重点目录及2027年度尚缺
云南|昆明理工大学|复杂系统类脑省重点实验室2026；省平台验收目录|https://lxy.kust.edu.cn/info/1151/2522.htm|E065|年度正文全读，脑功能/高阶传播任务无具体机器人关联排除；智能控制省平台受理仍需查
甘肃|兰州交通大学|重点实验室目录、铁路系统运维及动力可靠性平台|https://www.lzjtu.edu.cn/kxyj/zdsys.htm|无新增正式公告|目录已发现；机器人相关年度任务与开放机制未取得
甘肃|兰州理工大学|成套装备智能化集成技术教育部重点实验室2026|https://jidian.lut.edu.cn/info/1924/18496.htm|M053复用|既有2026相关公告复用；2027新指南未取得，校内其他机器人工程平台名单未核
青海|青海大学|新能源智慧能源省重点实验室2026及2024机器人运维任务|https://seee.qhu.edu.cn/docs/2024-11/578a4dec562644c298214a650c53919c.pdf|M054|2024任务不沿用2026；2026适用机器人任务、原附件仍待手动
青海|青海师范大学|藏语智能、青藏地表生态2026年度|https://kjc.qhnu.edu.cn/info/1062/2238.htm|无新增机器人基金|年度任务藏语/地表生态不据AI纳入；其他机器人相关平台完整目录尚缺
宁夏|宁夏大学／自治区科技厅|数学基础学科中心2026及省重点实验室目录|https://kjt.nx.gov.cn/kjzy/cxtx/zdsys/202309/t20230914_4264687.html|M094复用|数学年度指南原待核，不据复杂网络等关键字放首页；机器人/装备目录尚未逐室定位
西藏|西藏大学|信息学院机器人合作新闻；生态环境重点实验室2026|https://it.utibet.edu.cn/info/1020/1631.htm|无新增机器人基金|企业机器人交流不是开放基金；生态年度不相关；机器人或智能装备重点平台目录未定位
新疆|新疆大学|农牧机器人智能装备工程研究中心介绍与开放制度|https://jxxy.xju.edu.cn/__local/0/23/6F/B2938303B9580E6741F5D6F72BE_A1C96726_4AE3B.pdf|N010|制度PDF已取得，但年度指南和单项额度未取得，中心总经费不当单项金额'''
corpus={p.name:p.read_text(encoding='utf8') for p in H.glob('search_*.json')};corpus.update({p.name:p.read_text(encoding='utf8') for p in H.glob('open_*.json')})
for line in spec.splitlines():
 region,institution,scope,url,projects,gaps=line.split('|')
 domain=url.split('/')[2];matches=[fn for fn,s in corpus.items() if url in s]; directed=[fn for fn,s in corpus.items() if domain in s]
 files=list(dict.fromkeys(matches+directed))[:10]
 prev=[p for p in old if p['institution']==institution]
 evidence=[dict(url=url,file=fn,status='本轮保存检索/打开原文，是否正文全读见已查范围') for fn in matches[:5]]
 if not matches:evidence=[dict(url=url,file='前轮资料复用' if prev else ','.join(files) or '仅地区发现检索；具体URL来自既有官方资料',status='入口/目录或既有证据；未宣称本轮全文取得')]
 rec=dict(region=region,institution=institution,scope=scope,checked_years='2026—2027定向发现；往年机制/公告保留原年度；未核年份见缺口',projects=projects,gaps=gaps,checked_date='2026-10-08—09（北京时间）',evidence=evidence,search_files=files)
 records.append(rec)
 D['coverage'].append(['全国扩展／重点剩余补查',institution,region,'2026-10-08—09（北京时间）',scope+'；'+rec['checked_years']+'；项目：'+projects,gaps,'部分已查；不代表机构全部平台完成',url,'检索证据：'+','.join(files)+'；'+gaps])
D['coverage'][0][0]='机构检索覆盖：保留既有记录；2026-10-08—09全国扩展逐机构追加'
D['coverage'][1][0]='平台目录发现、年度搜索、正文/附件核验分别记录；无完整平台名录与年度逐室证据，不标机构完成。'
D['national_coverage']=records
(H/'institutions_national.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
(H/'prepared_regions.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')

# Query-level regional gap audit; only queries are counted, not search results as full coverage.
regions=['北京','天津','河北','山西','内蒙古','辽宁','吉林','黑龙江','上海','江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南','广东','广西','海南','重庆','四川','贵州','云南','西藏','陕西','甘肃','青海','宁夏','新疆','澳门','香港','台湾']
queryrecords=[]
for p in sorted(H.glob('search_*.json')):
 x=json.loads(p.read_text(encoding='utf8'))
 for q in x.get('queries',[]):queryrecords.append(dict(query=q,file=p.name))
(H/'query_index.json').write_text(json.dumps(queryrecords,ensure_ascii=False,indent=2),encoding='utf8')
regionrows=[]
for r in regions:
 qs=[q for q in queryrecords if r in q['query'] or (r=='澳门' and 'um.edu.mo' in q['query']) or (r=='香港' and 'polyu.edu.hk' in q['query'])]
 rs=[x for x in records if x['region']==r]
 regionrows.append(dict(region=r,query_files=list(dict.fromkeys(q['file'] for q in qs)),institutions=[x['institution'] for x in rs],status='已开展发现/补漏；尚无完整省级目录逐室覆盖' if qs or rs else '本轮无可确认记录，未查'))
(H/'regional_gaps.json').write_text(json.dumps(regionrows,ensure_ascii=False,indent=2),encoding='utf8')

stats=D['stats']; report=['# 全国扩展与重点地区补查记录（2026-10-08—09）','',f'输入：GitHub 06753b6及本地网页修改版150条；保留S001/S002和M066已授权规则调整。本轮新增16条N001—N016（11条历史、5条待核），更新R006/M068/M043/M035/M041，新增4条有正式证据的剔除。当前{stats["total"]}条：首页{stats["current"]}、历史{stats["historical"]}、待核{stats["pending"]}、其他{stats["other"]}。本轮没有新发现并核实的当前受理项目。', '',f'实际新增/追加{len(records)}条机构范围记录，涉及{len(set(x["institution"] for x in records))}个机构对象；复用前轮69个重点地区机构/平台群。保存{len(list(H.glob("search_*.json")))}批搜索、{len(queryrecords)}条查询及正式公告/附件。查询数不是机构完成数。全国高校及省平台的完整总清单尚未取得，本轮是可审计的系统扩展，不能宣称全国或七地区全部检索完成。','', '按用户最新授权保留往年机制；此前样本补查文件中的“不新增历史”仅描述那一轮，不适用于本轮。核查基准北京时间2026-10-09，10月8日相关已截止项目移历史，时点不猜测。','', '## 重点地区接续与全国逐机构范围','']
for x in records:
 report.extend([f'### {x["region"]}｜{x["institution"]}',f'- 已查：{x["scope"]}。年度：{x["checked_years"]}。',f'- 项目：{x["projects"]}。',f'- 官方入口：[查看]({x["evidence"][0]["url"]})。检索原文：'+', '.join(x['search_files'])+'。',f'- 剩余：{x["gaps"]}。',''])
report.extend(['## 地区补漏审计','', '| 地区 | 本轮查询记录 | 已定位机构对象 | 剩余范围 |','|---|---|---|---|'])
for x in regionrows:report.append('|'+x['region']+'|'+','.join(x['query_files'])+'|'+ '；'.join(x['institutions'])+'|'+x['status']+'|')
report.extend(['','## 中央高校基本科研业务费交叉入口','', '长安大学道路施工平台M109与华科图像控制M050复用，不重复计数；华科明确校外联合负责人但不外拨，只在校内报销。清华—美团与哈工大两专项校内负责人限制不因机器人方向保留。清华信息国家研究中心N001不能在资金来源未載时推为基本科研业务费。长安机场/特殊地区平台仅正文或任务未完整取得，列入剩余检索缺口，不套既有单位条件。','', '其他重点缺口：省科技厅/教育厅全量相关平台目录，部分省属高校独立机器人实验室年度机制，澳门/香港研究中心外部负责人途径，原网页/附件受限条款；查不到不写成不存在。各项目手动清单见[人工补充清单](手动补充事项_20261009.md)。'])
report=[s.replace('更新R006/M068/M043/M035/M041，','更新R006/M068/M043/M035/M041/M106/M114，') for s in report]
(ROOT/'全国扩展检索记录_20261009.md').write_text('\n'.join(report),encoding='utf8')
manual=['# 手动补充事项（2026-10-09北京时间）','', f'优先列当前{stats["current"]}条、待核{stats["pending"]}条、新增项目及本轮更新项目。这里分别记录“资料未取得”和“已取得正文未载”；联系人咨询条款不要求重复打开网页。申请人年龄/职称/限项、实际固定合作者及到访安排另按每项原文确认。已取得R006正文，不再交人工补正文。','', '| 项目编号 | 平台/年度 | 精确公告及附件入口 | 需要补充或确认 |','|---|---|---|---|']
ids=list(dict.fromkeys(D['groups'][0]['ids']+D['groups'][2]['ids']+D['national_changes']['new_ids']+D['national_changes']['updated_ids']))
pm={p['id']:p for p in D['projects']}
for id in ids:
 p=pm[id];manual.append('|'+id+'|'+p['org']+'·'+p['lab']+'／'+str(p['year'])+'|'+'<br>'.join(p['sources'])+'|'+p['gaps'].replace('\n','<br>').replace('|','／')+'|')
(ROOT/'手动补充事项_20261009.md').write_text('\n'.join(manual),encoding='utf8')
print(json.dumps({'coverage_added':len(records),'unique_institution_objects':len(set(x['institution'] for x in records)),'queries':len(queryrecords),'regions_with_records':len([x for x in regionrows if x['query_files'] or x['institutions']]),'manual_projects':len(ids)},ensure_ascii=False))
