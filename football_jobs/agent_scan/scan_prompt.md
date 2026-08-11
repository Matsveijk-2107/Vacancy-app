# Football analytics job scan — agent run

This is the agent-driven counterpart to the Streamlit app. It does what the
**Refresh data** button does — scan every club, match data/analytics roles, dedupe,
report — but as a Claude agent run instead of `scraper.py`. It leans on two tools:

- **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** — the agent's web
  reach. Use its channels (web / search / GitHub / **LinkedIn** / social) for every
  lookup instead of scraping raw HTML yourself.
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

**Scan every club in this list — all of them.** Do not sample, batch-and-stop, or
skip a club because it looks quiet. If a club genuinely can't be reached, it goes in
the "couldn't check" list (section 5D) — never dropped silently. Account for every
club by name.

Each line gives two anchors per club:
`Club name | careers: <careers URL> | linkedin: <LinkedIn jobs URL>`.
**Check both for every club** — a club may post a role on its own site, on its
LinkedIn, or on only one of the two. `(search layers only)` means no curated careers
page was found, so lean on LinkedIn + L3/L4 for that club (and find its live careers
page first — see L0).

<CLUBS>
Format:  Club name | careers: <careers/ATS URL> | linkedin: <LinkedIn jobs URL>
Check BOTH anchors for every club. `(search layers only)` = no curated careers
page found — lean on LinkedIn + L3/L4 (and find the club's live careers page first).

### Netherlands
PSV | careers: https://werkenbij.psv.nl/ | linkedin: https://www.linkedin.com/company/psv/jobs/
Ajax | careers: https://werkenbij.ajax.nl/vacatures | linkedin: https://www.linkedin.com/company/afc-ajax/jobs/
AZ Alkmaar | careers: https://www.werkenbijaz.nl/vacatures | linkedin: https://www.linkedin.com/company/az-alkmaar/jobs/
Feyenoord | careers: https://www.feyenoord.com/nl/vacatures | linkedin: https://www.linkedin.com/company/feyenoord-rotterdam-nv/jobs/
FC Utrecht | careers: https://www.fcutrecht.nl/vacatures/ | linkedin: https://www.linkedin.com/company/fcutrecht/jobs/

### Belgium
Royal Antwerp FC | careers: https://www.royalantwerpfc.be/club/vacatures | linkedin: https://www.linkedin.com/company/royal-antwerp-fc/jobs/
Royale Union Saint-Gilloise | careers: https://rusg.brussels/en/jobs | linkedin: https://www.linkedin.com/company/royale-union-saint-gilloise/jobs/
RSC Anderlecht | careers: https://www.rsca.be/en/club/jobs | linkedin: https://www.linkedin.com/company/rsc-anderlecht/jobs/
KRC Genk | careers: https://www.krcgenk.be/nl/vacatures | linkedin: https://www.linkedin.com/company/krc-genk/jobs/
Club Brugge | careers: https://jobs.clubbrugge.be/nl | linkedin: https://www.linkedin.com/company/club-brugge-kv/jobs/

### Germany
FC Bayern Munich | careers: https://careers.fcbayern.com/go/Alle-Jobangebote-anzeigen/8774701/ | linkedin: https://www.linkedin.com/company/fcbayern/jobs/
Borussia Dortmund | careers: https://karriere.bvb.de/ | linkedin: https://www.linkedin.com/company/borussia-dortmund/jobs/
Bayer 04 Leverkusen | careers: https://www.bayer04.de/en-US/page/stellenangebote | linkedin: https://www.linkedin.com/company/bayer-04-leverkusen/jobs/
RB Leipzig | careers: https://rbleipzig.com/de/klub/rbl/karriere | linkedin: https://www.linkedin.com/company/rb-leipzig/jobs/
VfB Stuttgart | careers: https://www.vfb.de/de/1893/aktuell/jobs/jobs/ | linkedin: https://www.linkedin.com/company/vfb-stuttgart-1893-ag/jobs/
Eintracht Frankfurt | careers: https://klub.eintracht.de/jobs/ag/ | linkedin: https://www.linkedin.com/company/eintrachtfrankfurt/jobs/
SC Freiburg | careers: https://jobs.scfreiburg.com/en | linkedin: https://www.linkedin.com/company/sport-club-freiburg-e.v./jobs/
1. FSV Mainz 05 | careers: https://jobapplication.hrworks.de/de?companyId=ba8e529b | linkedin: https://www.linkedin.com/company/mainz05/jobs/
Borussia Mönchengladbach | careers: https://job.borussia.de/de | linkedin: https://www.linkedin.com/company/borussia/jobs/
VfL Wolfsburg | careers: https://www.vfl-wolfsburg.de/der-vfl/jobs/direkteinstieg | linkedin: https://www.linkedin.com/company/vfl-wolfsburg/jobs/
FC Augsburg | careers: https://jobs.fcaugsburg.de/de | linkedin: https://www.linkedin.com/company/fcaugsburg/jobs/
Werder Bremen | careers: https://karriere.werder.de/ | linkedin: https://www.linkedin.com/company/svwerderbremen/jobs/
TSG Hoffenheim | careers: https://www.tsg-hoffenheim.de/tsg/karriere/stellenangebote | linkedin: https://www.linkedin.com/company/tsg-1899-hoffenheim-fu%C3%9Fball-spielbetriebs-gmbh/jobs/
1. FC Union Berlin | careers: https://www.altefoersterei.berlin/en/career-OIiJ | linkedin: https://www.linkedin.com/company/fc-union-berlin/jobs/
FC St. Pauli | careers: https://jobs.fcstpauli.com/de | linkedin: https://www.linkedin.com/company/football-cooperative-st-pauli-von-2024-eg/jobs/
1. FC Heidenheim | careers: https://www.fc-heidenheim.de/jobs | linkedin: https://www.linkedin.com/company/fch1846/jobs/
Holstein Kiel | careers: https://www.holstein-kiel.de/verein/karriere/ | linkedin: https://www.linkedin.com/company/holstein-kiel/jobs/
VfL Bochum | careers: https://jobs.vfl-bochum.de/jobs | linkedin: https://www.linkedin.com/company/vflbochum1848/jobs/
Hamburger SV | careers: https://www.hsv.de/unser-hsv/karriere-beim-hsv/jobs/festanstellungen | linkedin: https://www.linkedin.com/company/hamburger-sport-verein/jobs/
1. FC Köln | careers: https://effzeh.jobs.personio.de | linkedin: https://www.linkedin.com/company/fckoeln/jobs/

### France
Paris Saint-Germain | careers: https://parissaintgermain.wd3.myworkdayjobs.com/fr-FR/rejoigneznous | linkedin: https://www.linkedin.com/company/paris-saint-germain/jobs/
Olympique de Marseille | careers: https://olympique-de-marseille.taleez.com/ | linkedin: https://www.linkedin.com/company/sasp-olympique-de-marseille/jobs/
AS Monaco | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/as-monaco/jobs/
Olympique Lyonnais | careers: https://careers.eaglefootballgroup.com/search | linkedin: https://www.linkedin.com/company/olympique-lyonnais-groupe/jobs/
Lille OSC | careers: https://www.losc.fr/losc-espace-carriere | linkedin: https://www.linkedin.com/company/loscofficiel/jobs/
OGC Nice | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/ogcnice/jobs/
RC Lens | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/racingclubdelens/jobs/
Stade Rennais FC | careers: https://www.hellowork.com/fr-fr/entreprises/stade-rennais-football-club-170554.html#offres-emploi | linkedin: https://www.linkedin.com/company/staderennaisfc/jobs/
Stade Brestois 29 | careers: https://www.indeed.com/cmp/Stade-Brestois-29/jobs | linkedin: https://www.linkedin.com/company/stade-brestois-29/jobs/
Toulouse FC | careers: https://fr.indeed.com/q-toulouse-football-club-emplois.html?vjk=234ef2c7bfeb4f7e | linkedin: https://www.linkedin.com/company/toulousefc/jobs/
RC Strasbourg Alsace | careers: https://sportsjobs.fr/companyprofile?company=racing-club-de-strasbourg-alsace-6930244b42a23784be612196 | linkedin: https://www.linkedin.com/company/racing-club-strasbourg-alsace/jobs/
FC Nantes | careers: https://www.fcnantes.com/articles/article2809.php?num=48817 | linkedin: https://www.linkedin.com/company/fc-nantes/jobs/
Montpellier HSC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/montpellier-herault-sc/jobs/
AJ Auxerre | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/aj-auxerre/jobs/
Le Havre AC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/havre-ac-foot/jobs/
Angers SCO | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/angerssco/jobs/
FC Metz | careers: https://www.fcmetz.com/fr/contact | linkedin: https://www.linkedin.com/company/fcmetz/jobs/
FC Lorient | careers: https://www.fclorient.bzh/nous-rejoindre/ | linkedin: https://www.linkedin.com/company/fc-lorient/jobs/

### Spain - La Liga
Real Madrid CF | careers: https://eujobs.legendsglobal.com/jobs?location_id=1198105 | linkedin: https://www.linkedin.com/company/realmadrid/jobs/
FC Barcelona | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/fc-barcelona/jobs/
Valencia CF | careers: https://www.valenciacf.com/rrhh | linkedin: https://www.linkedin.com/company/valencia-cf/jobs/
Club Atletico de Madrid | careers: https://www.atleticodemadrid.com/ofertas-de-trabajo | linkedin: https://www.linkedin.com/company/atleticodemadrid/jobs/
Real Betis Balompie | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/real-betis-balompie/jobs/
Sevilla FC | careers: https://sevillafc.es/es/el-club/trabaja-con-nosotros | linkedin: https://www.linkedin.com/company/sevillafc/jobs/
Real Sociedad | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/real-sociedad/jobs/
Athletic Club Bilbao | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/athleticclub/jobs/
RCD Mallorca | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/real-mallorca/jobs/
Villarreal CF | careers: https://villarrealcf.es/trabaja-con-nosotros/ | linkedin: https://www.linkedin.com/company/villarreal-cf-sad/jobs/
RC Celta de Vigo | careers: https://rccelta.es/en/grupo-rccelta/trabaja-con-nosotros/ | linkedin: https://www.linkedin.com/company/rccelta/jobs/
CA Osasuna | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/ca-osasuna/jobs/
Rayo Vallecano | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/rayo-vallecano-de-madrid-s-a-d/jobs/
Elche CF | careers: https://academy.elchecf.es/en/work-with-us/ | linkedin: https://www.linkedin.com/company/elche-cf-sad/jobs/
Getafe CF | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/getafe-c-f-s-a-d/jobs/
Girona FC | careers: https://www.gironafc.cat/en/work-with-us | linkedin: https://www.linkedin.com/company/gironafc/jobs/
Deportivo Alaves | careers: https://deportivoalaves.com/trabaja-con-nosotros | linkedin: https://www.linkedin.com/showcase/deportivo-alav%C3%A9s-sad/jobs/
Levante UD | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/levanteud/jobs/
Real Oviedo | careers: https://www.realoviedo.es/empleo | linkedin: https://www.linkedin.com/company/realoviedo/jobs/
RCD Espanyol | careers: https://www.rcdespanyol.com/en/work-with-us | linkedin: https://www.linkedin.com/company/rcd-espanyol-de-barcelona/jobs/

### Spain - La Liga 2
Real Racing Santander | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/realracingclub/jobs/
UD Las Palmas | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/ud-las-palmas-sad/jobs/
UD Almeria | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/ud-almer%C3%ADa/jobs/
Malaga CF | careers: https://www.impulsyn.com/organizacion/malaga-club-de-futbol/empleo | linkedin: https://www.linkedin.com/company/m%C3%A1laga-cf/jobs/
CD Castellon | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/club-deportivo-castell%C3%B3n-sad/jobs/
RC Deportivo de La Coruna | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/rcdeportivo/jobs/
Burgos CF | careers: https://www.burgoscf.es/forma-parte-del-equipo-del-burgos-club-de-futbol | linkedin: https://www.linkedin.com/company/burgos-cf/jobs/
SD Eibar | careers: https://www.sdeibar.com/empleo | linkedin: https://www.linkedin.com/company/sd-eibar/jobs/
Cordoba CF | careers: https://www.infojobs.net/cordoba-club-de-futbol-sad/em-i97495253534949677982680012053389517751 | linkedin: https://www.linkedin.com/company/cordobacf/jobs/
FC Andorra | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/fc-andorra/jobs/
Real Sporting de Gijon | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/realsporting/jobs/
Albacete Balompie | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/albacete-balompi%C3%A9/jobs/
Granada CF | careers: https://www.granadacf.es/trabaja-con-nosotros | linkedin: https://www.linkedin.com/company/granada-cf/jobs/
Real Valladolid CF | careers: https://www.realvalladolid.es/trabaja-con-nosotros | linkedin: https://www.linkedin.com/company/real-valladolid-club-de-f-tbol-s.a.d./jobs/
CD Leganes | careers: https://www.infojobs.net/club-deportivo-leganes-sa-d/em-i97505653505948677685668023214499200069 | linkedin: https://www.linkedin.com/company/club-deportivo-legan%C3%A9s/jobs/
Cadiz CF | careers: https://www.cadizcf.com/oferta-de-empleo | linkedin: https://www.linkedin.com/company/c-diz-cf/jobs/
Real Zaragoza | careers: https://www.realzaragoza.com/trabaja-con-nosotros | linkedin: https://www.linkedin.com/company/real-zaragoza/jobs/

### England - Premier League
Arsenal FC | careers: https://careers.arsenal.com/jobs | linkedin: https://www.linkedin.com/company/arsenal-f-c/jobs/
Manchester City FC | careers: https://careers.cityfootballgroup.com/ | linkedin: https://www.linkedin.com/company/manchester-city-football-club/jobs/
Manchester United FC | careers: https://www.candidatemanager.net/cm/p/pJobs.aspx?mid=YFDU&sid=BBUU | linkedin: https://www.linkedin.com/company/manchester-united/jobs/
Liverpool FC | careers: https://jobsearch.liverpoolfc.com/ | linkedin: https://www.linkedin.com/company/liverpool-football-club/jobs/
Aston Villa FC | careers: https://avfc.wd502.myworkdayjobs.com/avfc_careers | linkedin: https://www.linkedin.com/company/aston-villa-football-club/jobs/
AFC Bournemouth | careers: https://careers.afcb.co.uk/ | linkedin: https://www.linkedin.com/company/afc-bournemouth/jobs/
Brentford FC | careers: https://hiring.brentfordfc.com/jobs | linkedin: https://www.linkedin.com/company/brentford-football-club/jobs/
Brighton & Hove Albion FC | careers: https://www.brightonandhovealbion.com/career-opportunities | linkedin: https://www.linkedin.com/company/brighton-&-hove-albion-fc/jobs/
Chelsea FC | careers: https://secure.workforceready.eu/ta/6189861.careers?CareersSearch=&lang=en-GB | linkedin: https://www.linkedin.com/company/chelsea-football-club/jobs/
Everton FC | careers: https://careers.evertonfc.com/vacancies | linkedin: https://www.linkedin.com/company/everton-football-club/jobs/
Fulham FC | careers: https://fulhamfc.careers.hibob.com/jobs | linkedin: https://www.linkedin.com/company/fulham-fc/jobs/
Sunderland AFC | careers: https://sunderlandafc.talosats-careers.com/vacancies | linkedin: https://www.linkedin.com/company/sunderlandafc/jobs/
Newcastle United FC | careers: https://careers.newcastleunited.com/jobs | linkedin: https://www.linkedin.com/company/newcastle-united-football-club/jobs/
Leeds United FC | careers: https://www.leedsunited.com/en/club/careers | linkedin: https://www.linkedin.com/company/leedsunited/jobs/
Crystal Palace FC | careers: https://careers.cpfc.co.uk/jobs | linkedin: https://www.linkedin.com/company/crystal-palace-football-club/jobs/
Nottingham Forest FC | careers: https://careers.nottinghamforest.co.uk/jobs | linkedin: https://www.linkedin.com/company/nottingham-forest-fc/jobs/
Tottenham Hotspur FC | careers: https://ce0812li.webitrent.com/ce0812li_webrecruitment/wrd/run/etrec179gf.open?wvid=9447152BOp | linkedin: https://www.linkedin.com/company/tottenham-hotspur-ltd/jobs/
West Ham United FC | careers: https://www.whufc.com/en/the-club/careers | linkedin: https://www.linkedin.com/company/west-ham-united/jobs/
Burnley FC | careers: https://careers.burnleyfootballclub.com/ | linkedin: https://www.linkedin.com/company/burnleyofficial/jobs/
Wolverhampton Wanderers FC | careers: https://www.wolves.co.uk/club/vacancies/ | linkedin: https://www.linkedin.com/company/wolverhampton-wanderers-fc/jobs/

### England - Championship
Birmingham City FC | careers: https://www.bcfc.com/club/careers/ | linkedin: https://www.linkedin.com/company/birmingham-city-fc/jobs/
Blackburn Rovers FC | careers: https://www.rovers.co.uk/club/job-vacancies | linkedin: https://www.linkedin.com/company/blackburn-rovers-football-club/jobs/
Bristol City FC | careers: https://www.bristol-sport.co.uk/careers/bristol-city/ | linkedin: https://www.linkedin.com/company/bristol-city-football-club/jobs/
Charlton Athletic FC | careers: https://www.charltonafc.com/vacancies | linkedin: https://www.linkedin.com/company/charlton-athletic-football-club/jobs/
Coventry City FC | careers: https://coventrycityfootballclub.teamtailor.com/jobs | linkedin: https://www.linkedin.com/company/coventry-city-football-club/jobs/
Derby County FC | careers: https://www.dcfc.co.uk/page/permanent-roles | linkedin: https://www.linkedin.com/company/derby-county-football-club/jobs/
Hull City AFC | careers: https://www.wearehullcity.co.uk/club/careers | linkedin: https://www.linkedin.com/company/hull-city/jobs/
Ipswich Town FC | careers: https://www.itfc.co.uk/club/careers/vacancies | linkedin: https://www.linkedin.com/company/ipswich-town-fc/jobs/
Leicester City FC | careers: https://www.lcfc.com/vacancies | linkedin: https://www.linkedin.com/company/leicester-city-football-club/jobs/
Middlesbrough FC | careers: https://www.mfc.co.uk/careers/ | linkedin: https://www.linkedin.com/company/middlesbrough-fc/jobs/
Millwall FC | careers: https://www.millwallfc.co.uk/club-information/work-for-the-lions | linkedin: https://www.linkedin.com/company/millwall-football-club/jobs/
Norwich City FC | careers: https://careers.canaries.co.uk/ | linkedin: https://www.linkedin.com/company/norwich-city-football-club/jobs/
Oxford United FC | careers: https://www.oufc.co.uk/vacancies-oxford-united | linkedin: https://www.linkedin.com/company/oufc1893/jobs/
Portsmouth FC | careers: https://www.portsmouthfc.co.uk/club/work-for-us | linkedin: https://www.linkedin.com/company/portsmouth-football-club/jobs/
Preston North End FC | careers: https://www.pnefc.net/pnecet/ | linkedin: https://www.linkedin.com/company/pnefcofficial/jobs/
Queens Park Rangers FC | careers: https://www.qpr.co.uk/club/careers | linkedin: https://www.linkedin.com/company/qprfc/jobs/
Sheffield United FC | careers: https://www.sufc.co.uk/club/vacancies/ | linkedin: https://www.linkedin.com/company/sheffieldunited/jobs/
Sheffield Wednesday FC | careers: https://www.swfc.co.uk/club/careers/ | linkedin: https://www.linkedin.com/company/sheffield-wednesday-football-club/jobs/
Southampton FC | careers: https://saintsfc.wd3.myworkdayjobs.com/SFC001 | linkedin: https://www.linkedin.com/company/southampton-football-club/jobs/
Stoke City FC | careers: https://www.stokecityfc.com/ | linkedin: https://www.linkedin.com/company/stoke-city-football-club/jobs/
Swansea City AFC | careers: https://www.swanseacity.com/news/permanent-roles-full-timepart-time | linkedin: https://www.linkedin.com/company/swansea-city-football-club/jobs/
Watford FC | careers: https://www.watfordfc.com/club/careers | linkedin: https://www.linkedin.com/company/watford-football-club/jobs/
West Bromwich Albion FC | careers: https://www.wba.co.uk/club/vacancies | linkedin: https://www.linkedin.com/company/west-bromwich-albion-football-club/jobs/
Wrexham AFC | careers: https://careers.wrexhamafc.co.uk/vacancies | linkedin: https://www.linkedin.com/company/wrexhamafc/jobs/

### Italy - Serie A
Inter Milan | careers: https://www.inter.it/en/club/job-opportunities | linkedin: https://www.linkedin.com/company/fc-internazionale-milano/jobs/
SSC Napoli | careers: https://www.sscnapoli.it/static/page/lavora-con-noi.aspx | linkedin: https://www.linkedin.com/company/sscnapoli/jobs/
AC Milan | careers: https://www.acmilan.com/en/club/work-with-us | linkedin: https://www.linkedin.com/company/ac-milan/jobs/
Juventus FC | careers: https://www.juventus.com/it/club/careers/ | linkedin: https://www.linkedin.com/company/juventus-football-club/jobs/
AS Roma | careers: https://asroma.altamiraweb.com/ | linkedin: https://www.linkedin.com/company/as-roma/jobs/
Como 1907 | careers: https://www.como1907.com/en/careers | linkedin: https://www.linkedin.com/company/como-1907/jobs/
Atalanta BC | careers: https://www.atalanta.it/it/club/lavora-con-noi | linkedin: https://www.linkedin.com/company/atalantabc/jobs/
SS Lazio | careers: https://www.sslazio.it/it/club/lavora-con-noi | linkedin: https://www.linkedin.com/company/sslaziospa/jobs/
Bologna FC 1909 | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/bologna-f-c-1909-s-p-a-/jobs/
ACF Fiorentina | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/acf-fiorentina-s-p-a-/jobs/
Torino FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/torino-football-club/jobs/
Udinese Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/udinese-calcio-spa/jobs/
Parma Calcio 1913 | careers: https://www.parmacalcio1913.com/lavora-con-noi/ | linkedin: https://www.linkedin.com/company/parma-calcio-1913/jobs/
Genoa CFC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/genoa-cricket-and-football-club-s.p.a./jobs/
Cagliari Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/cagliari-calcio/jobs/
Hellas Verona FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/hellas-verona-f-c-/jobs/
US Lecce | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/uslecce/jobs/
US Cremonese | careers: https://uscremonese.it/lavoraconoi/ | linkedin: https://www.linkedin.com/company/uscremonese/jobs/
Sassuolo Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/sassuolocalcio/jobs/
Pisa SC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/pisa-sporting-club-1909/jobs/

### Italy - Serie B
US Avellino | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/u-s-avellino-1912/jobs/
SSC Bari | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/ssc-bari/jobs/
Carrarese Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/carrarese-calcio-1908/jobs/
US Catanzaro | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/uscatanzaro1929/jobs/
Cesena FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/cesenafc/jobs/
Empoli FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/empoli-fc/jobs/
Frosinone Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/frosinone-calcio-s.r.l./jobs/
SS Juve Stabia | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/s.s.-juve-stabia-s.r.l./jobs/
Mantova 1911 | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/mantova-1911-s-r-l/jobs/
Modena FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/modena-football-club/jobs/
AC Monza | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/acmonza/jobs/
Calcio Padova | careers: https://www.padovacalcio.it/lavora-con-noi/ | linkedin: https://www.linkedin.com/company/calcio-padova/jobs/
Palermo FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/palermocalcio/jobs/
Delfino Pescara | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/pescaracalcio/jobs/
AC Reggiana | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/acreggiana1919/jobs/
UC Sampdoria | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/u-c--sampdoria/jobs/
Spezia Calcio | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/spezia-calcio-s.r.l.---societa-sportiva-professionistica/jobs/
FC Sudtirol | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/fc-s%C3%BCdtirol/jobs/
Venezia FC | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/veneziafc/jobs/
Virtus Entella | careers: (no careers page — search layers only) | linkedin: https://www.linkedin.com/company/virtus-entella/jobs/

### Scotland
Rangers FC | careers: https://uk.indeed.com/cmp/Rangers-Football-Club/jobs | linkedin: https://www.linkedin.com/company/rangersfc/jobs/
Celtic FC | careers: https://www.celticfc.com/club/jobs-at-celtic/permanent-and-fixed-term-roles/ | linkedin: https://www.linkedin.com/company/celtic-football-club/jobs/

### Portugal
SL Benfica | careers: https://recrutamento.slbenfica.pt/go/Job-Opportunities/9183055/?locale=en_US | linkedin: https://www.linkedin.com/company/sport-lisboa-e-benfica/jobs/
Sporting CP | careers: https://www.sporting.pt/pt/venha-trabalhar-connosco | linkedin: https://www.linkedin.com/company/sporting-clube-de-portugal/jobs/
FC Porto | careers: https://candidaturas.fcporto.pt/ | linkedin: https://www.linkedin.com/company/fcporto/jobs/

### Denmark
FC Copenhagen | careers: https://www.fck.dk/en/jobs-and-careers | linkedin: https://www.linkedin.com/company/f-c--k%C3%B8benhavn/jobs/
FC Midtjylland | careers: https://www.fcm.dk/klubben/karriere/ | linkedin: https://www.linkedin.com/company/fc-midtjylland/jobs/

_Total: 176 clubs across 13 league groups._
</CLUBS>

## 2. How to search each club

For **every** club, cover its OWN sources (L1/L2) **and** its LinkedIn (L-LI). Run
L3/L4 as a fallback when those come up empty. Research each club deeply — don't give
up on a stale URL; find the current one.

L0 — Confirm the club's CURRENT careers URL. Careers pages move and slugs change. If
     the stored `careers:` URL 404s, redirects to a generic landing page, or is
     `(search layers only)`, find the club's live careers/ATS page first — search
     `"<club>" (careers OR vacatures OR stellenangebote OR "lavora con noi" OR empleo)`
     — and use that. Note in the report when you had to correct a URL.

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

L-LI — The club's LinkedIn. Use the `agent-reach` LinkedIn/social channel (fall back
     to web search when that channel isn't configured). Cover BOTH of these, for every
     club — many clubs, especially the `(search layers only)` ones, post roles ONLY on
     LinkedIn:
       (a) the club's LinkedIn **jobs page** (the `linkedin:` URL on the club's line) —
           read the roles currently listed there; and
       (b) recent LinkedIn **posts / announcements** from the club that name a specific
           open vacancy (a "we're hiring: Data Analyst — apply here" post). Accept a
           post only when it names a specific role AND gives an apply link or a clear
           route to apply; ignore generic reshares, articles, and vague "join us"
           posts with no named role.
     Treat LinkedIn as lower-trust than the club's own site: open and verify the
     underlying posting (section 4), and set confidence accordingly. Don't scrape
     LinkedIn *search-results* pages (they block automation) — go via the club's own
     LinkedIn jobs page / feed through the agent-reach channel.

L3 — Web search, for clubs where L1/L2/L-LI still found nothing (mostly Serie A/B and
     parts of La Liga / Ligue 1). Query e.g.
       "<club name>" football (analyst OR "data scientist" OR analytics OR analista OR analyste)
     Accept a result only if the club's own name appears in the title or snippet, and
     the URL is on the club's domain or a known ATS / job-board host. For LinkedIn hits
     here, prefer `/jobs/view/` postings over reshared feed articles.

L4 — Football job boards: livefootballjobs.com, eurofootjobs.com, workinsports.

Respect robots.txt. Space out requests. If a page won't load, say so in the report
rather than guessing what was on it.

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
     Source | Posted/Closing | Link. Category is one of: Data Science & ML, Analytics
     & Insights, Performance Analysis, Scouting & Recruitment, Sports Science. Source
     is where the role was found: Own site, ATS, LinkedIn (jobs), LinkedIn (post), or
     Job board. Rank Data Scientist / Data Analyst / ML above performance-analysis
     roles, and those above scouting and borderline hits.
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
