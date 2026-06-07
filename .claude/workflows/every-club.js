export const meta = {
  name: 'every-club-working',
  description: 'Reverse-engineer every football-club ATS + find missing careers URLs so all 176 clubs scrape',
  phases: [
    { title: 'Crack ATS platforms' },
    { title: 'Find careers URLs' },
    { title: 'Diagnose generic misses' },
  ],
}

const REPO = 'football_jobs'

// ── Phase 1: ATS platforms with no working handler ───────────────────────────
const PLATFORMS = [
  { name: 'eploy', examples: [
      'https://www.qpr.co.uk/club/careers',
      'https://www.sufc.co.uk/club/vacancies/',
      'https://www.watfordfc.com/club/careers',
      'https://www.swfc.co.uk/club/careers/' ] },
  { name: 'hrworks', examples: [
      'https://jobs.fcaugsburg.de/de',
      'https://jobs.fcstpauli.com/de',
      'https://jobapplication.hrworks.de/de?companyId=ba8e529b' ] },
  { name: 'recruitee', examples: [ 'https://werkenbij.psv.nl/' ] },
  { name: 'softgarden', examples: [
      'https://karriere.bvb.de/', 'https://karriere.werder.de/' ] },
  { name: 'hibob', examples: [ 'https://fulhamfc.careers.hibob.com/jobs' ] },
  { name: 'corehr_workforceready', examples: [
      'https://secure.workforceready.eu/ta/6189861.careers?CareersSearch=&lang=en-GB' ] },
  { name: 'hellowork', examples: [
      'https://www.hellowork.com/fr-fr/entreprises/stade-rennais-football-club-170554.html' ] },
]

// ── Phase 2: clubs with NO careers URL (need research) ───────────────────────
const SEARCH_ONLY = ["AS Monaco","OGC Nice","RC Lens","Montpellier HSC","AJ Auxerre","Le Havre AC","Angers SCO","FC Barcelona","Real Betis Balompie","Real Sociedad","Athletic Club Bilbao","RCD Mallorca","CA Osasuna","Rayo Vallecano","Getafe CF","Levante UD","Real Racing Santander","UD Las Palmas","UD Almeria","CD Castellon","RC Deportivo de La Coruna","FC Andorra","Real Sporting de Gijon","Albacete Balompie","Bologna FC 1909","ACF Fiorentina","Torino FC","Udinese Calcio","Parma Calcio 1913","Genoa CFC","Cagliari Calcio","Hellas Verona FC","US Lecce","US Cremonese","Sassuolo Calcio","Pisa SC","US Avellino","SSC Bari","Carrarese Calcio","US Catanzaro","Cesena FC","Empoli FC","Frosinone Calcio","SS Juve Stabia","Mantova 1911","Modena FC","AC Monza","Calcio Padova","Palermo FC","Delfino Pescara","AC Reggiana","UC Sampdoria","Spezia Calcio","FC Sudtirol","Venezia FC","Virtus Entella"]
// Indeed-only careers URLs (anti-bot) — replace with a real club careers/ATS page
const INDEED = ["Stade Brestois 29","Toulouse FC","Rangers FC","Sporting CP"]

// ── Phase 3: generic-html pages where scraper finds 0 but page mentions analytics ──
const GENERIC_MISS = [
  ["FC Utrecht","https://www.fcutrecht.nl/vacatures/"],
  ["RSC Anderlecht","https://www.rsca.be/en/club/jobs"],
  ["Stade Rennais FC","https://www.hellowork.com/fr-fr/entreprises/stade-rennais-football-club-170554.html"],
  ["Real Oviedo","https://www.realoviedo.es/empleo"],
  ["Cordoba CF","https://www.infojobs.net/cordoba-club-de-futbol-sad/em-i97495253534949677982680012053389517751"],
  ["CD Leganes","https://www.infojobs.net/club-deportivo-leganes-sa-d/em-i97505653505948677685668023214499200069"],
  ["Cadiz CF","https://www.cadizcf.com/oferta-de-empleo"],
  ["AFC Bournemouth","https://careers.afcb.co.uk/"],
  ["Brighton & Hove Albion FC","https://www.brightonandhovealbion.com/career-opportunities"],
  ["Charlton Athletic FC","https://www.charltonafc.com/vacancies"],
  ["Derby County FC","https://www.dcfc.co.uk/page/permanent-roles"],
  ["Leicester City FC","https://www.lcfc.com/vacancies"],
  ["Oxford United FC","https://www.oufc.co.uk/vacancies-oxford-united"],
  ["West Bromwich Albion FC","https://www.wba.co.uk/club/vacancies"],
  ["Celtic FC","https://www.celticfc.com/club/jobs-at-celtic/permanent-and-fixed-term-roles/"],
  ["FC Midtjylland","https://www.fcm.dk/klubben/karriere/"],
]

