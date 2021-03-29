format_ccl = [
    (
        "Violation of Article 1 of Protocol No. 12 - General prohibition of discrimination",
        [
            {
                "element": "Violation of Article 1 of Protocol No. 12 - General prohibition of discrimination",
                "type": "violation",
                "article": "p12-1",
                "base_article": "p12-1"
            }
        ]
    ),
    (
        "Violation of Article 4 of Protocol No. 4 - Prohibition of collective expulsion of aliens",
        [
            {
                "element": "Violation of Article 4 of Protocol No. 4 - Prohibition of collective expulsion of aliens",
                "type": "violation",
                "article": "p4-4",
                "base_article": "p4-4"
            }
        ]
    ),
    (
        "Violation of Article 13+P4-4 - Right to an effective remedy",
        [
            {
                "element": "Violation of Article 13+P4-4 - Right to an effective remedy",
                "type": "violation",
                "article": "13",
                "base_article": "13"
            },
            {
                "element": "Violation of Article 13+P4-4 - Right to an effective remedy",
                "type": "violation",
                "article": "p4-4",
                "base_article": "p4-4"
            }
        ]
    ),
    (
        "Violation of Article 6+6-1 - Right to an effective remedy",
        [
            {
                "element": "Violation of Article 6+6-1 - Right to an effective remedy",
                "type": "violation",
                "article": "6-1",
                "base_article": "6"
            }
        ]
    ),
    (
        "Violation of Article 5-1+5-3 - Right to an effective remedy",
        [
            {
                "element": "Violation of Article 5-1+5-3 - Right to an effective remedy",
                "type": "violation",
                "article": "5-1",
                "base_article": "5"
            },
            {
                "element": "Violation of Article 5-1+5-3 - Right to an effective remedy",
                "type": "violation",
                "article": "5-3",
                "base_article": "5"
            }
        ]
    ),
    (
        "Violation of Article 14+5-3 - Right to an effective remedy",
        [
            {
                "element": "Violation of Article 14+5-3 - Right to an effective remedy",
                "type": "violation",
                "article": "14",
                "base_article": "14"
            },
            {
                "element": "Violation of Article 14+5-3 - Right to an effective remedy",
                "type": "violation",
                "article": "5-3",
                "base_article": "5"
            }
        ]
    ),
    (
        "Violation of Art. 2 (substantive aspect);Violation of Art. 2;Violation of Art. 13+2",
        [
            {
                "article": "2",
                "base_article": "2",
                "details": [
                    "substantive aspect"
                ],
                "element": "Violation of Art. 2",
                "type": "violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "element": "Violation of Art. 13+2",
                "type": "violation"
            },
            {
                "article": "13",
                "base_article": "13",
                "element": "Violation of Art. 13+2",
                "type": "violation"
            }
        ]
    ),
    (
        "No violation of Article 14+2 - Prohibition of discrimination (Article 14 - Discrimination) (Article 2 - Right to life;Article 2-1 - Effective investigation)",
        [
            {
                "element": "No violation of Article 14+2 - Prohibition of discrimination",
                "details": ["Article 14 - Discrimination"],
                "mentions": ["Article 2 - Right to life", "Article 2-1 - Effective investigation"],
                "type": "no-violation",
                "article": "2",
                "base_article": "2"
            },
            {
                "element": "No violation of Article 14+2 - Prohibition of discrimination",
                "details": ["Article 14 - Discrimination"],
                "mentions": ["Article 2 - Right to life", "Article 2-1 - Effective investigation"],
                "type": "no-violation",
                "article": "14",
                "base_article": "14"
                }
        ]
    ),
    (
        "Preliminary objections dismissed (estoppel, non-exhaustion of domestic remedies);Preliminary objection joined to merits and dismissed (lack of jurisdiction);Preliminary objection joined to merits and partially dismissed (victim);Violation of Art. 2 (procedural aspect);Non-pecuniary damage - award",
        [
            {
                "element":"Preliminary objections dismissed",
                "details":[
                    "estoppel, non-exhaustion of domestic remedies"
                ],
                "type":"other"
            },
            {
                "element":"Preliminary objection joined to merits and dismissed",
                "details":[
                    "lack of jurisdiction"
                ],
                "type":"other"
            },
            {
                "element":"Preliminary objection joined to merits and partially dismissed",
                "details":[
                    "victim"
                ],
                "type":"other"
            },
            {
                "element":"Violation of Art. 2",
                "details":[
                    "procedural aspect"
                ],
                "type":"violation",
                "article":"2",
                "base_article":"2"
            },
            {
                "element":"Non-pecuniary damage - award",
                "type":"other"
            }
        ]
    )
]

