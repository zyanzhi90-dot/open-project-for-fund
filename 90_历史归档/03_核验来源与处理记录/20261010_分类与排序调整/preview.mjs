import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,R=path.resolve(H,'../../..');
const source=process.argv[2]||path.join(R,'全国机器人开放课题_个人申报台账_结构精简版_20261009.xlsx');
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(source)).catch(e=>{console.log('IMPORT ERROR '+String(e.message).slice(0,3000));process.exit(1);});
const after=Boolean(process.argv[2]);
const views=after?[
 ['home_first','01申报总览','A1:F7'],['home_middle','01申报总览','A8:F14'],['home_last','01申报总览','A15:F20'],
 ['detail_status','02项目完整详情','A1:J4'],['detail_gaps','02项目完整详情','R1:AA3'],
 ['history_first','03历史项目','A1:F5'],['history_last','03历史项目','A283:F286'],
 ['other','04其他资助','A1:H3'],['coverage','05机构检索覆盖','A6:I8'],
]:[['before_home','01申报总览','A1:F5'],['before_history','03历史项目','A1:F4']];
for(const [name,sheetName,range] of views){
 const blob=await w.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
 console.log(name+' '+range);
}
await fs.writeFile(path.join(H,after?'render_manifest.json':'before_manifest.json'),JSON.stringify(views,null,2));
console.log((await w.inspect({kind:'table',range:'01申报总览!A1:F4',include:'values',tableMaxRows:4,tableMaxCols:6,maxChars:700})).ndjson);
