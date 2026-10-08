import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=path.dirname(fileURLToPath(import.meta.url)),R=path.resolve(H,'../../..');
const book=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(R,'全国机器人开放课题_个人申报台账_最终核验版_20261008.xlsx')));
const d=JSON.parse(await fs.readFile(path.join(H,'prepared_final.json'),'utf8'));
for(const [name,sheetName,range] of [['delivered_home','01申报总览','A1:F7'],['delivered_history','01申报总览',`A${d.groups[2].start-1}:F${d.groups[2].start+3}`],['delivered_other','01申报总览',`A${d.groups[3].start-1}:F${d.groups[3].end}`],['delivered_terms','02项目完整详情','K1:N3']]){
 const b=await book.render({sheetName,range,scale:1.1,format:'png'});await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await b.arrayBuffer()));
}
console.log('Delivered workbook imported; current, history, other funding and terms rendered.');