function chunk(a, n){ const o=[]; for(let i=0;i<a.length;i+=n) o.push(a.slice(i,i+n)); return o }

const SPEC_SCHEMA = {
  type:'object', additionalProperties:false,
  required:['platform','works','approach','recipe','confidence'],
  properties:{
    platform:{type:'string'},
    works:{type:'boolean', description:'true only if you VERIFIED it returns jobs live'},
    approach:{type:'string', enum:['public-api','embedded-json','html-scrape','headless-needed','dead-end']},
    detect:{type:'string', description:'how to detect this platform from a careers_url or page body'},
    recipe:{type:'string', description:'Step-by-step implementation recipe: how to derive the request URL from the careers_url, HTTP method, required headers/body, the JSON path to the jobs array, and which fields hold the job title and the apply URL. Detailed enough to code a Python handler from.'},
    example_club:{type:'string'},
    example_count:{type:'number'},
    sample_titles:{type:'array', items:{type:'string'}},
    confidence:{type:'string', enum:['high','medium','low']},
    notes:{type:'string'},
  },
}

const URLS_SCHEMA = {
  type:'object', additionalProperties:false, required:['results'],
  properties:{ results:{ type:'array', items:{
    type:'object', additionalProperties:false,
    required:['club','careers_url','ats_platform','verified'],
    properties:{
      club:{type:'string'},
      careers_url:{type:['string','null'], description:'best real careers/vacancies/ATS page, or null if none exists'},
      ats_platform:{type:['string','null'], description:'detected ATS slug e.g. teamtailor/recruitee/workday/eploy/null'},
      verified:{type:'boolean', description:'true if you fetched it and it returned 200 with job content'},
      notes:{type:'string'},
    }}}},
}

const DIAG_SCHEMA = {
  type:'object', additionalProperties:false, required:['results'],
  properties:{ results:{ type:'array', items:{
    type:'object', additionalProperties:false,
    required:['club','cause','fix','has_real_role'],
    properties:{
      club:{type:'string'},
      cause:{type:'string', enum:['js-rendered','embedded-json','path-hint-filtered','cookie-false-positive','anti-bot','no-real-role','other']},
      fix:{type:'string', description:'concrete fix: API endpoint to call, JSON path, or "none - genuinely no data role"'},
      has_real_role:{type:'boolean', description:'does this club ACTUALLY have an open data/analytics/performance-analyst role right now?'},
      sample_titles:{type:'array', items:{type:'string'}},
    }}}},
}

// ════════════════════════════════════════════════════════════════════════════
phase('Crack ATS platforms')
log(`Reverse-engineering ${PLATFORMS.length} ATS platforms`)

const platformSpecs = await parallel(PLATFORMS.map(p => () =>
  agent(
    `You are reverse-engineering the "${p.name}" recruitment platform used by football clubs, so we can scrape its job listings programmatically.

Example club careers pages on this platform:
${p.examples.map(u => '  - ' + u).join('\n')}

Working dir context: the scraper lives in ${REPO}/scraper.py — read it to match the existing handler style (functions like _teamtailor, _talos, _jobtoolz return lists of vacancies). Existing handlers show the patterns (public JSON API, or embedded JSON in the page, or two-step token flows).

YOUR JOB:
1. Fetch an example page with Bash (python3 -c "import requests;..." or curl). Inspect HTML, look for: an embedded JSON job array, a fetch/XHR to a JSON API (search the JS bundles for api/vacanc/job/search endpoints), or a public REST API for the platform.
2. Figure out how to get the FULL list of current vacancies (title + apply URL) for a club from JUST its careers_url.
3. VERIFY by actually fetching the API/data live and printing real job titles. Do NOT guess — run it.
4. Return a precise implementation recipe: how to derive the request from the careers_url, method, headers, body, JSON path to the jobs array, the title field, and the job-url field. Include a verified example (club, count, a few sample titles).

If the platform is JS-only with no reachable API (needs a headless browser), set approach=headless-needed and works=false but still describe what you found. If a careers_url just embeds the jobs as JSON in the HTML, approach=embedded-json and give the exact regex/JSON path.

Be rigorous and verify live. Token budget is not a concern — dig into JS bundles if needed.`,
    { label:`crack:${p.name}`, phase:'Crack ATS platforms', schema:SPEC_SCHEMA, agentType:'general-purpose' }
  ).then(r => ({...r, _platform:p.name})).catch(()=>null)
))

