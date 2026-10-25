const fs=require('fs'),path=require('path'),os=require('os');
const {pathToFileURL}=require('url');
const runtime=path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const {chromium}=require(path.join(runtime,'node/node_modules/playwright'));
const root=path.resolve(__dirname,'..'),work=path.join(root,'output/pdf/production');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 const pending=JSON.parse(fs.readFileSync(path.join(work,'pending.json'),'utf8'));const results=[];let next=0;
 async function worker(){while(next<pending.length){const m=pending[next++],page=await browser.newPage({viewport:{width:665,height:1100}});
  try{
   await page.goto(pathToFileURL(m.html).href);await page.waitForFunction(()=>window.ready===true);await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode())));
   const checks=await page.evaluate(()=>{
    const height=250*96/25.4;
    for(const el of document.querySelectorAll('.exercise,.answer'))if(el.getBoundingClientRect().height>height)el.classList.add('long');
    return {mathErrors:window.mathErrors,questions:document.querySelectorAll('[data-q]').length,answers:document.querySelectorAll('[data-answer]').length,math:document.querySelectorAll('.math').length,images:[...document.images].map(im=>({src:im.src,width:im.naturalWidth,height:im.naturalHeight,loaded:im.complete})),overflows:[...document.querySelectorAll('.math,.exercise,.answer,table')].filter(el=>el.scrollWidth>el.clientWidth+3).map(el=>({tag:el.tagName,text:el.textContent.slice(0,140),width:el.clientWidth,scroll:el.scrollWidth})),unparsedDollars:[...document.querySelectorAll('p,td,h1,h2,h3')].filter(el=>[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.includes('$'))).map(el=>el.textContent.slice(0,140)),longBlocks:[...document.querySelectorAll('.long')].map(el=>el.dataset)};
   });
   const imageAssignments=await page.evaluate(()=>[...document.images].map(im=>({alt:im.alt,question:im.closest('[data-q]')?.dataset.q})));
   checks.imageAssignments=imageAssignments;
   if(checks.mathErrors.length||checks.questions!==m.questions||checks.answers!==m.answers||checks.images.length!==m.images||imageAssignments.some(x=>String(x.alt.match(/\d+/)?.[0])!==x.question))throw Error(JSON.stringify(checks));
   await page.pdf({path:m.raw_pdf,format:'A4',preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,headerTemplate:`<div style="font:8px Arial;width:100%;margin:0 48px;color:#536e76;text-align:left;direction:rtl">מה״ט · חומרי תרגול · פרק ${m.chapter}</div>`,footerTemplate:'<div style="font:9px Arial;width:100%;text-align:center;color:#536e76;direction:rtl">אמיתי · <span style="direction:ltr;unicode-bidi:isolate;display:inline-block"><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
   results.push({source:m.source,...checks});console.log(results.length+'/'+pending.length+' '+m.source);
  }catch(e){results.push({source:m.source,error:String(e)});console.error('ERROR '+m.source+' '+e.message.slice(0,1400));}finally{await page.close();}
 }}
 await Promise.all([worker(),worker(),worker()]);await browser.close();
 fs.writeFileSync(path.join(work,'render-checks.json'),JSON.stringify(results,null,2));
 if(results.some(x=>x.error))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
