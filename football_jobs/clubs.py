# clubs.py
# ============================================================
# Master list of football clubs for the vacancy tracker app.
#
# Each club dict contains:
#   name             : Display name of the club
#   country          : Country
#   league           : League / division
#   careers_url      : Direct URL to the club's careers/vacancies page.
#                      None = no dedicated page found; use search layers only.
#   teamtailor_slug  : Set when club uses Teamtailor ATS (subdomain prefix)
#   linkedin_company : Exact company name as it appears on LinkedIn
#   notes            : Scraper hints, ownership context, analytics culture flags
#
# URL STATUS IN COMMENTS:
#   [live]        - URL fetched and page confirmed responsive
#   [confirmed]   - URL confirmed via live search result snippet
#   [best-guess]  - URL inferred from site structure; validate on first run
#   [search-only] - No dedicated page found; rely on search layers only
# ============================================================

CLUBS = [

    # ================================================================= #
    #  NETHERLANDS                                                        #
    # ================================================================= #
    {
        "name": "PSV",
        "country": "Netherlands",
        "league": "Eredivisie",
        "careers_url": "https://werkenbij.psv.nl/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "PSV",
        "linkedin_jobs_url": "https://www.linkedin.com/company/psv/jobs/",
        "notes": "Main careers page confirmed by user.",
    },
    {
        "name": "Ajax",
        "country": "Netherlands",
        "league": "Eredivisie",
        "careers_url": "https://werkenbij.ajax.nl/vacatures",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "AFC Ajax",
        "linkedin_jobs_url": "https://www.linkedin.com/company/afc-ajax/jobs/",
        "notes": None,
    },
    {
        "name": "AZ Alkmaar",
        "country": "Netherlands",
        "league": "Eredivisie",
        "careers_url": "https://www.werkenbijaz.nl/vacatures",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "AZ",
        "linkedin_jobs_url": "https://www.linkedin.com/company/az/jobs/",
        "notes": "Strong data culture.",
    },
    {
        "name": "Feyenoord",
        "country": "Netherlands",
        "league": "Eredivisie",
        "careers_url": "https://www.feyenoord.com/nl/vacatures",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Feyenoord Rotterdam",
        "linkedin_jobs_url": "https://www.linkedin.com/company/feyenoord-rotterdam-nv/jobs/",
        "notes": "vacatures.feyenoord.nl redirects here.",
    },
    {
        "name": "FC Utrecht",
        "country": "Netherlands",
        "league": "Eredivisie",
        "careers_url": "https://www.fcutrecht.nl/vacatures/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC Utrecht",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-utrecht/jobs/",
        "notes": None,
    },

    # ================================================================= #
    #  BELGIUM                                                            #
    # ================================================================= #
    {
        "name": "Royal Antwerp FC",
        "country": "Belgium",
        "league": "Jupiler Pro League",
        "careers_url": "https://www.royalantwerpfc.be/club/vacatures",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Royal Antwerp FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/royal-antwerp-fc/jobs/",
        "notes": None,
    },
    {
        "name": "Royale Union Saint-Gilloise",
        "country": "Belgium",
        "league": "Jupiler Pro League",
        "careers_url": "https://rusg.brussels/en/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Royale Union Saint-Gilloise",
        "linkedin_jobs_url": "https://www.linkedin.com/company/royale-union-saint-gilloise/jobs/",
        "notes": "Brighton-affiliated.",
    },
    {
        "name": "RSC Anderlecht",
        "country": "Belgium",
        "league": "Jupiler Pro League",
        "careers_url": "https://www.rsca.be/en/club/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "RSC Anderlecht",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rsc-anderlecht/jobs/",
        "notes": None,
    },
    {
        "name": "KRC Genk",
        "country": "Belgium",
        "league": "Jupiler Pro League",
        "careers_url": "https://www.krcgenk.be/nl/vacatures",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "KRC Genk",
        "linkedin_jobs_url": "https://www.linkedin.com/company/krc-genk/jobs/",
        "notes": "Strong analytics culture.",
    },
    {
        "name": "Club Brugge",
        "country": "Belgium",
        "league": "Jupiler Pro League",
        "careers_url": "https://jobs.clubbrugge.be/nl",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Club Brugge KV",
        "linkedin_jobs_url": "https://www.linkedin.com/company/club-brugge-kv/jobs/",
        "notes": "Also accessible via clubbrugge.be/en/vacancies.",
    },

    # ================================================================= #
    #  GERMANY - Bundesliga                                               #
    # ================================================================= #
    {
        "name": "FC Bayern Munich",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://careers.fcbayern.com/go/Alle-Jobangebote-anzeigen/8774701/",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "FC Bayern MÃ¼nchen",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fcbayern/jobs/",
        "notes": "URL confirmed by user. Main portal: careers.fcbayern.com",
    },
    {
        "name": "Borussia Dortmund",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://karriere.bvb.de/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Borussia Dortmund",
        "linkedin_jobs_url": "https://www.linkedin.com/company/borussia-dortmund/jobs/",
        "notes": "Dedicated careers subdomain karriere.bvb.de.",
    },
    {
        "name": "Bayer 04 Leverkusen",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.bayer04.de/en-US/page/stellenangebote",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Bayer 04 Leverkusen",
        "linkedin_jobs_url": "https://www.linkedin.com/company/bayer-04-leverkusen/jobs/",
        "notes": None,
    },
    {
        "name": "RB Leipzig",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://rbleipzig.com/de/klub/rbl/karriere",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "RB Leipzig",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rb-leipzig/jobs/",
        "notes": "Note: /de/ is added by redirect. Red Bull network.",
    },
    {
        "name": "VfB Stuttgart",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.vfb.de/de/1893/aktuell/jobs/jobs/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "VfB Stuttgart",
        "linkedin_jobs_url": "https://www.linkedin.com/company/vfb-stuttgart-1893-ag/jobs/",
        "notes": None,
    },
    {
        "name": "Eintracht Frankfurt",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://klub.eintracht.de/jobs/ag/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Eintracht Frankfurt",
        "linkedin_jobs_url": "https://www.linkedin.com/company/eintrachtfrankfurt/jobs/",
        "notes": None,
    },
    {
        "name": "SC Freiburg",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://jobs.scfreiburg.com/en",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Sport-Club Freiburg",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sport-club-freiburg-e.v./jobs/",
        "notes": None,
    },
    {
        "name": "1. FSV Mainz 05",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://jobapplication.hrworks.de/de?companyId=ba8e529b",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "1. FSV Mainz 05",
        "linkedin_jobs_url": "https://www.linkedin.com/company/mainz05/jobs/",
        "notes": None,
    },
    {
        "name": "Borussia MÃ¶nchengladbach",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://job.borussia.de/de",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Borussia MÃ¶nchengladbach",
        "linkedin_jobs_url": "https://www.linkedin.com/company/borussia/jobs/",
        "notes": None,
    },
    {
        "name": "VfL Wolfsburg",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.vfl-wolfsburg.de/der-vfl/jobs/direkteinstieg",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "VfL Wolfsburg",
        "linkedin_jobs_url": "https://www.linkedin.com/company/vfl-wolfsburg/jobs/",
        "notes": "Volkswagen-owned.",
    },
    {
        "name": "FC Augsburg",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://jobs.fcaugsburg.de/de",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC Augsburg",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fcaugsburg/jobs/",
        "notes": "Uses HRworks ATS at jobs.fcaugsburg.de (same system as St. Pauli).",
    },
    {
        "name": "Werder Bremen",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://karriere.werder.de/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "SV Werder Bremen",
        "linkedin_jobs_url": "https://www.linkedin.com/company/svwerderbremen/jobs/",
        "notes": None,
    },
    {
        "name": "TSG Hoffenheim",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.tsg-hoffenheim.de/tsg/karriere/stellenangebote",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "TSG 1899 Hoffenheim",
        "linkedin_jobs_url": "https://www.linkedin.com/company/tsg-1899-hoffenheim-fu%C3%9Fball-spielbetriebs-gmbh/jobs/",
        "notes": "Strong analytics culture (SAP partnership). High priority.",
    },
    {
        "name": "1. FC Union Berlin",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.altefoersterei.berlin/en/career-OIiJ",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "1. FC Union Berlin",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-union-berlin/jobs/",
        "notes": "Sub-pages have random slugs (/vollzeit-Q8DA etc); scraper should list all /de/jobs/* URLs.",
    },
    {
        "name": "FC St. Pauli",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://jobs.fcstpauli.com/de",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC St. Pauli",
        "linkedin_jobs_url": "https://www.linkedin.com/company/football-cooperative-st-pauli-von-2024-eg/jobs/",
        "notes": "Uses HRworks ATS at jobs.fcstpauli.com.",
    },
    {
        "name": "1. FC Heidenheim",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.fc-heidenheim.de/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "1. FC Heidenheim 1846",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fch1846/jobs/",
        "notes": None,
    },
    {
        "name": "Holstein Kiel",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://www.holstein-kiel.de/verein/karriere/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Holstein Kiel",
        "linkedin_jobs_url": "https://www.linkedin.com/company/holstein-kiel/jobs/",
        "notes": None,
    },
    {
        "name": "VfL Bochum",
        "country": "Germany",
        "league": "Bundesliga",
        "careers_url": "https://jobs.vfl-bochum.de/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "VfL Bochum 1848",
        "linkedin_jobs_url": "https://www.linkedin.com/company/vflbochum1848/jobs/",
        "notes": "Uses Talention ATS at jobs.vfl-bochum.de.",
    },
    {
        "name": "Hamburger SV",
        "country": "Germany",
        "league": "2. Bundesliga",
        "careers_url": "https://www.hsv.de/unser-hsv/karriere-beim-hsv/jobs/festanstellungen",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Hamburger SV",
        "linkedin_jobs_url": "https://www.linkedin.com/company/hamburger-sport-verein/jobs/",
        "notes": None,
    },
    {
        "name": "1. FC KÃ¶ln",
        "country": "Germany",
        "league": "2. Bundesliga",
        "careers_url": "https://effzeh.jobs.personio.de",  # [live] Personio board
        "teamtailor_slug": None,
        "linkedin_company": "1. FC KÃ¶ln",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fckoeln/jobs/",
        "notes": None,
    },

    # ================================================================= #
    #  FRANCE - Ligue 1                                                   #
    # ================================================================= #
    {
        "name": "Paris Saint-Germain",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://parissaintgermain.wd3.myworkdayjobs.com/fr-FR/rejoigneznous",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Paris Saint-Germain",
        "linkedin_jobs_url": "https://www.linkedin.com/company/paris-saint-germain/jobs/",
        "notes": "Official Workday recruitment portal. Also see psg.fr/club/carrieres for overview.",
    },
    {
        "name": "Olympique de Marseille",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://olympique-de-marseille.taleez.com/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Olympique de Marseille",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sasp-olympique-de-marseille/jobs/",
        "notes": "Posts jobs via LinkedIn (primary) and Welcome to the Jungle (welcometothejungle.com). No dedicated careers page on om.fr.",
    },
    {
        "name": "AS Monaco",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "AS Monaco FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/as-monaco/jobs/",
        "notes": "No confirmed public careers page. Open applications via rh@asmonaco.com. LinkedIn is main channel for executive roles.",
    },
    {
        "name": "Olympique Lyonnais",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://careers.eaglefootballgroup.com/search",  # [live]
        "ats_platform": "successfactors",
        "teamtailor_slug": None,
        "linkedin_company": "Olympique Lyonnais",
        "linkedin_jobs_url": "https://www.linkedin.com/company/olympique-lyonnais-groupe/jobs/",
        "notes": "Eagle Football Group ownership. All EFG clubs (OL, Botafogo etc.) listed here.",
    },
    {
        "name": "Lille OSC",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.losc.fr/losc-espace-carriere",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "LOSC Lille",
        "linkedin_jobs_url": "https://www.linkedin.com/company/loscofficiel/jobs/",
        "notes": None,
    },
    {
        "name": "OGC Nice",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "OGC Nice",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ogcnice/jobs/",
        "notes": (
            "INEOS-owned. No permanent careers page. Posts via LinkedIn (primary). "
            "Academy: formation@ogcnice.com. Scouting: recrutement@ogcnice.com. "
            "Annual jobs fair at Allianz Riviera (ogcnice.com/en/endowment-fund/community/jobs-fair.html)."
        ),
    },
    {
        "name": "RC Lens",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "RC Lens",
        "linkedin_jobs_url": "https://www.linkedin.com/company/racingclubdelens/jobs/",
        "notes": "No permanent careers page. LinkedIn is primary channel. Hospitality/events roles via SPORTFIVE and Adecco (official partner). Also posts on sportjobshunter.com.",
    },
    {
        "name": "Stade Rennais FC",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.hellowork.com/fr-fr/entreprises/stade-rennais-football-club-170554.html#offres-emploi",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Stade Rennais FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/staderennaisfc/jobs/",
        "notes": "Official recruitment partner is Hellowork (URL above). LinkedIn also active. Matchday roles via Samsic Emploi (main sponsor/HR partner). Regional jobs fair: offres-stade-emploi.staderennais.com.",
    },
    {
        "name": "Stade Brestois 29",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.indeed.com/cmp/Stade-Brestois-29/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Stade Brestois 29",
        "linkedin_jobs_url": "https://www.linkedin.com/company/stade-brestois-29/jobs/",
        "notes": "Management open application form confirmed. Academy/youth form: sb29.bzh/candidature.php. LinkedIn for corporate updates. Regional jobs project: sb29.bzh/supporters-de-l-emploi.php.",
    },
    {
        "name": "Toulouse FC",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://fr.indeed.com/q-toulouse-football-club-emplois.html?vjk=234ef2c7bfeb4f7e",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Toulouse FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/toulousefc/jobs/",
        "notes": "RedBird Capital ownership. LinkedIn is primary channel. Ticketing/admin: recrutement.billetterie@toulousefc.com. Scouting/analytics: recrutement.scouting@toulousefc.com.",
    },
    {
        "name": "RC Strasbourg Alsace",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://sportsjobs.fr/companyprofile?company=racing-club-de-strasbourg-alsace-6930244b42a23784be612196",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "RC Strasbourg Alsace",
        "linkedin_jobs_url": "https://www.linkedin.com/company/racing-club-strasbourg-alsace/jobs/",
        "notes": "BlueCo (Chelsea) ownership. LinkedIn primary. Corporate: recrutement@rcstrasbourg.eu. Scouting/sports roles: scouting@rcstrasbourg.eu. Also on sportsjobs.fr.",
    },
    {
        "name": "FC Nantes",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.fcnantes.com/articles/article2809.php?num=48817",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "FC Nantes",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-nantes/jobs/",
        "notes": "Posts vacancies as news articles on their website (URL above) rather than a dedicated jobs page. LinkedIn also active. Sports/academy roles: written applications to Centre Sportif JosÃ© Arribas, La JoneliÃ¨re, 44240 La Chapelle-sur-Erdre.",
    },
    {
        "name": "Montpellier HSC",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Montpellier HÃ©rault Sport Club",
        "linkedin_jobs_url": "https://www.linkedin.com/company/montpellier-herault-sc/jobs/",
        "notes": "No careers portal. LinkedIn primary. No direct HR email confirmed; call +33 4 67 15 46 00 for HR contacts. Sports roles via mhscfoot.com/en/formation/directors-and-sports-staff/.",
    },
    {
        "name": "AJ Auxerre",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "AJ Auxerre",
        "linkedin_jobs_url": "https://www.linkedin.com/company/aj-auxerre/jobs/",
        "notes": "LinkedIn primary. Academy/internaat roles on Hellowork and Indeed. Sporttechnical roles via UNECATEF. International roles on futboljobs.com.",
    },
    {
        "name": "Le Havre AC",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Le Havre Athletic Club",
        "linkedin_jobs_url": "https://www.linkedin.com/company/havre-ac-foot/jobs/",
        "notes": "LinkedIn primary. No permanent careers page. Academy (La CavÃ©e Verte) trained Pogba and Mahrez. Sports/academy roles via internal networks; written applications to training complex.",
    },
    {
        "name": "Angers SCO",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Angers SCO",
        "linkedin_jobs_url": "https://www.linkedin.com/company/angerssco/jobs/",
        "notes": "LinkedIn primary. Commercial/shop roles: commercial@angers-sco.fr. Admin/legal: secretariat@angers-sco.fr. Also posts on futboljobs.com.",
    },
    {
        "name": "FC Metz",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.fcmetz.com/fr/contact",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "FC Metz",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fcmetz/jobs/",
        "notes": "Contact page has 'Recrutement Administratif' dropdown for direct HR applications. Email: recrutement@fcmetz.com. Also posts via Ligue du Grand Est (lgef.fff.fr) and sportjobshunter.com.",
    },
    {
        "name": "FC Lorient",
        "country": "France",
        "league": "Ligue 1",
        "careers_url": "https://www.fclorient.bzh/nous-rejoindre/",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "FC Lorient",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-lorient/jobs/",
        "notes": "Official 'nous rejoindre' page confirmed. Contact form also allows direct CV submissions per department. LinkedIn very active for corporate roles. Matchday hospitality via Actual Group (actual.events@actualgroup.com).",
    },

    # ================================================================= #
    #  SPAIN - La Liga                                                    #
    # ================================================================= #
    {
        "name": "Real Madrid CF",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://eujobs.legendsglobal.com/jobs?location_id=1198105",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Real Madrid C.F.",
        "linkedin_jobs_url": "https://www.linkedin.com/company/realmadrid/jobs/",
        "notes": (
            "No public corporate careers page. Operational roles (stadium, hospitality, shops) "
            "are posted via partner Legends Global at the URL above. "
            "Corporate/management roles are almost never posted publicly; "
            "primary route is via Real Madrid Graduate School - Universidad Europea. "
            "Also monitor LALIGA LinkedIn page for wider Spanish football roles."
        ),
    },
    {
        "name": "FC Barcelona",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "FC Barcelona",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-barcelona/jobs/",
        "notes": (
            "No general careers page. Corporate roles (marketing, sponsoring, data, IT) posted "
            "primarily via LinkedIn. Analytics/data roles also appear via Barca Innovation Hub "
            "(barcainnovationhub.fcbarcelona.com). "
            "Note: HQ roles require fluent Catalan + Spanish; EU work permit required."
        ),
    },
    {
        "name": "Valencia CF",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://www.valenciacf.com/rrhh",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Valencia CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/valencia-cf/jobs/",
        "notes": (
            "HR page confirmed. Retail/shop roles: email RRHH@valenciacf.es with 'VACANTE TIENDAS'. "
            "Analytics/data/IT roles also via VCF Innovation Hub LinkedIn page. "
            "Operational/stadium roles (VIP sales etc.) also on Legends and futboljobs.com."
        ),
    },
    {
        "name": "Club Atletico de Madrid",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://www.atleticodemadrid.com/ofertas-de-trabajo",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Club AtlÃ©tico de Madrid",
        "linkedin_jobs_url": "https://www.linkedin.com/company/atleticodemadrid/jobs/",
        "notes": None,
    },
    {
        "name": "Real Betis Balompie",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Real Betis",
        "linkedin_jobs_url": "https://www.linkedin.com/company/real-betis-balompie/jobs/",
        "notes": "No dedicated careers page. Posts jobs (data analysts, commercial, admin) primarily via LinkedIn.",
    },
    {
        "name": "Sevilla FC",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://sevillafc.es/es/el-club/trabaja-con-nosotros",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Sevilla FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sevillafc/jobs/",
        "notes": (
            "Official careers/open application portal confirmed. CVs stored up to 1 year. "
            "Data/analytics roles also via Sevilla FC Innovation Center "
            "(sevillafcinnovationcenter.com) - known for IBM Scout Advisor AI platform. "
            "Also monitor laliga.com/trabaja-con-nosotros (LaLiga talent pool)."
        ),
    },
    {
        "name": "Real Sociedad",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Real Sociedad",
        "linkedin_jobs_url": "https://www.linkedin.com/company/real-sociedad/jobs/",
        "notes": (
            "No public careers portal. Posts via InfoJobs (infojobs.net) and LaLiga talent pool "
            "(laliga.com/trabaja-con-nosotros). Open applications via realsoc@realsociedad.eus. "
            "Sports roles (data analysts, scouts, video analysts) appear on footballcareers.com "
            "and futboljobs.com."
        ),
    },
    {
        "name": "Athletic Club Bilbao",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Athletic Club",
        "linkedin_jobs_url": "https://www.linkedin.com/company/athleticclub/jobs/",
        "notes": (
            "No public careers portal. Corporate/IT/marketing roles posted via LinkedIn. "
            "Also uses LaLiga talent pool (laliga.com/trabaja-con-nosotros) and "
            "regional platform Bizkaia Talent (bizkaiatalent.eus). "
            "Note: playing staff Basque-only policy; office roles open internationally."
        ),
    },
    {
        "name": "RCD Mallorca",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "RCD Mallorca",
        "linkedin_jobs_url": "https://www.linkedin.com/company/real-mallorca/jobs/",
        "notes": (
            "No careers portal. Open applications via marketing@rcdmallorca.es or "
            "comunicacion@rcdmallorca.es. Shop/retail roles via Sports Emotion careers portal "
            "(careers.sportsemotion.com). LinkedIn is main channel for corporate roles."
        ),
    },
    {
        "name": "Villarreal CF",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://villarrealcf.es/trabaja-con-nosotros/",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Villarreal CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/villarreal-cf-sad/jobs/",
        "notes": (
            "Official open-application portal confirmed. Also actively posts on InfoJobs "
            "(villarrealcf.ofertas-trabajo.infojobs.net) and LinkedIn for data, IT and "
            "marketing roles. Also uses LaLiga talent pool (laliga.com/trabaja-con-nosotros)."
        ),
    },
    {
        "name": "RC Celta de Vigo",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://rccelta.es/en/grupo-rccelta/trabaja-con-nosotros/",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "RC Celta de Vigo",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rccelta/jobs/",
        "notes": "English-language portal confirmed. Spanish version: rccelta.es/grupo-rccelta/trabaja-con-nosotros/",
    },
    {
        "name": "CA Osasuna",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "CA Osasuna",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ca-osasuna/jobs/",
        "notes": "Member-owned club, no recruitment portal. Open applications via osasuna@osasuna.es. LinkedIn for networking; rarely posts vacancies directly.",
    },
    {
        "name": "Rayo Vallecano",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Rayo Vallecano",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rayo-vallecano-de-madrid-s-a-d/jobs/",
        "notes": "No recruitment portal. Open applications via direct contact (rayovallecano.es/datos-del-club). LinkedIn is main digital channel.",
    },
    {
        "name": "Elche CF",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://academy.elchecf.es/en/work-with-us/",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Elche CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/elche-cf-sad/jobs/",
        "notes": "Academy careers portal confirmed (English version). Spanish: academy.elchecf.es/trabaja-con-nosotros/. Also posts on InfoJobs for admin roles.",
    },
    {
        "name": "Getafe CF",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Getafe C.F.",
        "linkedin_jobs_url": "https://www.linkedin.com/company/getafe-c-f-s-a-d/jobs/",
        "notes": (
            "No recruitment portal. Open applications via admon@getafecf.com (general/HR) "
            "or contabilidad@getafecf.com (finance). LinkedIn active but small club. "
            "International academy via getafeinternational.com."
        ),
    },
    {
        "name": "Girona FC",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://www.gironafc.cat/en/work-with-us",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Girona FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/gironafc/jobs/",
        "notes": "City Football Group affiliate. English portal confirmed. Spanish: gironafc.cat/es/trabaja-con-nosotros. Corporate roles also via futboljobs.com.",
    },
    {
        "name": "Deportivo Alaves",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://deportivoalaves.com/trabaja-con-nosotros",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Deportivo AlavÃ©s",
        "linkedin_jobs_url": "https://www.linkedin.com/showcase/deportivo-alav%C3%A9s-sad/jobs/",
        "notes": (
            "Part of Grupo Baskonia-AlavÃ©s (also includes Baskonia basketball). "
            "All vacancies also on group Join portal: join.com/companies/bkndagroup. "
            "Direct applications via deportivoalavessad@alaves.com."
        ),
    },
    {
        "name": "Levante UD",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Levante UD",
        "linkedin_jobs_url": "https://www.linkedin.com/company/levanteud/jobs/",
        "notes": "No careers portal. Open applications via info@levanteud.es. Also posts on InfoJobs. LinkedIn active for institutional updates and selective recruitment campaigns.",
    },
    {
        "name": "Real Oviedo",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://www.realoviedo.es/empleo",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Real Oviedo",
        "linkedin_jobs_url": "https://www.linkedin.com/company/realoviedo/jobs/",
        "notes": (
            "Full careers portal confirmed with upload form. Covers both deportivas "
            "(scouting, video analysis, medical) and corporativas (data, IT, marketing, finance). "
            "Foundation jobs: fundacionrealoviedo.com/trabaja-con-nosotros or empleo@fundacionrealoviedo.es. "
            "Shop/retail: realoviedo.shop/trabaja-con-nosotros."
        ),
    },

    # ================================================================= #
    #  SPAIN - La Liga 2                                                  #
    # ================================================================= #
    {
        "name": "RCD Espanyol",
        "country": "Spain",
        "league": "La Liga",
        "careers_url": "https://www.rcdespanyol.com/en/work-with-us",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "RCD Espanyol de Barcelona",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rcd-espanyol-de-barcelona/jobs/",
        "notes": "English portal confirmed. Spanish: rcdespanyol.com/es/trabaja-con-nosotros. Also posts on InfoJobs and futboljobs.com. Corporate departments selectable in form (marketing, IT, finance, ticketing etc.).",
    },
    {
        "name": "Real Racing Santander",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Real Racing Club de Santander",
        "linkedin_jobs_url": "https://www.linkedin.com/company/realracingclub/jobs/",
        "notes": "No permanent careers page. LinkedIn primary for corporate/admin roles. Commercial roles sometimes via external consultancies (e.g. BDR Consultores). International youth focus via Wakatake Group partnership.",
    },
    {
        "name": "UD Las Palmas",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "UD Las Palmas",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ud-las-palmas-sad/jobs/",
        "notes": "LinkedIn primary. Creative/media roles via InfoJobs (UD Las Palmas Creative SL). No permanent careers page.",
    },
    {
        "name": "UD Almeria",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "UD AlmerÃ­a",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ud-almer%C3%ADa/jobs/",
        "notes": "LinkedIn primary. No careers page; management contacts via udalmeriasad.com/organigrama. Open applications directly to relevant department.",
    },
    {
        "name": "Malaga CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.impulsyn.com/organizacion/malaga-club-de-futbol/empleo",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "MÃ¡laga CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/m%C3%A1laga-cf/jobs/",
        "notes": "Posts via Impulsyn (confirmed). Open applications/internships via malagacf.com/en/contacta-con-nosotros. LinkedIn for management roles.",
    },
    {
        "name": "CD Castellon",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "CD CastellÃ³n",
        "linkedin_jobs_url": "https://www.linkedin.com/company/club-deportivo-castell%C3%B3n-sad/jobs/",
        "notes": "No permanent careers page. LinkedIn primary. Growing club with international (incl. Dutch) staff. Open applications via cdcastellon.com contact form.",
    },
    {
        "name": "RC Deportivo de La Coruna",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "RC Deportivo de La CoruÃ±a",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rcdeportivo/jobs/",
        "notes": "LinkedIn primary. Youth/coaching roles via Escola de Adestradores (escolaadestradoresrcd.es/formacion/). Open applications via rcdeportivo.es/es/contacto.",
    },
    {
        "name": "Burgos CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.burgoscf.es/forma-parte-del-equipo-del-burgos-club-de-futbol",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Burgos CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/burgos-cf/jobs/",
        "notes": "Open application form confirmed. Also posts on futboljobs.com and LinkedIn.",
    },
    {
        "name": "SD Eibar",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.sdeibar.com/empleo",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "SD Eibar",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sd-eibar/jobs/",
        "notes": "Careers/employment page confirmed. Direct HR email: rrhh@sdeibar.com. LinkedIn for commercial/admin roles.",
    },
    {
        "name": "Cordoba CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.infojobs.net/cordoba-club-de-futbol-sad/em-i97495253534949677982680012053389517751",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "CÃ³rdoba CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/cordobacf/jobs/",
        "notes": "Primary channel is InfoJobs (URL above). LinkedIn for commercial/management roles. Commercial dept: comercial@cordobacf.com.",
    },
    {
        "name": "FC Andorra",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "FC Andorra",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-andorra/jobs/",
        "notes": "Gerard Pique ownership. No careers page. Open applications via rrhh@fcandorra.com (Catalan/Spanish preferred). LinkedIn for media/admin roles. Note: Andorra is not EU; work permit rules apply.",
    },
    {
        "name": "Real Sporting de Gijon",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Real Sporting de GijÃ³n",
        "linkedin_jobs_url": "https://www.linkedin.com/company/realsporting/jobs/",
        "notes": "Owned by Orlegi Sports (Mexico). Vacancies via Orlegi Sports LinkedIn and club LinkedIn. Open applications via info@realsporting.com. Known academy: Escuela de FÃºtbol de Mareo.",
    },
    {
        "name": "Albacete Balompie",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": None,  # [search-only]
        "teamtailor_slug": None,
        "linkedin_company": "Albacete BalompiÃ©",
        "linkedin_jobs_url": "https://www.linkedin.com/company/albacete-balompi%C3%A9/jobs/",
        "notes": "No careers page. LinkedIn and InfoJobs primary. Open applications via club@albacetebalompie.com or contact form at albacetebalompie.es/contacto.",
    },
    {
        "name": "Granada CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.granadacf.es/trabaja-con-nosotros",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Granada CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/granada-cf/jobs/",
        "notes": "Dedicated careers page confirmed. HR email: rrhh@granadacf.es. LinkedIn for commercial/management roles.",
    },
    {
        "name": "Real Valladolid CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.realvalladolid.es/trabaja-con-nosotros",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Real Valladolid CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/real-valladolid-club-de-f-tbol-s.a.d./jobs/",
        "notes": "Careers page confirmed. HR email: rrhh@realvalladolid.es. Ronaldo (Brazilian) ownership. LinkedIn for management roles.",
    },
    {
        "name": "CD Leganes",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.infojobs.net/club-deportivo-leganes-sa-d/em-i97505653505948677685668023214499200069",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Club Deportivo LeganÃ©s",
        "linkedin_jobs_url": "https://www.linkedin.com/company/club-deportivo-legan%C3%A9s/jobs/",
        "notes": "HR email: recursoshumanos@cdleganes.com. InfoJobs confirmed. Official partnership with futboljobs.com for sports/operational roles. LinkedIn for management.",
    },
    {
        "name": "Cadiz CF",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.cadizcf.com/oferta-de-empleo",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "CÃ¡diz CF",
        "linkedin_jobs_url": "https://www.linkedin.com/company/c-diz-cf/jobs/",
        "notes": "Careers page confirmed. HR email for open applications: curriculum@cadizcf.es. Also on InfoJobs. LinkedIn for management/commercial roles.",
    },
    {
        "name": "Real Zaragoza",
        "country": "Spain",
        "league": "La Liga 2",
        "careers_url": "https://www.realzaragoza.com/trabaja-con-nosotros",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Real Zaragoza",
        "linkedin_jobs_url": "https://www.linkedin.com/company/real-zaragoza/jobs/",
        "notes": "Careers portal confirmed. LinkedIn for corporate/admin roles. Retail/shop roles via FÃºtbol Emotion (careers.sportsemotion.com).",
    },

    # ================================================================= #
    #  ENGLAND - Premier League                                           #
    # ================================================================= #
    {
        "name": "Arsenal FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.arsenal.com/jobs",  # [live]
        "teamtailor_slug": "careers.arsenal",
        "linkedin_company": "Arsenal FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/arsenal-f-c/jobs/",
        "notes": "Teamtailor ATS. Strong analytics dept.",
    },
    {
        "name": "Manchester City FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.cityfootballgroup.com/",  # [live]
        "ats_platform": "successfactors",
        "teamtailor_slug": None,
        "linkedin_company": "Manchester City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/manchester-city-football-club/jobs/",
        "notes": "Jobs via City Football Group portal. All CFG clubs listed there.",
    },
    {
        "name": "Manchester United FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://www.candidatemanager.net/cm/p/pJobs.aspx?mid=YFDU&sid=BBUU",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Manchester United",
        "linkedin_jobs_url": "https://www.linkedin.com/company/manchester-united/jobs/",
        "notes": "Uses Candidate Manager ATS (confirmed). Talent pool registration: candidatemanager.net/cm/p/pLogin.aspx?mid=YFDU&sid=YAZAZEV. INEOS takeover.",
    },
    {
        "name": "Liverpool FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://jobsearch.liverpoolfc.com/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Liverpool FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/liverpool-football-club/jobs/",
        "notes": "Main jobs portal. Also see recruitment.liverpoolfc.com for overview.",
    },
    {
        "name": "Aston Villa FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://avfc.wd502.myworkdayjobs.com/avfc_careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Aston Villa FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/aston-villa-football-club/jobs/",
        "notes": "Teamtailor ATS at careers.avfc.co.uk.",
    },
    {
        "name": "AFC Bournemouth",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.afcb.co.uk/",  # [live] Pinpoint ATS
        "teamtailor_slug": None,
        "ats_platform": "pinpoint",
        "linkedin_company": "AFC Bournemouth",
        "linkedin_jobs_url": "https://www.linkedin.com/company/afc-bournemouth/jobs/",
        "notes": "Pinpoint ATS — API at careers.afcb.co.uk/jobs.json",
    },
    {
        "name": "Brentford FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://hiring.brentfordfc.com/jobs",  # [live]
        "teamtailor_slug": "hiring.brentfordfc",
        "linkedin_company": "Brentford FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/brentford-football-club/jobs/",
        "notes": "Teamtailor for corporate roles. Football/sports roles via Workday: brentfordfootballclub.wd107.myworkdayjobs.com/BrentfordFC. Community trust jobs: brentfordfccommunitysportstrust.teamtailor.com. Extremely data-driven. High priority.",
    },
    {
        "name": "Brighton & Hove Albion FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://www.brightonandhovealbion.com/career-opportunities",  # [confirmed]
        "teamtailor_slug": None,
        "linkedin_company": "Brighton & Hove Albion FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/brighton-&-hove-albion-fc/jobs/",
        "notes": "Tony Bloom ownership. Data-driven. Also owns USG. No speculative CVs accepted - must apply to open role. Matchday team: teamtalent@brightonandhovealbion.com. Hospitality via Sodexo Live: staffing.bhafc.uk@sodexo.com.",
    },
    {
        "name": "Chelsea FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://secure.workforceready.eu/ta/6189861.careers?CareersSearch=&lang=en-GB",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Chelsea FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/chelsea-football-club/jobs/",
        "notes": "BlueCo ownership (also owns Strasbourg). Uses CoreHR ATS (linked from careers page). Also on globalsportsjobs.com. LinkedIn very active.",
    },
    {
        "name": "Everton FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.evertonfc.com/vacancies",  # [live]
        "ats_platform": "talos",
        "teamtailor_slug": None,
        "linkedin_company": "Everton FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/everton-football-club/jobs/",
        "notes": "Uses Talos ATS at careers.evertonfc.com.",
    },
    {
        "name": "Fulham FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://fulhamfc.careers.hibob.com/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Fulham FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fulham-fc/jobs/",
        "notes": "Uses HiBob ATS (confirmed). General careers info: fulhamfc.com/club/careers. LinkedIn active for commercial/academy roles.",
    },
    {
        "name": "Sunderland AFC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://sunderlandafc.talosats-careers.com/vacancies",  # [live]
        "ats_platform": "talos",
        "teamtailor_slug": None,
        "linkedin_company": "Sunderland AFC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sunderlandafc/jobs/",
        "notes": "Uses Talos ATS.",
    },
    {
        "name": "Newcastle United FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.newcastleunited.com/jobs",  # [live]
        "teamtailor_slug": "careers.newcastleunited",
        "linkedin_company": "Newcastle United FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/newcastle-united-football-club/jobs/",
        "notes": "Teamtailor ATS. PIF ownership. Growing analytics dept.",
    },
    {
        "name": "Leeds United FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://www.leedsunited.com/en/club/careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Leeds United FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/leedsunited/jobs/",
        "notes": "49ers Enterprises ownership.",
    },
    {
        "name": "Crystal Palace FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.cpfc.co.uk/jobs",  # [live]
        "teamtailor_slug": "careers.cpfc",
        "linkedin_company": "Crystal Palace FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/crystal-palace-football-club/jobs/",
        "notes": "Teamtailor ATS. Foundation jobs via palaceforlifefoundation.teamtailor.com (recruitment@palaceforlife.org).",
    },
    {
        "name": "Nottingham Forest FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.nottinghamforest.co.uk/jobs",  # [live]
        "teamtailor_slug": "careers.nottinghamforest",
        "linkedin_company": "Nottingham Forest FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/nottingham-forest-fc/jobs/",
        "notes": "Teamtailor ATS. Evangelos Marinakis ownership. Community Trust jobs: careers.nottinghamforestcommunitytrust.co.uk. Matchday hospitality via Constellation.",
    },
    {
        "name": "Tottenham Hotspur FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://ce0812li.webitrent.com/ce0812li_webrecruitment/wrd/run/etrec179gf.open?wvid=9447152BOp",  # [live]
        "ats_platform": "webitrent",
        "teamtailor_slug": None,
        "linkedin_company": "Tottenham Hotspur FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/tottenham-hotspur-ltd/jobs/",
        "notes": "Vacancies via MHR/webitrent portal. HR email: thf.recruitment@tottenhamhotspur.com.",
    },
    {
        "name": "West Ham United FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://www.whufc.com/en/the-club/careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "West Ham United FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/west-ham-united/jobs/",
        "notes": "careers.whufc.com redirects here.",
    },
    {
        "name": "Burnley FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://careers.burnleyfootballclub.com/",  # [live]
        "teamtailor_slug": "careers.burnleyfootballclub",
        "linkedin_company": "Burnley FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/burnleyofficial/jobs/",
        "notes": "Teamtailor ATS. ALK Capital ownership. Community jobs: vacancies.burnleyfccommunity.org/jobs. Matchday hospitality via Constellation (jobs.constellation.co.uk/burnley-fc).",
    },
    {
        "name": "Wolverhampton Wanderers FC",
        "country": "England",
        "league": "Premier League",
        "careers_url": "https://www.wolves.co.uk/club/vacancies/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Wolverhampton Wanderers FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/wolverhampton-wanderers-fc/jobs/",
        "notes": "Fosun International ownership. Applications via jobs@wolves.co.uk. Foundation jobs: foundation.wolves.co.uk/about-us/vacancies. Matchday hospitality via Constellation (jobs.constellation.co.uk/wolverhampton-wanderers).",
    },

    # ================================================================= #
    #  ENGLAND - Championship                                             #
    # ================================================================= #
    {
        "name": "Birmingham City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.bcfc.com/club/careers/",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "Birmingham City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/birmingham-city-fc/jobs/",
        "notes": "Tom Brady / Knighthead Capital ownership.",
    },
    {
        "name": "Blackburn Rovers FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.rovers.co.uk/club/job-vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Blackburn Rovers FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/blackburn-rovers-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Bristol City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.bristol-sport.co.uk/careers/bristol-city/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Bristol City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/bristol-city-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Charlton Athletic FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.charltonafc.com/vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Charlton Athletic FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/charlton-athletic-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Coventry City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://coventrycityfootballclub.teamtailor.com/jobs",  # [live]
        "teamtailor_slug": "coventrycityfootballclub",
        "linkedin_company": "Coventry City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/coventry-city-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Derby County FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.dcfc.co.uk/page/permanent-roles",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Derby County FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/derby-county-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Hull City AFC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.wearehullcity.co.uk/club/careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Hull City AFC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/hull-city/jobs/",
        "notes": None,
    },
    {
        "name": "Ipswich Town FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.itfc.co.uk/club/careers/vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Ipswich Town FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ipswich-town-fc/jobs/",
        "notes": None,
    },
    {
        "name": "Leicester City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.lcfc.com/vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Leicester City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/leicester-city-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Middlesbrough FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.mfc.co.uk/careers/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Middlesbrough FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/middlesbrough-fc/jobs/",
        "notes": None,
    },
    {
        "name": "Millwall FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.millwallfc.co.uk/club-information/work-for-the-lions",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Millwall FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/millwall-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Norwich City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://careers.canaries.co.uk/",  # [live]
        "teamtailor_slug": None,
        "ats_platform": "postingpanda",
        "linkedin_company": "Norwich City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/norwich-city-football-club/jobs/",
        "notes": "Posting Panda ATS — API routes by Origin header.",
    },
    {
        "name": "Oxford United FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.oufc.co.uk/vacancies-oxford-united",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Oxford United FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/oufc1893/jobs/",
        "notes": None,
    },
    {
        "name": "Portsmouth FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.portsmouthfc.co.uk/club/work-for-us",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Portsmouth FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/portsmouth-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Preston North End FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.pnefc.net/pnecet/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Preston North End FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/pnefcofficial/jobs/",
        "notes": None,
    },
    {
        "name": "Queens Park Rangers FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.qpr.co.uk/club/careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Queens Park Rangers FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/qprfc/jobs/",
        "notes": None,
    },
    {
        "name": "Sheffield United FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.sufc.co.uk/club/vacancies/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Sheffield United FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sheffieldunited/jobs/",
        "notes": None,
    },
    {
        "name": "Sheffield Wednesday FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.swfc.co.uk/club/careers/",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "Sheffield Wednesday FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sheffield-wednesday-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Southampton FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://saintsfc.wd3.myworkdayjobs.com/SFC001",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Southampton FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/southampton-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Stoke City FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.stokecityfc.com/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Stoke City FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/stoke-city-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Swansea City AFC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.swanseacity.com/news/permanent-roles-full-timepart-time",  # [live] text-list page
        "teamtailor_slug": None,
        "linkedin_company": "Swansea City AFC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/swansea-city-football-club/jobs/",
        "notes": "Vacancies listed as text in a news article — Layer 1 text-scan used.",
    },
    {
        "name": "Watford FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.watfordfc.com/club/careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Watford FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/watford-football-club/jobs/",
        "notes": "Pozzo family (same as Udinese).",
    },
    {
        "name": "West Bromwich Albion FC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://www.wba.co.uk/club/vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "West Bromwich Albion FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/west-bromwich-albion-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Wrexham AFC",
        "country": "England",
        "league": "Championship",
        "careers_url": "https://careers.wrexhamafc.co.uk/vacancies",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Wrexham AFC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/wrexhamafc/jobs/",
        "notes": "Ryan Reynolds / Rob McElhenney ownership.",
    },

    # ================================================================= #
    #  ITALY - Serie A                                                    #
    # ================================================================= #
    {
        "name": "Inter Milan",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.inter.it/en/club/job-opportunities",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Inter Milan",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-internazionale-milano/jobs/",
        "notes": "Oaktree Capital ownership since 2024.",
    },
    {
        "name": "SSC Napoli",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.sscnapoli.it/static/page/lavora-con-noi.aspx",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "SSC Napoli",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sscnapoli/jobs/",
        "notes": None,
    },
    {
        "name": "AC Milan",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.acmilan.com/en/club/work-with-us",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "AC Milan",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ac-milan/jobs/",
        "notes": "RedBird Capital ownership.",
    },
    {
        "name": "Juventus FC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.juventus.com/it/club/careers/",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "Juventus FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/juventus-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "AS Roma",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://asroma.altamiraweb.com/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "AS Roma",
        "linkedin_jobs_url": "https://www.linkedin.com/company/as-roma/jobs/",
        "notes": "Dan Friedkin ownership.",
    },
    {
        "name": "Como 1907",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.como1907.com/en/careers",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "Como 1907",
        "linkedin_jobs_url": "https://www.linkedin.com/company/como-1907/jobs/",
        "notes": "Hartono family ownership.",
    },
    {
        "name": "Atalanta BC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.atalanta.it/it/club/lavora-con-noi",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "Atalanta BC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/atalantabc/jobs/",
        "notes": None,
    },
    {
        "name": "SS Lazio",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": "https://www.sslazio.it/it/club/lavora-con-noi",  # [best-guess]
        "teamtailor_slug": None,
        "linkedin_company": "SS Lazio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sslaziospa/jobs/",
        "notes": None,
    },
    {
        "name": "Bologna FC 1909",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Bologna FC 1909",
        "linkedin_jobs_url": "https://www.linkedin.com/company/bologna-f-c-1909-s-p-a-/jobs/",
        "notes": None,
    },
    {
        "name": "ACF Fiorentina",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "ACF Fiorentina",
        "linkedin_jobs_url": "https://www.linkedin.com/company/acf-fiorentina-s-p-a-/jobs/",
        "notes": None,
    },
    {
        "name": "Torino FC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Torino FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/torino-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "Udinese Calcio",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Udinese Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/udinese-calcio-spa/jobs/",
        "notes": "Pozzo family (same as Watford).",
    },
    {
        "name": "Parma Calcio 1913",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Parma Calcio 1913",
        "linkedin_jobs_url": "https://www.linkedin.com/company/parma-calcio-1913/jobs/",
        "notes": None,
    },
    {
        "name": "Genoa CFC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Genoa CFC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/genoa-cricket-and-football-club-s.p.a./jobs/",
        "notes": "777 Partners ownership.",
    },
    {
        "name": "Cagliari Calcio",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Cagliari Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/cagliari-calcio/jobs/",
        "notes": None,
    },
    {
        "name": "Hellas Verona FC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Hellas Verona FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/hellas-verona-f-c-/jobs/",
        "notes": None,
    },
    {
        "name": "US Lecce",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "US Lecce",
        "linkedin_jobs_url": "https://www.linkedin.com/company/uslecce/jobs/",
        "notes": None,
    },
    {
        "name": "US Cremonese",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "US Cremonese",
        "linkedin_jobs_url": "https://www.linkedin.com/company/uscremonese/jobs/",
        "notes": None,
    },
    {
        "name": "Sassuolo Calcio",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "US Sassuolo Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sassuolocalcio/jobs/",
        "notes": None,
    },
    {
        "name": "Pisa SC",
        "country": "Italy",
        "league": "Serie A",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Pisa Sporting Club",
        "linkedin_jobs_url": "https://www.linkedin.com/company/pisa-sporting-club-1909/jobs/",
        "notes": "Alexander Knaster ownership.",
    },

    # ================================================================= #
    #  ITALY - Serie B                                                    #
    # ================================================================= #
    {
        "name": "US Avellino",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "US Avellino",
        "linkedin_jobs_url": "https://www.linkedin.com/company/u-s-avellino-1912/jobs/",
        "notes": None,
    },
    {
        "name": "SSC Bari",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "SSC Bari",
        "linkedin_jobs_url": "https://www.linkedin.com/company/ssc-bari/jobs/",
        "notes": "De Laurentiis family.",
    },
    {
        "name": "Carrarese Calcio",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Carrarese Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/carrarese-calcio-1908/jobs/",
        "notes": None,
    },
    {
        "name": "US Catanzaro",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "US Catanzaro 1929",
        "linkedin_jobs_url": "https://www.linkedin.com/company/uscatanzaro1929/jobs/",
        "notes": None,
    },
    {
        "name": "Cesena FC",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Cesena FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/cesenafc/jobs/",
        "notes": None,
    },
    {
        "name": "Empoli FC",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Empoli FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/empoli-fc/jobs/",
        "notes": None,
    },
    {
        "name": "Frosinone Calcio",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Frosinone Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/frosinone-calcio-s.r.l./jobs/",
        "notes": None,
    },
    {
        "name": "SS Juve Stabia",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "SS Juve Stabia",
        "linkedin_jobs_url": "https://www.linkedin.com/company/s.s.-juve-stabia-s.r.l./jobs/",
        "notes": None,
    },
    {
        "name": "Mantova 1911",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Mantova 1911",
        "linkedin_jobs_url": "https://www.linkedin.com/company/mantova-1911-s-r-l/jobs/",
        "notes": None,
    },
    {
        "name": "Modena FC",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Modena FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/modena-football-club/jobs/",
        "notes": None,
    },
    {
        "name": "AC Monza",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "AC Monza",
        "linkedin_jobs_url": "https://www.linkedin.com/company/acmonza/jobs/",
        "notes": "Berlusconi / Fininvest.",
    },
    {
        "name": "Calcio Padova",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Calcio Padova",
        "linkedin_jobs_url": "https://www.linkedin.com/company/calcio-padova/jobs/",
        "notes": None,
    },
    {
        "name": "Palermo FC",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Palermo FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/palermocalcio/jobs/",
        "notes": "City Football Group affiliate.",
    },
    {
        "name": "Delfino Pescara",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Pescara Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/pescaracalcio/jobs/",
        "notes": None,
    },
    {
        "name": "AC Reggiana",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "AC Reggiana 1919",
        "linkedin_jobs_url": "https://www.linkedin.com/company/acreggiana1919/jobs/",
        "notes": None,
    },
    {
        "name": "UC Sampdoria",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "UC Sampdoria",
        "linkedin_jobs_url": "https://www.linkedin.com/company/u-c--sampdoria/jobs/",
        "notes": None,
    },
    {
        "name": "Spezia Calcio",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Spezia Calcio",
        "linkedin_jobs_url": "https://www.linkedin.com/company/spezia-calcio-s.r.l.---societa-sportiva-professionistica/jobs/",
        "notes": None,
    },
    {
        "name": "FC Sudtirol",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "FC SÃ¼dtirol",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-s%C3%BCdtirol/jobs/",
        "notes": None,
    },
    {
        "name": "Venezia FC",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Venezia FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/veneziafc/jobs/",
        "notes": "US ownership.",
    },
    {
        "name": "Virtus Entella",
        "country": "Italy",
        "league": "Serie B",
        "careers_url": None,
        "teamtailor_slug": None,
        "linkedin_company": "Virtus Entella",
        "linkedin_jobs_url": "https://www.linkedin.com/company/virtus-entella/jobs/",
        "notes": None,
    },

    # ================================================================= #
    #  SCOTLAND                                                           #
    # ================================================================= #
    {
        "name": "Rangers FC",
        "country": "Scotland",
        "league": "Scottish Premiership",
        "careers_url": "https://uk.indeed.com/cmp/Rangers-Football-Club/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Rangers FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/rangersfc/jobs/",
        "notes": "Uses People First ATS.",
    },
    {
        "name": "Celtic FC",
        "country": "Scotland",
        "league": "Scottish Premiership",
        "careers_url": "https://www.celticfc.com/club/jobs-at-celtic/permanent-and-fixed-term-roles/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Celtic FC",
        "linkedin_jobs_url": "https://www.linkedin.com/company/celtic-football-club/jobs/",
        "notes": None,
    },

    # ================================================================= #
    #  PORTUGAL                                                           #
    # ================================================================= #
    {
        "name": "SL Benfica",
        "country": "Portugal",
        "league": "Primeira Liga",
        "careers_url": "https://recrutamento.slbenfica.pt/go/Job-Opportunities/9183055/?locale=en_US",  # [live]
        "ats_platform": "successfactors",
        "teamtailor_slug": None,
        "linkedin_company": "Sport Lisboa e Benfica",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sport-lisboa-e-benfica/jobs/",
        "notes": "Dedicated recruitment portal. Uses SAP SuccessFactors. Strong analytics culture.",
    },
    {
        "name": "Sporting CP",
        "country": "Portugal",
        "league": "Primeira Liga",
        "careers_url": "https://www.indeed.com/cmp/Sporting-Clube-De-Portugal/jobs",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "Sporting CP",
        "linkedin_jobs_url": "https://www.linkedin.com/company/sporting-clube-de-portugal/jobs/",
        "notes": None,
    },
    {
        "name": "FC Porto",
        "country": "Portugal",
        "league": "Primeira Liga",
        "careers_url": "https://candidaturas.fcporto.pt/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC Porto",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fcporto/jobs/",
        "notes": "Dedicated candidaturas subdomain. Requires JS.",
    },

    # ================================================================= #
    #  DENMARK                                                            #
    # ================================================================= #
    {
        "name": "FC Copenhagen",
        "country": "Denmark",
        "league": "Superliga",
        "careers_url": "https://www.fck.dk/en/jobs-and-careers",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC Copenhagen",
        "linkedin_jobs_url": "https://www.linkedin.com/company/f-c--k%C3%B8benhavn/jobs/",
        "notes": None,
    },
    {
        "name": "FC Midtjylland",
        "country": "Denmark",
        "league": "Superliga",
        "careers_url": "https://www.fcm.dk/klubben/karriere/",  # [live]
        "teamtailor_slug": None,
        "linkedin_company": "FC Midtjylland",
        "linkedin_jobs_url": "https://www.linkedin.com/company/fc-midtjylland/jobs/",
        "notes": "Matthew Benham/Smartodds ownership. Extremely data-driven. High priority.",
    },
]


