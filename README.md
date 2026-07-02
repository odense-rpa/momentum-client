# momentum-client

A Python client library for the KMD Momentum API, giving Danish municipalities programmatic access to citizens, companies, tasks, journal notes, tags, taxonomies, and VITAS grants.

> Denne klient er ikke officielt støttet eller godkendt af KMD. Brug på eget ansvar.

## Om KMD Momentum

KMD Momentum is a Danish case management system used by municipalities for employment and social services. This library wraps its REST API with OAuth2 authentication and exposes the functionality through a set of named sub-clients.

## Installation

```bash
uv add git+https://github.com/odense-rpa/momentum-client
```

## Forudsætninger

- Python ≥ 3.13
- Adgang til KMD Momentum API (kræver OAuth2-klientoplysninger og API-nøgle)

## Konfiguration

Opret en `.env`-fil med følgende variable:

| Variabel | Beskrivelse |
|---|---|
| `BASE_URL` | Base URL for Momentum API'et |
| `CLIENT_ID` | OAuth2 klient-ID |
| `CLIENT_SECRET` | OAuth2 klienthemmelighed |
| `API_KEY` | API-nøgle sendt som `apikey`-header på alle forespørgsler |
| `RESOURCE` | OAuth2 ressource-ID brugt i client credentials grant |

## Brug

`MomentumClientManager` er det anbefalede indgangspunkt og lazy-loader alle sub-klienter ved første adgang:

```python
from dotenv import load_dotenv
from momentum_client import MomentumClientManager

load_dotenv()
client = MomentumClientManager()

# Søg på tværs af borgere, virksomheder mv.
results = client.søg("Odense")

# Hent en borger via CPR-nummer
borger = client.borgere.hent_borger(cpr="1234567890")

# Hent en virksomhed via CVR-nummer
virksomhed = client.virksomheder.hent_virksomhed(cvr="12345678")
```

## Nuværende funktionalitet

| Sub-klient | Tilgås via | Hvad den gør |
|---|---|---|
| `BorgereClient` | `client.borgere` | Hent og søg borgere via CPR eller borger-ID |
| `VirksomhederClient` | `client.virksomheder` | Hent virksomheder via CVR/P-nummer inkl. kontaktpersoner, sagsbehandlere og jobordrer |
| `MarkeringerClient` | `client.markeringer` | Opret, hent, afslut og slet markeringer på borgere og virksomheder |
| `OpgaverClient` | `client.opgaver` | Opret, hent, søg og opdater opgavestatus for borgere og virksomheder |
| `JournalnotaterClient` | `client.journalnotater` | Hent journalnotater for en given reference |
| `VitasClient` | `client.vitas` | Hent og søg VITAS-tilbud med paginering |
| `TaksonomierClient` | `client.taksonomier` | Slå taksonomier og taksonomigrupper op via kode |

Global søgning (`client.søg`) dækker: borgere, virksomheder, kontaktpersoner, sagsbehandlere, tilbud, jobordrer, jobopslag og kurser.

## Afhængigheder

| Pakke | Formål |
|---|---|
| `authlib` | OAuth2 client credentials-flow |
| `httpx` | Underliggende HTTP-klient |
| `python-dotenv` | Indlæsning af miljøvariabler fra `.env` |
| `certifi` | SSL-certifikatverifikation |

> **Bemærk:** Biblioteket inkluderer en bundtet DigiCert CA-certifikatkæde (`momentum_client/certs/`) som workaround for et TLS-problem i KMD's infrastruktur (noteret 31-10-2025).

## GDPR og sikkerhed

Dette bibliotek håndterer CPR-numre og borgerdata fra Momentum, herunder kontaktoplysninger, sagsdata og beskæftigelseshistorik. Sørg for at legitimationsoplysninger aldrig gemmes i kildekode eller versionsstyring — brug `.env`-filer eller et dedikeret hemmelighedshåndteringssystem.

## Licens

MIT
