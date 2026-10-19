// Run inside the backend container, only on explicit owner request.
const Database=require('better-sqlite3');
const path=require('node:path');
(async()=>{
 if(process.env.RESET_SELLER_ACCOUNTS!=='YES')throw Error('Set RESET_SELLER_ACCOUNTS=YES to reset seller accounts');
 const url=process.env.DATABASE_URL;
 if(!url||!url.startsWith('file:'))throw Error('Expected SQLite DATABASE_URL');
 const filename=path.resolve(url.slice(5));
 if(!filename.startsWith('/app/data/'))throw Error('Unexpected database location');
 const db=new Database(filename,{fileMustExist:true});
 for(const table of ['sellers','sessions','verification_codes'])if(!db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(table))throw Error('Missing expected table '+table);
 const backup=filename+'.before-account-reset-'+Date.now()+'.sqlite';
 await db.backup(backup);
 const count=db.prepare('SELECT count(*) AS n FROM sellers').get().n;
 db.transaction(()=>{db.prepare('DELETE FROM sessions').run();db.prepare('DELETE FROM verification_codes').run();db.prepare('DELETE FROM sellers').run();})();
 db.close();console.log('Seller accounts removed:',count);console.log('Database backup:',backup);console.log('Client records, quotes and catalogs retained.');
})().catch(err=>{console.error(err.message);process.exitCode=1;});
