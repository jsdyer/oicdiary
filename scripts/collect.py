from common import ROOT,save
import source,json,argparse,datetime,concurrent.futures,http.cookiejar,time
from urllib.request import build_opener,HTTPCookieProcessor
from urllib.parse import urlencode

def period(start,end):
 opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 payload=urlencode({'pcNumber':'','fromDate':start,'toDate':end,'keywords':'','department':'','act':'','chapterNumber':'','chapterYear':'','billNumber':'','foa':'na','leaveBlank':'','searchList':'Search / List'}).encode()
 raw=source.get(source.PCO+'index.php?lang=en',opener=opener,data=payload);rows,nexturl=source.parse_pco(raw);seen=set()
 while nexturl:
  if nexturl in seen or len(seen)>500:raise ValueError('Invalid source pagination')
  seen.add(nexturl);time.sleep(.3);part,nexturl=source.parse_pco(source.get(nexturl,opener=opener))
  if not part:raise ValueError('Unexpected empty results page')
  rows+=part
 if any(not start<=r['date']<=end for r in rows):raise ValueError('Source ignored date range')
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',action='store_true');a=p.parse_args();today=datetime.date.today();start=f'{today.year}-01-01';end=today.isoformat()
 if a.seed:
  d=json.loads((source.ROOT/'oicdiary.json').read_text());rows=d['rows'];start=d['from'];end=d['through']
 else:
  periods=[]
  for month in [1,4,7,10]:
   begin=datetime.date(today.year,month,1)
   if begin>today:continue
   finish=min(today,datetime.date(today.year+1,1,1)-datetime.timedelta(days=1) if month==10 else datetime.date(today.year,month+3,1)-datetime.timedelta(days=1));periods.append((begin.isoformat(),finish.isoformat()))
  with concurrent.futures.ThreadPoolExecutor(2) as pool:rows=[r for group in pool.map(lambda p:period(*p),periods) for r in group]
 if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate order IDs')
 for r in rows:r['order']=r['id'];r['year']=r['date'][:4]
 rows.sort(key=lambda r:(r['date'],r['id']),reverse=True)
 save(rows,sources=[{'label':'Privy Council Office public search','url':source.PCO},{'label':'About Orders in Council','url':'https://www.canada.ca/en/privy-council/services/orders-in-council.html'}],coverage=f'All returned orders approved {start} through {end} · official database also covers earlier years',warnings=['A newly observed order may have an earlier approval date. Some orders are withheld under statutory restrictions.','Collector version 2 follows numbered tail pages even where the source omits its Next link. Additions versus version 1 can reflect expanded extraction coverage.'],extra={'collector_version':2})
if __name__=='__main__':main()
