export const meta = {
  name: 'find-careers-urls',
  description: 'Research real careers/ATS URLs for football clubs that have none on file',
  phases: [ { title: 'Find careers URLs' } ],
}

const SEARCH_ONLY = ["AS Monaco","OGC Nice","RC Lens","Montpellier HSC","AJ Auxerre","Le Havre AC","Angers SCO","FC Barcelona","Real Betis Balompie","Real Sociedad","Athletic Club Bilbao","RCD Mallorca","CA Osasuna","Rayo Vallecano","Getafe CF","Levante UD","Real Racing Santander","UD Las Palmas","UD Almeria","CD Castellon","RC Deportivo de La Coruna","FC Andorra","Real Sporting de Gijon","Albacete Balompie","Bologna FC 1909","ACF Fiorentina","Torino FC","Udinese Calcio","Parma Calcio 1913","Genoa CFC","Cagliari Calcio","Hellas Verona FC","US Lecce","US Cremonese","Sassuolo Calcio","Pisa SC","US Avellino","SSC Bari","Carrarese Calcio","US Catanzaro","Cesena FC","Empoli FC","Frosinone Calcio","SS Juve Stabia","Mantova 1911","Modena FC","AC Monza","Calcio Padova","Palermo FC","Delfino Pescara","AC Reggiana","UC Sampdoria","Spezia Calcio","FC Sudtirol","Venezia FC","Virtus Entella","Stade Brestois 29","Toulouse FC","Rangers FC","Sporting CP"]

function chunk(a, n){ const o=[]; for(let i=0;i<a.length;i+=n) o.push(a.slice(i,i+n)); return o }

const SCHEMA = {
  type:'object', additionalProperties:false, required:['results'],
  properties:{ results:{ type:'array', items:{
    type:'object', additionalProperties:false,
    required:['club','careers_url','ats_platform','verified'],
    properties:{
      club:{type:'string'},
      careers_url:{type:['string','null']},
      ats_platform:{type:['string','null']},
      verified:{type:'boolean'},
      notes:{type:'string'},
    }}}},
}

phase('Find careers URLs')
const batches = chunk(SEARCH_ONLY, 4)
log(`Researching ${SEARCH_ONLY.length} clubs in ${batches.length} batches of 4`)

const out = await parallel(batches.map((b, i) => () =>
  agent(
    `Find the official CAREERS / VACANCIES page for each football club below. Time-box yourself to ~3 minutes per club — return best-effort, don't get stuck.

Clubs: ${b.join(' | ')}

For each club:
1. WebSearch: "<club> lavora con noi" (Italian) / "<club> trabaja con nosotros" or "empleo" (Spanish) / "<club> recrutement" or "nous rejoindre" (French) / "<club> careers". Also try "<club> teamtailor OR workday OR recruitee OR greenhouse OR factorial OR inrecruiting".
2. Pick the best URL: a recognised ATS (teamtailor/workday/greenhouse/lever/workable/personio/recruitee/smartrecruiters/softgarden/inrecruiting/factorial/altamira) OR the club's own /careers /vacancies /lavora-con-noi /trabaja-con-nosotros page.
3. Verify it loads: fetch with Bash (curl/python requests), expect HTTP 200 with job-ish content. Set verified=true only if you actually fetched it and saw vacancies or an application form.
4. ats_platform = the recognised platform slug, else null. careers_url=null if the club truly has no public careers page (LinkedIn/email only) — say so in notes.

Return exactly one result object per club listed.`,
    { label:`urls:b${i+1}`, phase:'Find careers URLs', schema:SCHEMA, agentType:'general-purpose' }
  ).then(r => r.results || []).catch(()=>[])
))

return { careers_urls: out.flat() }
