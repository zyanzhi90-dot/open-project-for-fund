import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=path.dirname(fileURLToPath(import.meta.url)), R=path.resolve(H,'../../..');
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(R,'全国机器人开放课题_个人申报台账_最终核验版_20261008.xlsx')));
const views=[
 ['handoff_deadline','01申报总览','A26:F35'],
 ['handoff_leads','01申报总览','A39:F47'],
 ['handoff_detail_identity','02项目完整详情','A1:J3'],
 ['handoff_detail_delivery','02项目完整详情','O1:S3'],
 ['handoff_detail_sources','02项目完整详情','T1:AA3'],
 ['handoff_coverage','03机构检索覆盖','A1:I9'],
 ['handoff_log','04本轮信息核验日志','A1:H4'],
 ['handoff_excluded','05剔除记录','A1:G4'],
];
for(const [name,sheetName,range] of views){
 const b=await book.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await b.arrayBuffer()));
 console.log(name+' '+sheetName+' '+range);
}