merge_ccl = [
    (
        [
            {
                "article": "2",
                "base_article": "2",
                "details": ["substantive aspect"],
                "element": "Violation of Art. 2",
                "type": "violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "element": "Violation of Art. 2",
                "type": "violation"}
        ],
        [
            {
                "article": "2",
                "base_article": "2",
                "details": ["substantive aspect"],
                "element": "Violation of Art. 2",
                "type": "violation"
                }
        ]
    ),
    (
        [
            {
                "article": "3",
                "base_article": "3",
                "details": ["substantive aspect"],
                "element": "No violation of Article 3",
                "type": "non-violation"},
            {
                "article": "2",
                "base_article": "2",
                "element": "No violation of Art. 2",
                "type": "non-violation"
            }
        ],
        [
            {
                "article": "3",
                "base_article": "3",
                "details": ["substantive aspect"],
                "element": "No violation of Article 3",
                "type": "non-violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "element": "No violation of Art. 2",
                "type": "non-violation"
            }
        ]
    ),
    (
        [
            {
                "article": "3",
                "base_article": "3",
                "details": ["substantive aspect"],
                "element": "No violation of Art. 3",
                "type": "non-violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "element": "No violation of Art. 2",
                "type": "non-violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "details": ["substantive aspect"],
                "element": "No violation of Art. 2",
                "type": "non-violation"
            }
        ],
        [
            {
                "article": "3",
                "base_article": "3",
                "details": ["substantive aspect"],
                "element": "No violation of Art. 3",
                "type": "non-violation"
            },
            {
                "article": "2",
                "base_article": "2",
                "details": ["substantive aspect"],
                "element": "No violation of Art. 2",
                "type": "non-violation"
            }
        ]
    )
]

columns = ['itemid', 'scl', 'respondent', 'extractedappno', 'separateopinion', 'kpdate', 'paragraphs', 'kpthesaurus',
           'languageisocode', 'rank', 'applicability', 'doctypebranch', 'typedescription', 'article',
           'originatingbody_name', 'importance', 'originatingbody_type', 'externalsources', '__articles',
           'representedby', 'introductiondate', 'country', 'decisiondate', 'judgementdate', 'documentcollectionid',
           '__conclusion', 'parties', 'application', 'respondentOrderEng', 'appno', 'sharepointid', 'docname',
           'originatingbody', 'conclusion', 'issue', 'ecli']

