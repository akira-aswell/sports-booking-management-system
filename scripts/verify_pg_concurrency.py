"""Local demo only: concurrent HTTP requests to a free future 60-minute slot.
Requires a real PostgreSQL-backed stack for the intended acceptance evidence.
This script cannot determine the backend DB dialect; verify it separately.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',default='http://127.0.0.1:8000/api')
    p.add_argument('--court',type=int,required=True);p.add_argument('--date',type=date.fromisoformat,required=True)
    p.add_argument('--workers',type=int,default=50)
    p.add_argument('--email',default='player@demo.example.com');p.add_argument('--password',default='Demo123!')
    a=p.parse_args();base=a.base.rstrip('/')
    if urlparse(base).hostname not in ('localhost','127.0.0.1','::1'):p.error('Local demo only')
    if not 2<=a.workers<=50:p.error('workers must be 2–50')
    start=datetime.combine(a.date,time(18),timezone(timedelta(hours=7)));end=start+timedelta(hours=1)
    if start<=datetime.now(start.tzinfo):p.error('Choose a future date')
    def request(path,data=None,token=None):
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        try:
            with urlopen(Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers),timeout=60) as r:
                return r.status,json.loads(r.read())
        except HTTPError as e:return e.code,e.read().decode(errors='replace')
        except (URLError,TimeoutError) as e:return 0,str(e)
    code,body=request('/auth/login',{'email':a.email,'password':a.password})
    if code!=200:print('Login failed:',code,body);return 1
    token=body['access_token'];code,body=request(f'/courts/{a.court}/availability?date={a.date.isoformat()}&duration_minutes=60')
    if code!=200 or not any(datetime.fromisoformat(s['start_at'])==start and s['available'] for s in body['slots']):
        print('Slot not available; select a different court/date.');return 1
    payload={'court_id':a.court,'start_at':start.isoformat(),'end_at':end.isoformat(),'note':'Local concurrency verification'}
    with ThreadPoolExecutor(max_workers=a.workers) as executor:
        results=list(executor.map(lambda _:request('/bookings',payload,token),range(a.workers)))
    counts=Counter(status for status,_ in results);ids=[body['id'] for status,body in results if status==201]
    print('HTTP counts:',dict(counts),'Booking IDs:',ids)
    ok=counts==Counter({201:1,409:a.workers-1})
    print('PASS' if ok else 'FAIL','— verify SQL allocation and PostgreSQL dialect separately; cancel disposable booking after recording evidence.')
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
