import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=path.dirname(fileURLToPath(import.meta.url));
const d=JSON.parse(await fs.readFile(path.join(H,'prepared_strict.json'),'utf8'));
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,'全国机器人开放课题_个人申报台账_严格重筛版_20261008.xlsx')));
const row=id=>d.projects.findIndex(p=>p.id===id)+2;
const views=[
 ['home_1','01申报总览','A1:F7'],['home_2','01申报总览','A8:F13'],
 ['detail_identity','02项目完整详情','A1:J3'],
 ['detail_conditions','02项目完整详情','K1:N3'],
 ['detail_outputs','02项目完整详情','O1:S3'],
 ['detail_sources','02项目完整详情','T1:AA3'],
 ['detail_long_funds','02项目完整详情',`K${row('M004')}:N${row('M004')}`],
 ['detail_long_outputs','02项目完整详情',`O${row('M157')}:S${row('M157')}`],
 ['detail_blocked','02项目完整详情',`K${row('M100')}:Q${row('M100')}`],
 ['coverage','03机构检索覆盖','A1:I8'],
 ['log','04本轮信息核验日志','A1:H3'],
 ['excluded_prior','05剔除记录','A1:G4'],
 ['excluded_new','05剔除记录','A34:G37'],
 ['history_first','06历史项目','A1:F5'],
 ['history_last','06历史项目','A73:F76'],
 ['pending','07待核项目','A1:H4'],
 ['other','08其他资助','A1:H5'],
];
await fs.mkdir(path.join(H,'renders'),{recursive:true});
for(const [name,sheetName,range] of views){
 if(process.argv[2] && name!==process.argv[2])continue;
 const blob=await book.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(path.join(H,'renders',name+'.png'),new Uint8Array(await blob.arrayBuffer()));
 console.log(name+' '+sheetName+' '+range);
}
await fs.writeFile(path.join(H,'render_manifest.json'),JSON.stringify(views.map(([name,sheet,range])=>({file:'renders/'+name+'.png',sheet,range,status:'pending'})),null,2));
