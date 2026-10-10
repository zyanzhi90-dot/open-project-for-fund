import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const H=import.meta.dirname,d=JSON.parse(await fs.readFile(path.join(H,'plan.json'),'utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(H,d.output_name)));
for(const [name,range] of [['home_top','A1:F7'],['home_middle','A8:F14'],['home_bottom','A15:F22']]){
 const b=await w.render({sheetName:'01申报总览',range,scale:1,format:'png'});await fs.writeFile(path.join(H,name+'.png'),new Uint8Array(await b.arrayBuffer()));console.log(name);
}