// ════════════════════════════════════════════════════════════════════════════
phase('Find careers URLs')
const researchClubs = [
  ...SEARCH_ONLY.map(c => ({club:c, why:'no careers url on file'})),
  ...INDEED.map(c => ({club:c, why:'only an Indeed URL on file (anti-bot) - find the real one'})),
]
const batches = chunk(researchClubs, 5)
log(`Researching careers URLs for ${researchClubs.length} clubs in ${batches.length} batches`)

const urlResults = await parallel(batches.map((b, i) => () =>
  agent(
    `Find the REAL careers / vacancies page for each of these football clubs. For each, I need the URL where the club actually posts job vacancies (their own careers page, or the ATS they use: Teamtailor, Workday, Greenhouse, Lever, Workable, Personio, Recruitee, SmartRecruiters, Eploy, Jobtoolz, SuccessFactors, etc.).

Clubs:
${b.map(x => '  - ' + x.club + '  ('+x.why+')').join('\n')}

For each club:
1. Use WebSearch / WebFetch to find the official careers page. Search terms like "<club> careers", "<club> vacatures/lavora con noi/trabaja con nosotros/jobs", "<club> teamtailor OR workday OR greenhouse".
2. Prefer a structured ATS (you can give the ATS domain URL) or the club's own /careers, /vacancies, /jobs, /lavora-con-noi, /trabaja-con-nosotros page.
3. VERIFY the URL actually loads (fetch it with Bash; expect HTTP 200 and job-ish content). Set verified=true only if you fetched it.
4. Identify the ats_platform if recognizable (e.g. 'teamtailor','recruitee','workday','greenhouse','lever','workable','personio','smartrecruiters','eploy','jobtoolz','successfactors') else null.
5. If a club genuinely has NO public careers page (only LinkedIn/email), set careers_url=null and explain in notes.

Italian clubs often use "lavora con noi"; Spanish "trabaja con nosotros"/"empleo"; French "nous rejoindre"/"recrutement". Return one result per club.`,
    { label:`urls:batch${i+1}`, phase:'Find careers URLs', schema:URLS_SCHEMA, agentType:'general-purpose' }
  ).then(r => r.results || []).catch(()=>[])
))

// ════════════════════════════════════════════════════════════════════════════
phase('Diagnose generic misses')
const diagBatches = chunk(GENERIC_MISS, 4)
log(`Diagnosing ${GENERIC_MISS.length} generic-html clubs where the scraper finds nothing`)

const diagResults = await parallel(diagBatches.map((b, i) => () =>
  agent(
    `These football-club careers pages mention "analyst"/"data"/"analytics" but our static-HTML scraper extracts ZERO vacancies. For each, determine WHY and HOW to fix it.

Clubs (name + careers_url):
${b.map(([c,u]) => '  - ' + c + '  ' + u).join('\n')}

For each:
1. Fetch the page with Bash. Determine the cause:
   - js-rendered: jobs load via JavaScript, not in static HTML
   - embedded-json: jobs ARE in the HTML as a JSON blob / script (give the path/regex)
   - path-hint-filtered: job links exist but our path-hint filter drops them
   - cookie-false-positive: the "analytics" mentions are just cookie-consent text, no real jobs
   - anti-bot: page blocks scraping
   - no-real-role: page loads fine but has no data/analytics role currently
2. If js-rendered, try to find the underlying JSON API (inspect JS/network patterns) and give the endpoint.
3. Decide has_real_role: does the club ACTUALLY have an open data/analytics/performance-analyst (NOT sports-science/physio/coach) vacancy right now? List sample real titles if any.
4. Give a concrete fix (API endpoint + JSON path, or "none").

Verify live with Bash. Return one result per club.`,
    { label:`diag:batch${i+1}`, phase:'Diagnose generic misses', schema:DIAG_SCHEMA, agentType:'general-purpose' }
  ).then(r => r.results || []).catch(()=>[])
))

return {
  platforms: platformSpecs.filter(Boolean),
  careers_urls: urlResults.flat(),
  diagnoses: diagResults.flat(),
}
