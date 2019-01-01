import requests
import re
import sys
import argparse
import threading
import random

__BANNER__ = '''
{r}    db    88   88 888888  dP"Yb  {w} VISITOR BLOG 0.1
{r}   dPYb   88   88   88   dP   Yb
{r}  dP__Yb  Y8   8P   88   Yb   dp {b} fb.com/zvtyrdt {r}*{w}
{r} dP""""Yb `YbodP'   88    YbodP  {w} ================
'''

def log(me, ex=False):
    print('\r' + me.format( r='\x1b[31m', w='\x1b[0m', b='\x1b[34m',
                     plus='\x1b[32m[+]\x1b[0m', bad='\x1b[31m[!]\x1b[0m',
                     tab='    ', inf='\x1b[34m[*]\x1b[0m',
                     badbut='\x1b[33m[+]\x1b[0m'
                   ))
    if ex: sys.exit()

class get_data:
    def __init__(self):
        self.ref = ["https://google.com", "https://google.co.uk",
                    "https://nekopoi.com", "https://xnxx.com",
                    "https://nekopoi.lol", "https://nekopoi.care",
                    "https://brazzers.com", "https://google.co.id",
                    "https://nekopoi.org", # tambahin sendiri, w capek
                    "https://m.facebook.com/zvtyrdt", "https://yahoo.com"
                    "https://www.facebook.com/zvtyrdt", "https://baidu.com",
                    "https://mbasic.facebook.com/zvtyrdt",
                    "https://m.facebook.com/putriy.kaeysha",
                    "https://www.facebook.com/putriy.kaeysha",
                    "https://mbasic.facebook.com/putriy.kaeysha"]

        self.UrlList = ["https://free-proxy-list.net/", "https://www.us-proxy.org",
                        "http://free-proxy-list.appspot.com/proxy.json",
                        "http://www.useragentstring.com/pages/useragentstring.php?name={}".format(arg.useragent.capitalize())]

        self.ua = self.UserAgent()
        self.proxy = self.ProxyList() if not arg.proxylist else self.openFile(arg.proxylist)
        log('{inf} %s proxies retrieved' % len(self.proxy))

    def openFile(self, f):
        log('{inf} get the proxylist from the file (%s)' % f)
        return [i.strip() for i in open(f, 'r').readlines() if i.strip()]

    def UserAgent(self):
        ua = []
        log('{inf} grab a list of user agents')
        ua += re.findall(r'<a href=\'\/index.php\?id\=\d*?\'>(.*?)<\/a>', self.grabContent(3))
        log('{inf} %s user agents retrieved (device %s)' % (len(ua), arg.useragent.capitalize()))

        return ua

    def ProxyList(self):
        proxy = []
        log('{inf} grab multiple proxies')
        for _ in range(2):
            proxy += self.reProxy(_)
        proxy += self.by_json(2, ('Host', 'Port'))
        return proxy

    def by_json(self,num, sp):
        r = requests.get(self.UrlList[num])
        final = ['{}:{}'.format(i[sp[0]], i[sp[1]]) for i in r.json()]
        log('{tab}{plus} got %s proxies from %s' % (len(final), self.UrlList[num]))

        return final
    def reProxy(self, num):
        prox = re.findall(r'<td>(.*?)<\/td>', self.grabContent(num))
        final = [':'.join(prox[:2]) for prox in [prox[i:i+4] for i in range(0,len(prox), 4)]][:-5]
        log('{tab}{plus} got %s proxies from %s' % (len(final), self.UrlList[num]))

        return final
    def grabContent(self, num):
        return requests.get(self.UrlList[num]).content

def listUA():
    r = requests.get('http://www.useragentstring.com/pages/useragentstring.php')
    return ['all'] + [i.lower().replace(' ', '') for i in re.findall(r'<a href=\'\/pages\/useragentstring.php\?name=(.*?)\'.*?<\/a>', r.text)]

class visit:
    def __init__(self):
        self.URL = self.parseFileUrl() if arg.fileurl else [arg.url]
        self.data = get_data()
        self.th = self.addThread()
        self.startVisiting()

    def startVisiting(self):
        for i in self.th:
            i.start()

    def addThread(self):
        temp = []
        dot = 1
        un = True
        for i in self.URL:
            for _ in range(1, arg.limit + 1):
                if dot % 10 == 0:
                    dot = 1
                print('\r\x1b[34m[*]\x1b[0m {1}: prepairing{0:<10}'.format('.'*dot, i)),
                sys.stdout.flush()
                try:
                    prox = self.data.proxy[_-1]
                except IndexError:
                    if un:
                        log('\n{badbut} warning: the number of proxies is not enough, starting to randomize the proxy')
                        un = False
                    prox = random.choice(self.data.proxy)
                temp.append(threading.Thread(target=self.makeRequests, args=(_, i, prox, random.choice(self.data.ua), random.choice(self.data.ref),)))
                dot += 1
            dot = 1
        print('') # new line
        return temp

    def makeRequests(self, num, url, proxy, ua, refer):
        hdr = {'User-Agent': ua, 'referer': refer}
        prox = {'https': proxy, 'http': proxy}

        try:
            r = requests.get(url, headers=hdr, proxies=prox, timeout=arg.timeout)
            if r.status_code == 200:
                log('{plus} Thread-%s: %s visiting web [status %s]' % (num, proxy.split(':')[0], r.status_code))
            else:
                log('{badbut} Thread-%s: %s visiting web [status %s]' % (num, proxy.split(':')[0], r.status_code))
        except Exception as e:
            log('{bad} Thread-%s: %s' % (num, e))

    def parseFileUrl(self):
        return [i.strip() for i in open(arg.fileurl, 'r').readlines() if i.strip()]

if __name__ == '__main__':
    log(__BANNER__)

    if sys.version.split(' ')[0][:3] != '2.7':
        log('{bad} use python version 2.7.x', True)

    list_ua = listUA()
    parse = argparse.ArgumentParser(epilog='https://github.com/zevtyardt')
    parse.add_argument('-u', '--url', metavar='', dest='url', help='enter the URL / Link blog, for the single visitor link')
    parse.add_argument('-f', '--file-url', metavar='', dest='fileurl', help='enter the .txt file that lists your blog links')
    parse.add_argument('-v', '--value', metavar='', dest='limit', type=int, help='enter How many visitors do you need for your blog', default=10)
    parse.add_argument('--pr', metavar='filename', dest='proxylist', help='enter your proxy list')
    parse.add_argument('--ua','--useragent',  metavar='', dest='useragent', help='name of the user agent device, default Chrome', default='Chrome', choices=list_ua)
    parse.add_argument('-t', '--timeout', metavar='', dest='timeout', type=int, default=10, help='timeout requests, default 10')
    parse.add_argument('--list-device-UA', action='store_true', dest='listua', help='print list of available user agent devices')
    arg = parse.parse_args()

    if arg.listua:
        for num, ua in enumerate(list_ua, start=1):
            if num % 4 == 0:
                sys.stdout.write('\n')
            sys.stdout.write('\x1b[34m[%s]\x1b[0m %s ' % (num, ua))
        print('') # new line

    elif arg.url or arg.fileurl:
        if arg.url:
            if not re.match(r'^http[s]?:\/\/.*?\.(.*?)', arg.url):
                log('{bad} website url is invalid (%s)' % arg.url, True)

        try:
            visit()
        except KeyboardInterrupt:
            log('{bad} user interrupt')
        except Exception as e:
            log('{bad} %s' % e)

    else: parse.print_help()