# ================================================================= #
#  HELPER LOOKUPS                                                    #
# ================================================================= #

# ================================================================= #
#  CLUBS_BY_LEAGUE                                                   #
#  Dict used by app.py and scraper.py.  Keys are the display names  #
#  expected by the UI (country or "country - league" format).       #
# ================================================================= #

CLUBS_BY_LEAGUE: dict[str, list] = {
    "Netherlands":              [c for c in CLUBS if c["league"] == "Eredivisie"],
    "Belgium":                  [c for c in CLUBS if c["league"] == "Jupiler Pro League"],
    "Germany":                  [c for c in CLUBS if c["league"] in ("Bundesliga", "2. Bundesliga")],
    "France":                   [c for c in CLUBS if c["league"] == "Ligue 1"],
    "Spain - La Liga":          [c for c in CLUBS if c["league"] == "La Liga"],
    "Spain - La Liga 2":        [c for c in CLUBS if c["league"] == "La Liga 2"],
    "England - Premier League": [c for c in CLUBS if c["league"] == "Premier League"],
    "England - Championship":   [c for c in CLUBS if c["league"] == "Championship"],
    "Italy - Serie A":          [c for c in CLUBS if c["league"] == "Serie A"],
    "Italy - Serie B":          [c for c in CLUBS if c["league"] == "Serie B"],
    "Scotland":                 [c for c in CLUBS if c["league"] == "Scottish Premiership"],
    "Portugal":                 [c for c in CLUBS if c["league"] == "Primeira Liga"],
    "Denmark":                  [c for c in CLUBS if c["league"] == "Superliga"],
}


