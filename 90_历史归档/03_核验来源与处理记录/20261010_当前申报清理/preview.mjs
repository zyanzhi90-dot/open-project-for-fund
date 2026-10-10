import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,d=JSON.parse(await fs.readFile(path.join(H,'plan.json'),'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,d.output_name)));
const frow=d.history.findIndex(e=>e.id==='F010')+2;
const detailrow=d.patches.find(p=>p.row&&p.value==='任务范围未明确·仅留详情').row;
const views=process.argv[2]==='additional'?[['history_large','03历史项目',`A${frow}:F${frow+1}`],['detail_status','02项目完整详情',`A${detailrow}:G${detailrow+1}`]]:[['other','04其他资助','A1:H3'],['history','03历史项目','A1:F5'],['history_fund','03历史项目','A287:F297']];
for(const [name,sheetName,range] of views){
 await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await (await w.render({sheetName,range,scale:1,format:'png'})).arrayBuffer()));console.log(name);
}
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'formula error scan'})).ndjson);
