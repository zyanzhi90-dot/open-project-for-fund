import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../..');
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'全国机器人开放课题_个人申报台账_筛选核验版_20261008.xlsx')));
const d=JSON.parse(await fs.readFile(path.join(here,'prepared.json'),'utf8'));
const row=d.projects.findIndex(p=>p.id==='M035')+2;
for(const [name,sheetName,range] of [['final_home','01申报总览','A1:F8'],['final_current','01申报总览',`A${row}:F${row+6}`],['final_terms','02项目完整详情','J11:P11']]){
 const blob=await book.render({sheetName,range,scale:1.2,format:'png'});
 await fs.writeFile(path.join(here,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
console.log((await book.inspect({kind:'table',range:"'01申报总览'!A5:F7",tableMaxRows:3,tableMaxCols:6,maxChars:1500})).ndjson);
console.log('Final workbook imported and rendered successfully.');
