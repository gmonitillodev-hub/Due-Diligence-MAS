# Benchmark — Due Diligence Multi-Agent System

## Aziende

| Azienda / sito | Descrizione | Stato | Memo prodotto |
| --- | --- | --- | --- |
| [Boom](https://boom.co) | Ben strutturata — valutazione dell’utente | Valutata | [Memo Boom](https://chatgpt.com/library?file_id=libfile_28548625ac748191874f074eb4e088de&account_id=118376eb-d45a-404f-82a8-184b08b6d67a) |
| [Inkeep](https://inkeep.com) | Agenti AI per assistenza clienti | Eseguita | [Memo Inkeep](https://chatgpt.com/library?file_id=libfile_80fbf7f9918481919836320400a7d4b3&account_id=118376eb-d45a-404f-82a8-184b08b6d67a) |

## Esecuzioni

| Campo | Boom | Inkeep |
| --- | --- | --- |
| Eseguita in | CrewAI | CrewAI |
| Versione | profiler | Non indicata |
| trace_url | [Trace Boom](https://app.crewai.com/crewai_plus/ephemeral_traces/37eca1e7-2b91-4ddc-a607-59b453df33fe) | [Trace Inkeep](https://app.crewai.com/crewai_plus/ephemeral_traces/ecad1f74-dab6-431a-8c20-ec8ea5d12fdf) |
| started_at | 2026-11-14T18:54:53.651+00:00 | 2026-11-14T19:13:53.909+00:00 |
| finished_at | 2026-11-14T19:02:44.250+00:00 | 2026-11-14T19:20:40.255+00:00 |

## Valutazione dei memo

Analisi dei documenti prodotti, senza verifica esterna dei fatti aziendali o ispezione delle trace. I miglioramenti sono proposte da implementare.

### Boom

| Topic | Punti di forza | Problematiche | Miglioramenti suggeriti |
| --- | --- | --- | --- |
| Identità aziendale | Dominio di riferimento esplicito. | Hardware per videoconferenze associato alla pagina LinkedIn boom-imagestudio: possibile confusione fra omonimi. | Validare dominio, ragione sociale e attività prima di acquisire dati su team e funding; isolare le fonti con identità incerta. |
| Struttura e approfondimento | Sintesi, analisi, dibattito, rischi e prossimi passi presenti. | Tecnologia e team ripetono il profilo aziendale, con poco approfondimento specialistico. | Richiedere risultati distinti per area: specifiche e supporto per Tech; persone, ruoli ed esperienza per Team. Eliminare le ripetizioni in aggregazione. |
| Fonti | Riferimenti associati a prezzi, finanziamenti e profilo. | Molti Verified rimandano alla sola homepage; supporto puntuale non dimostrato nel memo. | Associare ogni affermazione a pagina, estratto e data di consultazione; lasciare non confermate quelle prive di riscontro. |
| Relazioni commerciali | Piattaforme nominate esplicitamente. | Partnership e compatibilità dei prodotti non sono distinte. | Classificare ogni relazione come cliente, partner, integrazione o compatibilità, con relativa evidenza. |
| Rischi e conclusioni | Rischi collegati a impatti e follow-up; lacune dichiarate. | Pagine 404 e dati mancanti sostengono inferenze su maturità e sostenibilità non dimostrate. | Separare fatti, ipotesi e informazioni mancanti; cercare URL alternativi e documenti di prodotto prima di formulare conclusioni. |
| Formato | Sezioni riconoscibili. | Heading racchiusi in grassetto, link e tabelle escapati. | Generare Markdown nativo e verificarne il rendering prima di salvare il memo. |

### Inkeep

| Topic | Punti di forza | Problematiche | Miglioramenti suggeriti |
| --- | --- | --- | --- |
| Coerenza dei finanziamenti | Profilo e Team riportano importo e investitori. | Citati $13M di seed, ma Commercial dichiara di non trovare notizie sul funding. | Usare un registro condiviso delle evidenze; far risolvere all’aggregator i conflitti fra sezioni oppure esplicitarli come irrisolti. |
| Date | Date e cutoff dichiarati. | Memo e accessi datati 2023, esecuzione nel 2026; provenienza delle date da chiarire. | Passare la data di esecuzione dal sistema e conservare separatamente pubblicazione, consultazione e cutoff; segnalare dati successivi al cutoff. |
| Analisi tecnica e team | Repository, SDK e funzionalità elencati; fondatori descritti con ruoli e background. | Stack e claim marcati Verified senza riscontri puntuali; elenco dei repository poco interpretato. | Citare file o documenti specifici, distinguere repository ufficiali e di esempio e spiegare cosa dimostrano sul prodotto. |
| Clienti e case study | Riferimenti commerciali e case study citati. | Case study e testimonianze sono poi elencati come mancanti; clienti e partner vengono confusi. | Riconciliare evidenze e lacune prima del memo finale; distinguere disponibilità del case study da mancanza di metriche quantitative. |
| Analisi commerciale e rischi | Clienti, concorrenti e vendita trattati separatamente. | Rischi di implementazione e sostenibilità dedotti da lacune senza evidenze sufficienti. | Collegare ogni rischio a un riscontro; presentare quelli non dimostrati come ipotesi e indicare la verifica necessaria. |
| Formato | Struttura completa e fonti raccolte. | Heading in grassetto, link e tabelle escapati. | Applicare un template Markdown comune e controllare link, tabelle e intestazioni in anteprima. |
