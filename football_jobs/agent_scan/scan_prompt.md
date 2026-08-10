# Football analytics job scan — agent run

This is the agent-driven counterpart to the Streamlit app. It does what the
**Refresh data** button does — scan every club, match data/analytics roles, dedupe,
report — but as a Claude agent run instead of `scraper.py`. It leans on two tools:

- **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** — the agent's web
  reach. Use its channels (web / search / GitHub / social) for every lookup instead
  of scraping raw HTML yourself.
- **[Ruflo](https://github.com/ruvnet/ruflo)** — the swarm harness. Spawn agents
  (`swarm_init` / `agent_spawn`) so batches of clubs are scanned in parallel rather
  than one slow serial pass.

See `README.md` in this folder for the one-time setup of both tools. The club list in
section 1 is generated from the app's `clubs.py` (176 hand-curated clubs) by
`build_prompt.py`; regenerate it whenever `clubs.py` changes rather than editing the
list by hand.

---

## The prompt

You are my job-hunting research agent. I am a football data scientist looking for
DATA / ANALYTICS / PERFORMANCE-ANALYSIS roles at European football clubs.

Scan the clubs listed below, find every currently-open role that fits, and give me
one report. Accuracy matters more than volume: I would rather see 12 real roles than
60 guesses. Never invent a vacancy, a URL, or a date.

Do the research with agents rather than fetching everything yourself: use the
`agent-reach` skill for every web lookup, and spawn ruflo agents (`swarm_init` /
`agent_spawn`) so batches of clubs are scanned in parallel. A good shape is one
worker per league group, each handed its slice of the club list below.

## 1. Which clubs

Each line is `Club name | careers URL`. The careers URL is the app's curated entry
point — **start there**. When it says "search layers only", the club has no
scrapable careers page, so go straight to L3/L4 for it.

<CLUBS>
Club | Careers URL (the app's curated entry point — start here)

### Netherlands
PSV | https://werkenbij.psv.nl/
Ajax | https://werkenbij.ajax.nl/vacatures
AZ Alkmaar | https://www.werkenbijaz.nl/vacatures
Feyenoord | https://www.feyenoord.com/nl/vacatures
FC Utrecht | https://www.fcutrecht.nl/vacatures/

### Belgium
Royal Antwerp FC | https://www.royalantwerpfc.be/club/vacatures
Royale Union Saint-Gilloise | https://rusg.brussels/en/jobs
RSC Anderlecht | https://www.rsca.be/en/club/jobs
KRC Genk | https://www.krcgenk.be/nl/vacatures
Club Brugge | https://jobs.clubbrugge.be/nl

### Germany
FC Bayern Munich | https://careers.fcbayern.com/go/Alle-Jobangebote-anzeigen/8774701/
Borussia Dortmund | https://karriere.bvb.de/
Bayer 04 Leverkusen | https://www.bayer04.de/en-US/page/stellenangebote
RB Leipzig | https://rbleipzig.com/de/klub/rbl/karriere
VfB Stuttgart | https://www.vfb.de/de/1893/aktuell/jobs/jobs/
Eintracht Frankfurt | https://klub.eintracht.de/jobs/ag/
SC Freiburg | https://jobs.scfreiburg.com/en
1. FSV Mainz 05 | https://jobapplication.hrworks.de/de?companyId=ba8e529b
Borussia Mönchengladbach | https://job.borussia.de/de
VfL Wolfsburg | https://www.vfl-wolfsburg.de/der-vfl/jobs/direkteinstieg
FC Augsburg | https://jobs.fcaugsburg.de/de
Werder Bremen | https://karriere.werder.de/
TSG Hoffenheim | https://www.tsg-hoffenheim.de/tsg/karriere/stellenangebote
1. FC Union Berlin | https://www.altefoersterei.berlin/en/career-OIiJ
FC St. Pauli | https://jobs.fcstpauli.com/de
1. FC Heidenheim | https://www.fc-heidenheim.de/jobs
Holstein Kiel | https://www.holstein-kiel.de/verein/karriere/
VfL Bochum | https://jobs.vfl-bochum.de/jobs
Hamburger SV | https://www.hsv.de/unser-hsv/karriere-beim-hsv/jobs/festanstellungen
1. FC Köln | https://effzeh.jobs.personio.de

### France
Paris Saint-Germain | https://parissaintgermain.wd3.myworkdayjobs.com/fr-FR/rejoigneznous
Olympique de Marseille | https://olympique-de-marseille.taleez.com/
AS Monaco | (no careers page — search layers only)
Olympique Lyonnais | https://careers.eaglefootballgroup.com/search
Lille OSC | https://www.losc.fr/losc-espace-carriere
OGC Nice | (no careers page — search layers only)
RC Lens | (no careers page — search layers only)
Stade Rennais FC | https://www.hellowork.com/fr-fr/entreprises/stade-rennais-football-club-170554.html#offres-emploi
Stade Brestois 29 | https://www.indeed.com/cmp/Stade-Brestois-29/jobs
Toulouse FC | https://fr.indeed.com/q-toulouse-football-club-emplois.html?vjk=234ef2c7bfeb4f7e
RC Strasbourg Alsace | https://sportsjobs.fr/companyprofile?company=racing-club-de-strasbourg-alsace-6930244b42a23784be612196
FC Nantes | https://www.fcnantes.com/articles/article2809.php?num=48817
Montpellier HSC | (no careers page — search layers only)
AJ Auxerre | (no careers page — search layers only)
Le Havre AC | (no careers page — search layers only)
Angers SCO | (no careers page — search layers only)
FC Metz | https://www.fcmetz.com/fr/contact
FC Lorient | https://www.fclorient.bzh/nous-rejoindre/

### Spain - La Liga
Real Madrid CF | https://eujobs.legendsglobal.com/jobs?location_id=1198105
FC Barcelona | (no careers page — search layers only)
Valencia CF | https://www.valenciacf.com/rrhh
Club Atletico de Madrid | https://www.atleticodemadrid.com/ofertas-de-trabajo
Real Betis Balompie | (no careers page — search layers only)
Sevilla FC | https://sevillafc.es/es/el-club/trabaja-con-nosotros
Real Sociedad | (no careers page — search layers only)
Athletic Club Bilbao | (no careers page — search layers only)
RCD Mallorca | (no careers page — search layers only)
Villarreal CF | https://villarrealcf.es/trabaja-con-nosotros/
RC Celta de Vigo | https://rccelta.es/en/grupo-rccelta/trabaja-con-nosotros/
CA Osasuna | (no careers page — search layers only)
Rayo Vallecano | (no careers page — search layers only)
Elche CF | https://academy.elchecf.es/en/work-with-us/
Getafe CF | (no careers page — search layers only)
Girona FC | https://www.gironafc.cat/en/work-with-us
Deportivo Alaves | https://deportivoalaves.com/trabaja-con-nosotros
Levante UD | (no careers page — search layers only)
Real Oviedo | https://www.realoviedo.es/empleo
RCD Espanyol | https://www.rcdespanyol.com/en/work-with-us

### Spain - La Liga 2
Real Racing Santander | (no careers page — search layers only)
UD Las Palmas | (no careers page — search layers only)
UD Almeria | (no careers page — search layers only)
Malaga CF | https://www.impulsyn.com/organizacion/malaga-club-de-futbol/empleo
CD Castellon | (no careers page — search layers only)
RC Deportivo de La Coruna | (no careers page — search layers only)
Burgos CF | https://www.burgoscf.es/forma-parte-del-equipo-del-burgos-club-de-futbol
SD Eibar | https://www.sdeibar.com/empleo
Cordoba CF | https://www.infojobs.net/cordoba-club-de-futbol-sad/em-i97495253534949677982680012053389517751
FC Andorra | (no careers page — search layers only)
Real Sporting de Gijon | (no careers page — search layers only)
Albacete Balompie | (no careers page — search layers only)
Granada CF | https://www.granadacf.es/trabaja-con-nosotros
Real Valladolid CF | https://www.realvalladolid.es/trabaja-con-nosotros
CD Leganes | https://www.infojobs.net/club-deportivo-leganes-sa-d/em-i97505653505948677685668023214499200069
Cadiz CF | https://www.cadizcf.com/oferta-de-empleo
Real Zaragoza | https://www.realzaragoza.com/trabaja-con-nosotros

### England - Premier League
Arsenal FC | https://careers.arsenal.com/jobs
Manchester City FC | https://careers.cityfootballgroup.com/
Manchester United FC | https://www.candidatemanager.net/cm/p/pJobs.aspx?mid=YFDU&sid=BBUU
Liverpool FC | https://jobsearch.liverpoolfc.com/
Aston Villa FC | https://avfc.wd502.myworkdayjobs.com/avfc_careers
AFC Bournemouth | https://careers.afcb.co.uk/
Brentford FC | https://hiring.brentfordfc.com/jobs
Brighton & Hove Albion FC | https://www.brightonandhovealbion.com/career-opportunities
Chelsea FC | https://secure.workforceready.eu/ta/6189861.careers?CareersSearch=&lang=en-GB
Everton FC | https://careers.evertonfc.com/vacancies
Fulham FC | https://fulhamfc.careers.hibob.com/jobs
Sunderland AFC | https://sunderlandafc.talosats-careers.com/vacancies
Newcastle United FC | https://careers.newcastleunited.com/jobs
Leeds United FC | https://www.leedsunited.com/en/club/careers
Crystal Palace FC | https://careers.cpfc.co.uk/jobs
Nottingham Forest FC | https://careers.nottinghamforest.co.uk/jobs
Tottenham Hotspur FC | https://ce0812li.webitrent.com/ce0812li_webrecruitment/wrd/run/etrec179gf.open?wvid=9447152BOp
West Ham United FC | https://www.whufc.com/en/the-club/careers
Burnley FC | https://careers.burnleyfootballclub.com/
Wolverhampton Wanderers FC | https://www.wolves.co.uk/club/vacancies/

### England - Championship
Birmingham City FC | https://www.bcfc.com/club/careers/
Blackburn Rovers FC | https://www.rovers.co.uk/club/job-vacancies
Bristol City FC | https://www.bristol-sport.co.uk/careers/bristol-city/
Charlton Athletic FC | https://www.charltonafc.com/vacancies
Coventry City FC | https://coventrycityfootballclub.teamtailor.com/jobs
Derby County FC | https://www.dcfc.co.uk/page/permanent-roles
Hull City AFC | https://www.wearehullcity.co.uk/club/careers
Ipswich Town FC | https://www.itfc.co.uk/club/careers/vacancies
Leicester City FC | https://www.lcfc.com/vacancies
Middlesbrough FC | https://www.mfc.co.uk/careers/
Millwall FC | https://www.millwallfc.co.uk/club-information/work-for-the-lions
Norwich City FC | https://careers.canaries.co.uk/
Oxford United FC | https://www.oufc.co.uk/vacancies-oxford-united
Portsmouth FC | https://www.portsmouthfc.co.uk/club/work-for-us
Preston North End FC | https://www.pnefc.net/pnecet/
Queens Park Rangers FC | https://www.qpr.co.uk/club/careers
Sheffield United FC | https://www.sufc.co.uk/club/vacancies/
Sheffield Wednesday FC | https://www.swfc.co.uk/club/careers/
Southampton FC | https://saintsfc.wd3.myworkdayjobs.com/SFC001
Stoke City FC | https://www.stokecityfc.com/
Swansea City AFC | https://www.swanseacity.com/news/permanent-roles-full-timepart-time
Watford FC | https://www.watfordfc.com/club/careers
West Bromwich Albion FC | https://www.wba.co.uk/club/vacancies
Wrexham AFC | https://careers.wrexhamafc.co.uk/vacancies

### Italy - Serie A
Inter Milan | https://www.inter.it/en/club/job-opportunities
SSC Napoli | https://www.sscnapoli.it/static/page/lavora-con-noi.aspx
AC Milan | https://www.acmilan.com/en/club/work-with-us
Juventus FC | https://www.juventus.com/it/club/careers/
AS Roma | https://asroma.altamiraweb.com/
Como 1907 | https://www.como1907.com/en/careers
Atalanta BC | https://www.atalanta.it/it/club/lavora-con-noi
SS Lazio | https://www.sslazio.it/it/club/lavora-con-noi
Bologna FC 1909 | (no careers page — search layers only)
ACF Fiorentina | (no careers page — search layers only)
Torino FC | (no careers page — search layers only)
Udinese Calcio | (no careers page — search layers only)
Parma Calcio 1913 | https://www.parmacalcio1913.com/lavora-con-noi/
Genoa CFC | (no careers page — search layers only)
Cagliari Calcio | (no careers page — search layers only)
Hellas Verona FC | (no careers page — search layers only)
US Lecce | (no careers page — search layers only)
US Cremonese | https://uscremonese.it/lavoraconoi/
Sassuolo Calcio | (no careers page — search layers only)
Pisa SC | (no careers page — search layers only)

### Italy - Serie B
US Avellino | (no careers page — search layers only)
SSC Bari | (no careers page — search layers only)
Carrarese Calcio | (no careers page — search layers only)
US Catanzaro | (no careers page — search layers only)
Cesena FC | (no careers page — search layers only)
Empoli FC | (no careers page — search layers only)
Frosinone Calcio | (no careers page — search layers only)
SS Juve Stabia | (no careers page — search layers only)
Mantova 1911 | (no careers page — search layers only)
Modena FC | (no careers page — search layers only)
AC Monza | (no careers page — search layers only)
Calcio Padova | https://www.padovacalcio.it/lavora-con-noi/
Palermo FC | (no careers page — search layers only)
Delfino Pescara | (no careers page — search layers only)
AC Reggiana | (no careers page — search layers only)
UC Sampdoria | (no careers page — search layers only)
Spezia Calcio | (no careers page — search layers only)
FC Sudtirol | (no careers page — search layers only)
Venezia FC | (no careers page — search layers only)
Virtus Entella | (no careers page — search layers only)

### Scotland
Rangers FC | https://uk.indeed.com/cmp/Rangers-Football-Club/jobs
Celtic FC | https://www.celticfc.com/club/jobs-at-celtic/permanent-and-fixed-term-roles/

### Portugal
SL Benfica | https://recrutamento.slbenfica.pt/go/Job-Opportunities/9183055/?locale=en_US
Sporting CP | https://www.sporting.pt/pt/venha-trabalhar-connosco
FC Porto | https://candidaturas.fcporto.pt/

### Denmark
FC Copenhagen | https://www.fck.dk/en/jobs-and-careers
FC Midtjylland | https://www.fcm.dk/klubben/karriere/

_Total: 176 clubs across 13 league groups._
</CLUBS>

## 2. How to search each club (stop at the first layer that yields results)

L1 — The club's own careers page. Fetch it and read the job list. Some pages render
     the list from embedded JSON rather than `<a>` links (Jobtoolz clubs put it in an
     `x-data="window.jobComponent([...])"` attribute) — parse that JSON if present.

L2 — The club's ATS, when the careers URL points at one. Read the tenant slug out of
     the careers URL (never guess it) and hit the public JSON endpoint:
       Teamtailor      https://<slug>.teamtailor.com/jobs.json
       Workable        https://apply.workable.com/api/v1/widget/accounts/<slug>/jobs
       Greenhouse      https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true
       Lever           https://api.lever.co/v0/postings/<slug>?mode=json
       Personio        https://<slug>.jobs.personio.de/search.json
       Workday         https://<host>/wday/cxs/<org>/<board>/jobs   (POST)
       Talos360        https://api-careers-sites.talos360.com
       HiBob           https://<host>/api/job-ad
     Also seen in this space: Recruitee, SuccessFactors, softgarden, HRworks, Pinpoint,
     Posting Panda, webitrent, CoreHR/WorkforceReady, Hellowork.

L3 — Web search, ONLY for clubs where L1 and L2 found nothing (mostly Serie A/B and
     parts of La Liga / Ligue 1). Query e.g.
       "<club name>" football (analyst OR "data scientist" OR analytics OR analista OR analyste)
     Accept a result only if the club's own name appears in the title or snippet, and
     the URL is on the club's domain or a known ATS / job-board host. Reject
     LinkedIn /posts/ reshares — only /jobs/view/ pages count.

L4 — Football job boards: livefootballjobs.com, eurofootjobs.com, workinsports.

Do not try to scrape LinkedIn search pages — it blocks automation and the results are
unreliable. Respect robots.txt. Space out requests. If a page won't load, say so in
the report rather than guessing what was on it.

## 3. What counts as a match

INCLUDE — the title names a data/analytics role, in any of EN, NL, DE, FR, ES, IT,
PT, DK. Match accent-insensitively ("données" == "donnees"):
  data analyst · data scientist · data engineer · machine learning · performance
  analyst · match/video/tactical/opposition/set-piece analyst · recruitment or
  scouting analyst · insights analyst/manager · head of data/analytics/insight/
  research · business intelligence · statistician · quantitative analyst · data
  scout · technical scout · sports analytics
  and their translations: data-analist, wedstrijdanalist, prestatieanalist,
  datenanalyst, leistungsanalyst, spielanalyst, analyste de données, analyste vidéo,
  analista de datos, analista de rendimiento, analista dati, analista tattico,
  analista de dados, cientista de dados, dataanalytiker, præstationsanalytiker …

ALSO INCLUDE — a data/analytics TOPIC word (data, analytics, analyse, insight,
intelligence, statistics, tracking data, event data, StatsBomb, Wyscout, SkillCorner,
InStat) paired with a real ROLE noun (analyst, scientist, engineer, manager, officer,
coordinator, specialist, lead, head, chief, intern, trainee, stagiair, werkstudent,
responsable, hoofd, jefe, capo …).

NEVER match on a topic word alone. "CLUB DATA" in a nav bar, or a JD that merely
lists "Python, SQL" as a skill, is not a vacancy.

EXCLUDE outright, even if the title says "analyst":
  finance · security · compliance · payroll · procurement · accounting · audit · HR ·
  physio · rehab · therapy · nutrition · medical · psychology · masseur ·
  master data management · data governance · data entry · data protection ·
  privacy/cookie/GDPR footer links.

SPORTS SCIENCE — include only when it leans data ("Sports Science Analyst",
"Performance Data Scientist"). A plain "Sports Scientist" or "S&C Coach" is out.

CONFIDENCE — mark each hit:
  high = an explicit data-role phrase, or the word "data", appears in the TITLE
  low  = matched only via a generic "analyst" token (e.g. "Business Analyst") or
         rescued from the description. Show it, but flag it.

## 4. Verify before reporting

For every candidate: open the posting URL and confirm the role is genuinely open
(not a closed archive page, not a generic careers landing page). Drop anything you
cannot open. Record the real posted date / closing date if the page shows one.

## 5. Output

A markdown report:

  A. Summary line — X roles at Y clubs across Z leagues, and the scan date.
  B. Table, most relevant first — Role | Club | League | Category | Confidence |
     Posted/Closing | Link. Category is one of: Data Science & ML, Analytics &
     Insights, Performance Analysis, Scouting & Recruitment, Sports Science.
     Rank Data Scientist / Data Analyst / ML above performance-analysis roles,
     and those above scouting and borderline hits.
  C. A "worth applying to first" shortlist of 5, with one line each on why.
  D. A "couldn't check" list — clubs whose page failed to load or blocked me,
     so I know what the scan missed.

Save the report to `scan-YYYY-MM-DD.md` in this folder. If a previous scan file
exists here, diff against it and open the report with what is NEW since that scan.

---

## Single club / ad-hoc check

For a one-off, skip the swarm and just check one club:

> Check `<CLUB>` for open data / analytics / performance-analysis roles.
> Read their careers page; if it runs on an ATS (Teamtailor, Greenhouse, Lever,
> Workable, Personio, Workday, Recruitee…), pull the ATS's public JSON instead of
> the rendered page. Include analyst / data scientist / data engineer / performance,
> match, video, tactical, opposition analyst / insights / BI roles in
> EN·NL·DE·FR·ES·IT·PT·DK. Exclude finance, HR, medical, physio, and plain
> sports-science or coaching roles. Open each posting to confirm it is live. Report:
> role, category, confidence (high if "data" or an explicit data-role phrase is in
> the title), date, link. No guesses — if you can't open it, say so.