raw_cases_input = [{
    u'itemid': u'001-201353',
    u'scl': u'Abdulaziz, Cabales and Balkandali v. the United Kingdom, 28 May 1985, \xa7 67, Series A no. 94;Airey v. Ireland, 9 October 1979, \xa7 24, Series A no. 32;Al Dulimi and Montana Management Inc. v. Switzerland [GC], no. 5809/08, \xa7 134, 21 June 2016;Al Skeini and Others v. the United Kingdom [GC], no. 55721/07, \xa7 141, ECHR 2011;Ali v. Switzerland, 5 August 1998, \xa7\xa7 30-33, Reports of Judgments and Decisions 1998-V;Allen v. the United Kingdom [GC], no. 25424/09, \xa7 95, ECHR 2013;Amuur v. France, 25 June 1996, \xa7 43, Reports 1996 III;Andric v. Sweden (dec.), no. 45917/99, 23 February 1999;Assanidze v. Georgia [GC], no. 71503/01, ECHR 2004-II;Baka v. Hungary [GC], no. 20261/12, \xa7 149, 23 June 2016;Bankovi\u0107 and Others v. Belgium and Others (dec.), [GC], no. 52207/99, ECHR 2001-XII;Berisha and Haljiti v. the former Yugoslav Republic of Macedonia (dec.), no. 18670/03, ECHR 2005-VIII (extracts);Boujlifa v. France, 21 October 1997, \xa7 42, Reports 1997-VI;Cyprus v. Turkey (just satisfaction) [GC], no. 25781/94, \xa7 23, ECHR 2014;Davydov v. Estonia (dec.), no. 16387/03, 31 May 2005;Del R\xedo Prada v. Spain [GC], no. 42750/09, \xa7 81, ECHR 2013;Dritsas and Others v. Italy (dec.), no. 2344/02, 1 February 2011;El Masri v. the former Yugoslav Republic of Macedonia [GC], no. 39630/09;F.G. v. Sweden, [GC], no. 43611/11, \xa7\xa7 81-82, ECHR 2016;Gebremedhin [Gaberamadhien] v. France, no. 25389/05, \xa7\xa7 54-58, ECHR 2007 II;Georgia v. Russia (I) [GC], no. 13255/07, ECHR 2014 (extracts);Ghulami v. France (dec.), no. 45302/05, 7 April 2009;G\xfczelyurtlu and Others v. Cyprus and Turkey [GC], no. 36925/07, 29 January 2019;Hayd v. the Netherlands (dec.), no. 30880/10, 29 November 2011;Hirsi Jamaa and Others v. Italy [GC], no. 27765/09, ECHR 2012;Ibrahim and Others v. the United Kingdom [GC], nos. 50541/08 and 3 others, \xa7 272, 13 September 2016;Ila\u015fcu and Others v. Moldova and Russia [GC], no. 48787/99, ECHR 2004 VII;Ilias and Ahmed v. Hungary [GC], no. 47287/15, \xa7\xa7 123-28, 21 November 2019;J.K. and Others v. Sweden, no. 59166/12, \xa7\xa7 78 and 79, 4 June 2015;Kadzoev v. Bulgaria (dec.), no. 56437/07, \xa7 7, 1 October 2013;Kebe and Others v. Ukraine, no. 12552/12, \xa7 87, 12 January 2017;Khlaifia and Others v. Italy [GC], no. 16483/12, 15 December 2016;Leyla \u015eahin v. Turkey [GC], no. 44774/98, \xa7 136, ECHR 2005 XI;Loizidou v. Turkey (preliminary objections), 23 March 1995, \xa7 75, Series A no. 310;M.A. and Others v. Lithuania, no. 59793/17, 11 December 2018;M.A. v. Cyprus, no. 41872/10, ECHR 2013 (extracts);M.H. v. Cyprus (dec.), no. 41744/10, \xa7 14, 14 January 2014;M.Is. v. Cyprus (dec.), no. 41805/10, \xa7 20, 10 February 2015;M.S.S. v. Belgium and Greece [GC], no. 30696/09, ECHR 201;Matthews v. the United Kingdom [GC], no. 24833/94, ECHR 1999-I;Micallef v. Malta [GC], no. 17056/06, \xa7 48, ECHR 2009;N. v. the United Kingdom [GC], no. 26565/05, \xa7 30, ECHR 2008;Paposhvili v. Belgium, [GC], no. 41738/10, 13 December 2016;Ramzy v. the Netherlands (striking out), no. 25424/05, \xa7\xa7 64-66, 20 July 2010;Saadi v. Italy [GC], no. 37201/06, ECHR 2008;Sharifi and Others v. Italy and Greece, no. 16643/09, 21 October 2014;Soering v. the United Kingdom, 7 July 1989, \xa7 86, Series A no. 161;Sultani v. France, no. 45223/05, ECHR 2007-IV (extracts);United Communist Party of Turkey and Others v. Turkey, 30 January 1998, \xa7 29, Reports 1998-I',
    u'respondent': u'ESP', u'documentcollectionid2': u'CASELAW;JUDGMENTS;GRANDCHAMBER;ENG',
    u'kpthesaurus': u'293;210;444;110;183;498;14;128;398;609;648;241;59;341;578', u'languageisocode': u'ENG',
    u'applicability': u'true', u'doctypebranch': u'GRANDCHAMBER', u'separateopinion': u'TRUE',
    u'isplaceholder': u'False', u'representedby': u'GERICKE C. ; BOYE G.', u'introductiondate': u'01/01/2020',
    u'decisiondate': u'01/01/2020', u'documentcollectionid': u'CASELAW;JUDGMENTS;GRANDCHAMBER;ENG',
    u'kpdateAsText': u'13/02/2020 00:00:00', u'application': u'MS WORD', u'respondentOrderEng': u'44',
    u'appno': u'8675/15;8697/15', u'sharepointid': u'496286', u'docname': u'CASE OF N.D. AND N.T. v. SPAIN',
    u'originatingbody': u'8',
    u'issue': u'Institutional Law 4/2000 of 11 January 2000 on the rights and freedoms of aliens in Spain and their social integration (\u201cthe LOEX\u201d) ; Law 12/2009 of 30 October 2009 on asylum and subsidiary protection ; Royal Decree 203/1995 of 10 February 1995 (implementing regulations for the Law on asylum) ; Royal Decree 557/2011 of 20 April 2011 (implementing regulations for the LOEX) ; The Guardia Civil border control operations protocol of 26 February 2014 (as applicable at the relevant time), which introduced the term \u201coperational border\u201d ; Circular letter to all Spanish ambassadors of 20 November 2009 ; Annual report of the Spanish Ombudsperson of 2005 and 2013 ; Articles 2 and 6 from the European Union Treaty ; Articles 67, 72, 77, 78, and 79 of the Treaty on the Functioning of the European Union ; Articles 4, 18, 19 and 47 of the Charter of Fundamental Rights of the European Union ; Agreement on the accession of the Kingdom of Spain to the Convention implementing the Schengen Agreement of 14 June 1985 on the gradual abolition of checks at their common borders [between the contracting parties] ; Regulation (EC) No 562/2006 of the European Parliament and of the Council of 15 March 2006 establishing a Community Code on the rules governing the movement of persons across borders (Schengen Borders Code) ; Directive 2008/115/EC of the European Parliament and of the Council of 16 December 2008 on common standards and procedures in Member States for returning illegally staying third country nationals (\u201cthe Return Directive\u201d) ; Council Directive 2005/85/EC of 1 December 2005 on minimum standards on procedures in Member States for granting and withdrawing refugee status ; Directive 2011/95/EU of the European Parliament and of the Council of 13 December 2011 on standards for the qualification of third-country nationals or stateless persons as beneficiaries of international protection, for a uniform status for refugees or for persons eligible for subsidiary protection, and for the content of the protection granted (recast) ; European Parliament resolution of 12 April 2016 on the situation in the Mediterranean and the need for a holistic EU approach to migration (2015/2095(INI))',
    u'ecli': u'ECLI:CE:ECHR:2020:0213JUD000867515', u'importance': u'1', u'kpdate': u'2/13/2020 12:00:00 AM',
    u'judgementdate': u'13/02/2020 00:00:00',
    u'extractedappno': u'8675/15;8697/15;16483/12;47/15;646/16;444/17;391/16;77/17;78/17;2011/95;27765/09;60125/11;16643/09;30880/10;56437/07;25424/05;41744/10;41805/10;43611/11;41738/10;23531/94;39630/09;20261/12;52207/99;24833/94;48787/99;36925/07;71503/01;30696/09;55721/07;13255/07;18670/03;2344/02;2005/85;2013/32;37201/06;26565/05;44774/98;50541/08;5809/08;25781/94;59793/17;17056/06;42750/09;25424/09;59166/12;25389/05;12552/12;47287/15;45917/99;16387/03;45223/05;45302/05;41872/10;17502/07',
    u'typedescription': u'15', u'article': u'1;13;13+P4-4;34;35;35-1;35-3-a;37;37-1;37-1-b;37-1-c;P4-4',
    u'externalsources': u'Guidelines of the Committee of Ministers of the Council of Europe on Forced Return, adopted on 4 May 2005;Report of the European Committee for the Prevention of Torture and Inhuman or Degrading Treatment or Punishment (CPT) on their visit to Spain in July 2014 (published on 9 April 2015);The 2015 annual activity report by the Commissioner for Human Rights of the Council of Europe;Report of the fact-finding mission by the Special Representative of the Secretary General of the Council of Europe on migration and refugees, to Spain, March 2018 (SG/Inf(2018)25);Resolution 2299 (2019) of the Parliamentary Assembly of the Council of Europe on the pushback policies and practice in Council of Europe member States;Charter of the United Nations (UN Charter), signed on 26 June 1945 in San Francisco;Articles 27, 31 and 32 of the Vienna Convention on the Law of Treaties of 23 May 1969;Geneva Convention of 28 July 1951 relating to the Status of Refugees;Convention against Torture and Other Cruel, Inhuman or Degrading Treatment or Punishment of 10 December 1984 (UNCAT);Declaration on Territorial Asylum adopted by the United Nations General Assembly on 14 December 1967 (Resolution 2312 (XXII));Draft Articles on the Expulsion of Aliens adopted by the International Law Commission at their sixty-sixth session (2014) of which the United Nations General Assembly took note (Resolution A/RES/69/119 of 10 December 2014);Second report on the expulsion of aliens, dated 20 July 2006 (Document A/CN.4/573), by Mr Maurice Kamto, Special Rapporteur;Conclusions on International Protection adopted by the Executive Committee of the UNHCR Programme 1975 \u2013 2017;Views adopted by the Committee on the Rights of the Child on 12 February 2019 under the Optional Protocol to the Convention on the Rights of the Child on a communications procedure, concerning communication No. 4/2016',
    u'meetingnumber': u'', u'doctype': u'HEJUD', u'Rank': u'25.8842315673828',
    u'conclusion': u'Preliminary objection dismissed (Article 34 - Victim);Preliminary objection dismissed (Article 35-1 - Exhaustion of domestic remedies);Preliminary objection dismissed (Article 37-1 - Respect for human rights;Article 37-1-b - Matter resolved;Article 37-1-c - Continued examination not justified);Preliminary objection joined to merits and dismissed (Article 35-3-a - Ratione materiae);No violation of Article 4 of Protocol No. 4 - Prohibition of collective expulsion of aliens-{general} (Article 4 of Protocol No. 4 - Prohibition of collective expulsion of aliens);No violation of Article 13+P4-4 - Right to an effective remedy (Article 13 - Effective remedy) (Article 4 of Protocol No. 4 - Prohibition of collective expulsion of aliens-{general};Prohibition of collective expulsion of aliens)'
},
{
    u'itemid': u'001-119120',
     u'scl': u'Aktas v. Turkey, no. 24351/94, \xa7 301, ECHR 2003-V (extracts);Anguelova v. Bulgaria, no. 38361/97, \xa7\xa7 122, 140, ECHR 2002-IV;Cyprus v. Turkey [GC], no. 25781/94, \xa7\xa7 112-113, ECHR 2001-IV;Hugh Jordan v. the United Kingdom, no. 24746/94, \xa7\xa7 120, ECHR 2001-III;McKerr v. the United Kingdom, no. 28883/95, \xa7 128, 129, ECHR 2001-III;Nachova and Others v. Bulgaria [GC], nos 43577/98 and 43579/98, \xa7\xa7 110-113, ECHR 2005-VII;Ogur v. Turkey [GC], no. 21594/93, \xa7 78, ECHR 1999 III;Ramsahai and Others v. the Netherlands, no. 52391/99, \xa7 356-371, ECHR 2005 \u2026 (extracts);Romijn v. the Netherlands (dec.) no. 62006/00, 3 March 2005;Salman v. Turkey [GC], no. 21986/93, \xa7 100, ECHR 2000-VII;Tahsin Acar v. Turkey [GC], no. 26307/95, 223, ECHR 2004-III',
     u'respondent': u'NLD', u'documentcollectionid2': u'CASELAW;JUDGMENTS;GRANDCHAMBER;AZE',
     u'kpthesaurus': u'445;41;70;449;231;496;4;444;216', u'languageisocode': u'AZE', u'applicability': u'38',
     u'doctypebranch': u'GRANDCHAMBER', u'separateopinion': u'TRUE', u'isplaceholder': u'False',
     u'representedby': u'HAMER G.P.', u'introductiondate': u'01/01/2020', u'decisiondate': u'01/01/2020',
     u'documentcollectionid': u'CASELAW;JUDGMENTS;GRANDCHAMBER;AZE', u'kpdateAsText': u'15/05/2007 00:00:00',
     u'application': u'MS WORD', u'respondentOrderEng': u'32', u'appno': u'52391/99', u'sharepointid': u'427085',
     u'docname': u'CASE OF RAMSAHAI AND OTHERS v. THE NETHERLANDS - [Azerbaijani Translation] legal summary by the COE Human Rights Trust Fund',
     u'originatingbody': u'8',
     u'issue': u'Code of Criminal Procedure, Articles 12, 12d sqq., 140, 148 ; The Police Act 1993 (Politiewet) ; Standing Orders for the Police, the Royal Military Constabulary and officers invested with special investigative powers (1994) ; The Police Weapons Rules 1994 ; Rules governing the organisation of the operational divisions of the Public Prosecution Service ; Judiciary (Organisation) Act - at the time of the events complained of',
     u'ecli': u'ECLI:CE:ECHR:2007:0515JUD005239199', u'importance': u'1', u'kpdate': u'5/15/2007 12:00:00 AM',
     u'judgementdate': u'15/05/2007 00:00:00', u'extractedappno': u'52391/99', u'typedescription': u'15',
     u'article': u'2;2-2;2-1;6;6-1;13;41', u'externalsources': u'source', u'meetingnumber': u'1', u'doctype': u'HJUDAZE',
     u'Rank': u'17.1129493713379',
     u'conclusion': u'Violation of Art. 2;No violation of Art. 2;No separate issue under Art. 13;Non-pecuniary damage - financial award;Costs and expenses award - domestic proceedings;Costs and expenses partial award - Convention proceedings'
},
{
    u'itemid': u'001-120236',
     u'scl': u'C.R. v. the United Kingdom, judgment of 22 November 1995, Series A no. 335-C, pp. 68-69, \xa7\xa7 32-33 and 34;Co\xebme and Others v. Belgium, nos. 32492/96, 32547/96, 32548/96, 33209/96 and 33210/96, ECHR 2000-VII, \xa7\xa7 98, 99, 107-108;G. v. Switzerland, no. 16875/90, Commission decision of 10 October 1990;Heidegger v. Austria (dec.), no. 27077/95, 5 October 1999;K.-H. W. v. Germany [GC], no. 37201/97, \xa7 45, ECHR 2001-II;Kopp v. Switzerland, judgment of 25 March 1998, Reports of Judgments and Decisions 1998-II, p. 541, \xa7 59;K\xfcbli v. Switzerland, no. 17495/90, Commission decision of 2 December 1992;Lavents v. Latvia, no. 58442/00, \xa7 114, 28 November 2002;S.W. v. the United Kingdom, judgment of 22 November 1995, Series A no. 335-C, pp. 41-42, \xa7\xa7 34-35 and 36;Sahin v. Germany [GC], no. 30943/96, \xa7 87, ECHR 2003-VII;Schenk v. Switzerland, judgment of 12 July 1988, Series A no. 140, p. 29, \xa7 45;Sommerfeld v. Germany [GC], no. 31871/96, \xa7 86, ECHR 2003-VIII;Streletz, Kessler and Krenz v. Germany [GC], no. 34044/96, 35532/97, 44801/98, \xa7 49 and \xa7 50, ECHR 2001-II;Vidal v. Belgium, judgment of 22 April 1992, Series A no. 235, pp. 32-33, \xa7 33',
     u'respondent': u'DEU', u'documentcollectionid2': u'CASELAW;JUDGMENTS;CHAMBER;KAT;GEO',
     u'kpthesaurus': u'288;291;445;76;136;119;295;495;448;552;220', u'languageisocode': u'ENG', u'applicability': u'',
     u'doctypebranch': u'CHAMBER', u'separateopinion': u'FALSE', u'isplaceholder': u'False',
     u'representedby': u'GRUNBAUER H.', u'introductiondate': u'', u'decisiondate': u'',
     u'documentcollectionid': u'CASELAW;JUDGMENTS;CHAMBER;KAT;GEO', u'kpdateAsText': u'12/07/2007 00:00:00',
     u'application': u'MS WORD', u'respondentOrderEng': u'18', u'appno': u'74613/01', u'sharepointid': u'414931',
     u'docname': u'CASE OF JORGIC v. GERMANY \u2013 [Georgian Translation] by the COE Human Rights Trust Fund',
     u'originatingbody': u'23',
     u'issue': u'Articles 6,7 and 220a of the Criminal Code ; Article 244 \xa7\xa7 3 and 5 of the Code of Criminal Procedure',
     u'ecli': u'ECLI:CE:ECHR:2007:0712JUD007461301', u'importance': u'1', u'kpdate': u'7/12/2007 12:00:00 AM',
     u'judgementdate': u'12/07/2007 00:00:00',
     u'extractedappno': u'74613/01;58442/00;32492/96;32547/96;32548/96;33209/96;33210/96;16875/90;17495/90;27077/95;30943/96;31871/96;34044/96;35532/97;44801/98;37201/97',
     u'typedescription': u'14', u'article': u'5;5-1-a;5-1;6;6-1;6-3-d;7;7-1;29;29-3',
     u'externalsources': u'Convention on the Prevention and Punishment of the Crime of Genocide (1948);Convention on the Prevention and Suppression of Genocide (1948);Resolution of the UN General Assembly 47/121 of 18 December 1992;Case-law of the ICTY (Prosecutor v. Krstic, judgment of 2 August 2001;Prosecutor v. Kupreskic and Others, judgment of 14 January 2000) and ICJ (Bosnia and Herzegovina v. Serbia and Montenegro, judgment of 26 February 2007)',
     u'meetingnumber': u'', u'doctype': u'HJUDGEO', u'Rank': u'15.1129503250122',
     u'conclusion': u'Remainder inadmissible;No violation of Art. 6-1 or 5-1;No violation of Art. 7'
},
{
    u'itemid': u'001-63325',
     u'scl': u'Arr\xeat Axen c. Allemagne du 8 d\xe9cembre 1983, s\xe9rie A n\xb0 72, p. 12, \xa7 25, \xa7 28;Arr\xeat Colozza c. Italie du 12 f\xe9vrier 1985, s\xe9rie A n\xb0 89, pp. 14-15, \xa7\xa7 27-29;Arr\xeat Ekbatani c. Su\xe8de du 26 mai 1988, s\xe9rie A n\xb0 134, p. 14, \xa7 31;Arr\xeat Fejde du 29 octobre 1991, s\xe9rie A n\xb0 212-B, p. 68, \xa7 28;Arr\xeat Fey c. Autriche du 24 f\xe9vrier 1993, s\xe9rie A n\xb0 255, p. 12, \xa7 50;Arr\xeat Immobiliare Saffi c. Italie [GC], n\xb0 22774/93, \xa7 79, ECHR 1999-V;Arr\xeat Nortier c. Pays-Bas du 24 ao\xfbt 1993, s\xe9rie A n\xb0 267, p. 15, \xa7 33;Arr\xeat Padovani c. Italie du 26 f\xe9vrier 1993, s\xe9rie A n\xb0 257-B, p. 20, \xa7 25, \xa7 27;Arr\xeat Piersack c. Belgique du 1er octobre 1982, s\xe9rie A n\xb0 53, p. 15, \xa7 29;Arr\xeat Sutter c. Suisse du 22 f\xe9vrier 1984, s\xe9rie A n\xb0 74, p. 12, \xa7 26, \xa7 27',
     u'respondent': u'SMR', u'documentcollectionid2': u'CASELAW;JUDGMENTS;CHAMBER;FRA;FRE',
     u'kpthesaurus': u'445;180;385;296;216', u'languageisocode': u'FRE', u'applicability': u'',
     u'doctypebranch': u'CHAMBER', u'separateopinion': u'FALSE', u'isplaceholder': u'False', u'representedby': u'N/A',
     u'introductiondate': u'', u'decisiondate': u'', u'documentcollectionid': u'CASELAW;JUDGMENTS;CHAMBER;FRA;FRE',
     u'kpdateAsText': u'25/07/2000 00:00:00', u'application': u'MS WORD', u'respondentOrderEng': u'39',
     u'appno': u'24954/94;24971/94;24972/94', u'sharepointid': u'438578',
     u'docname': u'AFFAIRE TIERCE ET AUTRES c. SAINT-MARIN', u'originatingbody': u'4',
     u'issue': u'Code de proc\xe9dure p\xe9nale, articles 174-185, 197', u'ecli': u'ECLI:CE:ECHR:2000:0725JUD002495494',
     u'importance': u'1', u'kpdate': u'7/25/2000 12:00:00 AM', u'judgementdate': u'25/07/2000 00:00:00',
     u'extractedappno': u'24954/94;24971/94;24972/94;22774/93', u'typedescription': u'15', u'article': u'6;6-1;41',
     u'externalsources': u'', u'meetingnumber': u'', u'doctype': u'HEJUD', u'Rank': u'16.1129493713379',
     u'conclusion': u"Violation de l'Art. 6-1 du fait du manque d'impartialit\xe9 du tribunal;Violation de l'Art. 6-1 du fait de l'impossibilit\xe9 d'\xeatre entendu en personne par le juge d'appel;Dommage mat\xe9riel - demande rejet\xe9e;Pr\xe9judice moral - r\xe9paration p\xe9cuniaire;Remboursement partiel frais et d\xe9pens"
},
{
    u'itemid': u'001-202428', u'scl': u'', u'respondent': u'TUR',
     u'documentcollectionid2': u'CASELAW;JUDGMENTS;COMMITTEE;ENG', u'kpthesaurus': u'445;76;136;86',
     u'languageisocode': u'ENG', u'applicability': u'', u'doctypebranch': u'COMMITTEE', u'separateopinion': u'FALSE',
     u'isplaceholder': u'False', u'representedby': u'AKME\u015eE \u0130. ', u'introductiondate': u'',
     u'decisiondate': u'', u'documentcollectionid': u'CASELAW;JUDGMENTS;COMMITTEE;ENG',
     u'kpdateAsText': u'12/05/2020 00:00:00', u'application': u'MS WORD', u'respondentOrderEng': u'47',
     u'appno': u'8211/10', u'sharepointid': u'497700', u'docname': u'CASE OF CANLI v. TURKEY',
     u'originatingbody': u'26', u'issue': u'', u'ecli': u'ECLI:CE:ECHR:2020:0512JUD000821110', u'importance': u'4',
     u'kpdate': u'5/12/2020 12:00:00 AM', u'judgementdate': u'12/05/2020 00:00:00',
     u'extractedappno': u'8211/10;25253/08;36391/02;27422/05;38802/08;21980/04;36658/05;71409/10;57837/09;50541/08;22744/07;76577/13;34779/09;4268/04;42371/02;25703/11;2308/06;48016/06;7817/07;9106/09;46661/09;7851/05;38907/09;30733/08',
     u'typedescription': u'15', u'article': u'6;6+6-1;6-1;6-3-c', u'externalsources': u'', u'meetingnumber': u'',
     u'doctype': u'HEJUD', u'Rank': u'12.1129503250122',
     u'conclusion': u'Article 6+6-1 - Right to a fair trial (Article 6-3-c - Defence through legal assistance) (Article 6 - Right to a fair trial;Criminal proceedings;Article 6-1 - Fair hearing)'
},
{
    u'itemid': u'001-202608', u'scl': u'', u'respondent': u'TUR',
     u'documentcollectionid2': u'CASELAW;JUDGMENTS;COMMITTEE;ENG', u'kpthesaurus': u'145;151',
     u'languageisocode': u'ENG', u'applicability': u'', u'doctypebranch': u'COMMITTEE', u'separateopinion': u'FALSE',
     u'isplaceholder': u'True', u'representedby': u'ALTUNTA\u015e M.', u'introductiondate': u'', u'decisiondate': u'',
     u'documentcollectionid': u'CASELAW;JUDGMENTS;COMMITTEE;ENG', u'kpdateAsText': u'19/05/2020 00:00:00',
     u'application': u'NULL', u'respondentOrderEng': u'47', u'appno': u'45540/09', u'sharepointid': u'497641',
     u'docname': u'CASE OF SEYFETT\u0130N DEM\u0130R v. TURKEY', u'originatingbody': u'26', u'issue': u'',
     u'ecli': u'ECLI:CE:ECHR:2020:0519JUD004554009', u'importance': u'4', u'kpdate': u'5/19/2020 12:00:00 AM',
     u'judgementdate': u'19/05/2020 00:00:00', u'extractedappno': u'', u'typedescription': u'15',
     u'article': u'11;11-1', u'externalsources': u'', u'meetingnumber': u'', u'doctype': u'HEJUD',
     u'Rank': u'',
     u'conclusion': u'Violation of Article 11 - Freedom of assembly and association (Article 11-1 - Freedom of peaceful assembly)'
}
]
