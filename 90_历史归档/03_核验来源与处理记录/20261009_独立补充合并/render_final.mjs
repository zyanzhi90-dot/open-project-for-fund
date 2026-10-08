import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname;
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,'全国机器人开放课题_个人申报台账_独立复核合并版_20261009.xlsx')));
for(const [name,sheetName,range] of [['M078','02项目完整详情','P10:S10'],['M014','02项目完整详情','J72:N72'],['R011','06历史项目','A97:F97'],['pending','07待核项目','A14:H16'],['log','04本轮信息核验日志','A2391:H2393']]){
 await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await (await w.render({sheetName,range,scale:1,format:'png'})).arrayBuffer()));
}
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},summary:'合并后错误检查'})).ndjson);
