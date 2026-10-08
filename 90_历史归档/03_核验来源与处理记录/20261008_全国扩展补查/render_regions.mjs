import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname;
const d=JSON.parse(await fs.readFile(path.join(H,'prepared_regions.json'),'utf8'));
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,'全国机器人开放课题_个人申报台账_全国扩展版_20261009.xlsx')));
const row=id=>d.projects.findIndex(p=>p.id===id)+2;
const pr=id=>d.list_maps['07待核项目'].find(x=>x.id===id).row;
const views=[['home','01申报总览','A1:F7'],['home_new','01申报总览','A8:F16'],['new_conditions','02项目完整详情',`K${row('N001')}:N${row('N001')}`],['new_outputs','02项目完整详情',`O${row('N001')}:S${row('N001')}`],['coverage','03机构检索覆盖',`A${d.coverage.length-4}:I${d.coverage.length-2}`],['new_pending','07待核项目',`A${pr('N007')}:H${pr('N007')+1}`]];
await fs.mkdir(path.join(H,'renders'),{recursive:true});
for(const [name,sheetName,range] of views){const b=await book.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(path.join(H,'renders',name+'.png'),new Uint8Array(await b.arrayBuffer()));console.log(name);}
await fs.writeFile(path.join(H,'render_manifest.json'),JSON.stringify(views.map(([name,sheet,range])=>({file:'renders/'+name+'.png',sheet,range,status:'pending'})),null,2));