def get_clubs_by_country(country: str) -> list:
    """Return all clubs for a given country (case-insensitive)."""
    return [c for c in CLUBS if c["country"].lower() == country.lower()]


def get_clubs_by_league(league: str) -> list:
    """Return all clubs for a given league (case-insensitive, partial match)."""
    return [c for c in CLUBS if league.lower() in c["league"].lower()]


def get_all_countries() -> list:
    """Return sorted list of unique countries."""
    return sorted(set(c["country"] for c in CLUBS))


def get_all_leagues() -> list:
    """Return sorted list of unique leagues."""
    return sorted(set(c["league"] for c in CLUBS))


def get_clubs_with_careers_url() -> list:
    """Return clubs that have a direct careers URL to scrape."""
    return [c for c in CLUBS if c["careers_url"] is not None]


def get_clubs_without_careers_url() -> list:
    """Return clubs that rely purely on search-layer scraping."""
    return [c for c in CLUBS if c["careers_url"] is None]


def get_teamtailor_clubs() -> list:
    """Return clubs confirmed to use Teamtailor ATS."""
    return [c for c in CLUBS if c["teamtailor_slug"] is not None]


if __name__ == "__main__":
    print(f"Total clubs loaded        : {len(CLUBS)}")
    print(f"Clubs with careers URL    : {len(get_clubs_with_careers_url())}")
    print(f"Clubs search-only         : {len(get_clubs_without_careers_url())}")
    print(f"Clubs using Teamtailor    : {len(get_teamtailor_clubs())}")
    print(f"Countries                 : {get_all_countries()}")
    print(f"Leagues                   : {get_all_leagues()}")
