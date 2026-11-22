#!/usr/bin/env python3
"""Read-only source proof. Normalized research fixtures, not a deployed collector."""
import argparse, concurrent.futures, datetime as dt, hashlib, http.cookiejar, json, re, time
from pathlib import Path
from urllib.parse import urlencode,urljoin,urlsplit,parse_qs
from urllib.request import Request,urlopen,build_opener,HTTPCookieProcessor
from lxml import html
ROOT=Path(__file__).resolve().parents[1]/'.cache'
ROOT.mkdir(exist_ok=True)
UA='CoolCode.ca public-records research (read-only)'
OIC='https://www.oic-ci.gc.ca'
PCO='https://orders-in-council.canada.ca/'

def txt(e):return ' '.join(e.itertext()).split() if e is not None else []
def text(e):return ' '.join(txt(e))
def tree(raw):return html.fromstring(raw.decode('utf-8-sig'))
def get(url,path=None,opener=None,data=None):
 if path and path.exists():return path.read_bytes()
 for attempt in range(3):
  try:
   response=(opener.open if opener else urlopen)(Request(url,data=data,headers={'User-Agent':UA}),timeout=50)
   raw=response.read(12_000_001)
   if len(raw)>12_000_000:raise ValueError('Oversize page')
   if path:path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(raw)
   return raw
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)

def field(row,name):
 return [text(e) for e in row.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," field--name-'+name+' ")]//*[contains(concat(" ",normalize-space(@class)," ")," field--item ")]')]
def outcome(summary):
 # Literal outcome sentences only. Preserve text for manual interpretation.
 patterns=[('not well founded',r'\b(?:complaints? (?:is|are|was|were)|conclude(?:s|d)? (?:that )?(?:the )?complaints? (?:is|are|was|were)) not well[- ]founded\b'),('well founded',r'\bcomplaints? (?:is|are|was|were) well[- ]founded\b'),('application partially granted',r'\bapplication (?:is|was) partially granted\b'),('application denied',r'\bapplication (?:is|was) denied\b'),('application granted',r'\bapplication (?:is|was) granted\b')]
 found=[label for label,pattern in patterns if re.search(pattern,summary,re.I)]
 return '; '.join(found) if found else 'Not classified from summary'

def parse_oic(raw):
 doc=tree(raw);records=[]
 for a in doc.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," decisions ")]'):
  links=a.xpath('.//h3[contains(@class,"decision-title")]/a');
  if not links:continue
  link=links[0];title=text(link);date_el=a.xpath('.//*[contains(@class,"decision-date-day")]')
  ds=text(date_el[0]);listing_date=dt.datetime.strptime(ds,'%b %d %Y').date().isoformat()
  summary=' '.join(field(a,'body'));sections=field(a,'field-section-of-the-act');types=field(a,'field-decision-type');institutions=field(a,'field-institution')
  issues=[];lower=summary.lower()
  if any(t in lower for t in ('deemed refusal','did not respond','failed to respond','respond within','response to the access request within')):issues.append('Delay / deemed refusal')
  if any(t in lower for t in ('extension of time','time extension')):issues.append('Extension of time')
  if any(t in lower for t in ('reasonable search','search for records')):issues.append('Search for records')
  if any(t in lower for t in ('improperly withheld','exemption','refused to disclose')):issues.append('Withholding / exemptions')
  if 'declining to act on a request' in ' '.join(types).lower():issues.append('Permission to decline to act')
  if not issues:issues=['Other / review source']
  records.append({'id':'oic-'+a.get('data-history-node-id'),'title':title,'date':listing_date,'date_basis':'listing date','listing_date':listing_date,'decision_date':None,'institution':'; '.join(x for x in institutions if x!='-') or 'Not named','institutions':[x for x in institutions if x!='-'],'sections':sections,'decision_types':types,'issues':issues,'issue_basis':'Summary keyword tags; review source','outcome':outcome(summary),'summary':summary,'source_url':urljoin(OIC,link.get('href'))})
 links=doc.xpath('//a[@rel="last"]/@href');last=int(parse_qs(urlsplit(links[0]).query)['page'][0]) if links else 0
 count=re.search(r'(\d[\d,]*) decisions found',text(doc))
 return records,last,int(count.group(1).replace(',','')) if count else None

def decision_dates():
 raw=get(OIC+'/en/decisions/final-reports',ROOT/'final-reports.html');doc=tree(raw);dates={}
 for link in doc.xpath('//main//a[contains(@href,"/en/decisions/final-reports/")]'):
  parent=text(link.getparent());match=re.search(r'\(([A-Z][a-z]+)\s+(\d{1,2})[,.]?\s+(\d{4})\)',parent)
  if match:
   try:date=dt.datetime.strptime(' '.join(match.groups()),'%B %d %Y').date().isoformat()
   except ValueError:continue
   url=urljoin(OIC,link.get('href'));dates[url]=date
 return dates

def collect_oic():
 first=get(OIC+'/en/decisions?page=0',ROOT/'oic-pages/0.html');rows,last,expected=parse_oic(first)
 def one(page):
  time.sleep(.25)
  raw=get(OIC+f'/en/decisions?page={page}',ROOT/f'oic-pages/{page}.html');r,_,n=parse_oic(raw)
  if not r:raise ValueError('Empty OIC page '+str(page))
  return page,r
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for page,r in pool.map(one,range(1,last+1)):
   rows.extend(r)
   if page%10==0:print('OIC pages',page,'/',last,flush=True)
 unique={r['id']:r for r in rows}
 if len(unique)!=expected:raise ValueError(f'Expected {expected} unique OIC records, saw {len(unique)}')
 dates=decision_dates()
 for row in unique.values():row['decision_date']=dates.get(row['source_url'])
 result={'schema':1,'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source_url':OIC+'/en/decisions','coverage':'All decisions returned by source pagination','expected_count':expected,'count':len(unique),'dates_note':'Listing date is retained separately from the decision date in final reports; do not substitute one for the other.','rows':list(unique.values())}
 (ROOT/'atipdecisions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 qraw=get(OIC+'/en/information-commissioners-guidance/quarterly-statistics',ROOT/'quarterly.html');qd=tree(qraw)
 tables=[]
 for table in qd.xpath('//main//table'):
  tables.append({'caption':text(table.find('caption')),'rows':[[text(c) for c in row.xpath('./th|./td')] for row in table.xpath('.//tr')]})
 (ROOT/'quarterly-tables.json').write_text(json.dumps({'source_url':OIC+'/en/information-commissioners-guidance/quarterly-statistics','tables':tables},ensure_ascii=False,indent=2)+'\n')
 print('OIC complete',len(unique),'decision dates',sum(bool(r['decision_date']) for r in unique.values()),flush=True)

def parse_pco(raw):
 doc=tree(raw);rows=[]
 for tr in doc.xpath('//table[@id="results"]/tbody/tr'):
  cells=tr.xpath('./td')
  if len(cells)!=10:raise ValueError('Unexpected PCO columns '+str(len(cells)))
  vals=[text(e) for e in cells];pc,date,chapter,chapter_year,bill,department,act,subject,precis,registration=vals
  if not re.fullmatch(r'\d{4}-\d{4}',pc):raise ValueError('Bad PC number '+pc)
  dt.date.fromisoformat(date)
  links=cells[0].xpath('.//a/@href');sources=[urljoin(PCO,link) for link in links]
  rows.append({'id':pc,'title':subject,'date':date,'department':department,'statute':act,'summary':precis,'chapter':chapter,'chapter_year':chapter_year,'bill':bill,'registration':registration,'source_url':sources[0] if sources else PCO,'attachments':sources})
 nextlinks=doc.xpath('//a[@rel="next"]/@href');return rows,urljoin(PCO,nextlinks[0]) if nextlinks else None

def collect_pco():
 opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 payload=urlencode({'pcNumber':'','fromDate':'2026-01-01','toDate':'2026-11-22','keywords':'','department':'','act':'','chapterNumber':'','chapterYear':'','billNumber':'','foa':'na','leaveBlank':'','searchList':'Search / List'}).encode()
 raw=get(PCO+'index.php?lang=en',opener=opener,data=payload);rows,nexturl=parse_pco(raw);Path(ROOT/'pco-pages').mkdir(exist_ok=True);(ROOT/'pco-pages/1.html').write_bytes(raw)
 seen=set();page=1
 while nexturl:
  if nexturl in seen:raise ValueError('PCO pagination loop')
  seen.add(nexturl);page+=1
  time.sleep(.25)
  raw=get(nexturl,opener=opener);(ROOT/f'pco-pages/{page}.html').write_bytes(raw);r,nexturl=parse_pco(raw)
  if not r:raise ValueError('Unexpected empty PCO page')
  rows.extend(r)
  if page%20==0:print('PCO pages',page,'records',len(rows),flush=True)
  if page>500:raise ValueError('PCO safety limit')
 unique={r['id']:r for r in rows}
 if len(unique)!=len(rows):raise ValueError('Duplicate PCO rows across pages')
 if any(not '2026-01-01'<=r['date']<='2026-11-22' for r in rows):raise ValueError('PCO did not honour selected date range')
 result={'schema':1,'captured_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source_url':PCO,'coverage':'Date made 2026-01-01 through 2026-11-22, all returned pages','from':'2026-01-01','through':'2026-11-22','pages':page,'count':len(rows),'rows':rows}
 (ROOT/'oicdiary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PCO complete',len(rows),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',choices=['oic','pco','all']);a=p.parse_args()
 if a.source=='all':
  with concurrent.futures.ThreadPoolExecutor(2) as pool:
   futures=[pool.submit(collect_oic),pool.submit(collect_pco)]
   for f in futures:f.result()
 elif a.source=='oic':collect_oic()
 else:collect_pco()
