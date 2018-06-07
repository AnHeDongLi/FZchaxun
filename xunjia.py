# -*- coding:utf-8 -*-
import time
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import json
from json.decoder import JSONDecodeError
from fake_useragent import UserAgent
import re
from urllib.parse import urlencode
from selenium.webdriver.chrome.options import Options
import Proxys
from gevent import monkey
import gevent
from selenium import webdriver

monkey.patch_all(ssl=False)

se = requests.Session()


# def get_cookie():
#     url = 'https://sjipiao.fliggy.com/flight_search_result.htm?_input_charset=utf-8&spm=181.7091613.a1z67.1001&searchBy=1280&tripType=0&depCityName=%E5%8C%97%E4%BA%AC&depCity=&depDate=2018-06-08&arrCityName=%E4%B8%8A%E6%B5%B7&arrCity=SHA&arrDate='
#     options = Options()
#     options.add_argument('-headless')
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     try:
#         c_list = []
#         for i in driver.get_cookies():
#             c_list.append(i['name']+'='+i['value'])
#         cookies = ';'.join(c_list)
#         return cookies
#     except:
#         return get_cookie()
#     finally:
#         driver.quit()

# cookies = get_cookie()
# print(cookies)

def headers():
    ua = UserAgent().random
    headers = {
        'User-Agent': ua,
        # 'X-DevTools-Emulate-Network-Conditions-Client-Id': '5D11684B2A36545823A4061215BAD355',
        'Cookie': 1
    }
    return headers


def request(url):
    if url:
        url = url.strip()
    try:
        response = se.get(url, headers=headers(), proxies=Proxys.get_proxy(), timeout=10)  # , proxies=Proxy.get_proxy()
        if response.status_code == 200 and 'jsonp' in response.text:
            _str = re.sub(r'jsonp\d+\(|\);|\(|\)', '', response.text).strip()
            if re.findall('\d+:{', _str):
                for i in re.findall('\d+:{', _str):
                    n = re.search('\d+', i)[0]
                    _str = re.sub(i, '"{n}":'.format(n=n) + '{', _str)
                return json.loads(_str)
            else:
                return json.loads(_str)
        else:
            return request(url)
    except (ConnectionError, JSONDecodeError, ReadTimeout):
        print('请求出错，正在重试')
        return request(url)


def base(dn, an, dd, rd='', sk='', qid='', fn='', te='', ca=''):
    base = {
        'callback': ca,
        'tripType': '0',
        'depCityName': dn,
        'arrCityName': an,
        'depDate': dd,
        'arrDate': rd,
        'searchSource': '99',
        'searchBy': '1280',
        'sKey': sk,
        'qid': qid,
        'flightNo': fn,
        'type': te,
        'needMemberPrice': 'true',
        '_input_charset': 'utf-8',
        'openCb': 'false'
    }
    if sk == '' and qid == '':
        return get_index(base)


def get_index(base):
    url = 'https://sjipiao.fliggy.com/searchow/search.htm?'
    url = url+urlencode(base)
    print('正在请求主页')
    return get_flightNo(request(url), base)


def get_token(flightNo_data):
    return [flightNo_data['qid'], flightNo_data['skey']]


def get_flightNo(flightNo_data, *args):
    print('主页请求成功')
    token = get_token(flightNo_data)
    _dict = flightNo_data['data']['airportMap']
    threads = [gevent.spawn(get_flight_list, i['flightNo'], token[0], token[1], args, {
        'depAirport': _dict[i['depAirport']] + i['depTerm'],
        'arrAirport': _dict[i['arrAirport']] + i['arrTerm'],
        'depTime': i['depTime'],
        'arrTime': i['arrTime'],
        'flightNo': i['flightNo'],
        'tax': 60
    }) for i in flightNo_data['data']['flight']]
    gevent.joinall(threads)


def get_flight_list(*args):
    base = args[3][0]
    flightNo = args[0]
    qid = args[1]
    sKey = args[2]
    base['qid'] = qid
    base['sKey'] = sKey
    base['flightNo'] = flightNo
    base['type'] = 'lowprice'
    base['callback'] = 'jsonp5895'
    url = 'https://sjipiao.fliggy.com/searchow/search.htm?'
    url = url + urlencode(base)
    print(url)
    print('正在请求', args[0], '航班信息')
    return get_detail(request(url), args[4])


def get_detail(detail_data, *args):
    print(args[0]['flightNo'], '航班信息请求成功')
    base = {}
    base['callback'] = 'jsonp4327'
    base['depCity'] = detail_data['data']['depCityCode']
    base['arrCity'] = detail_data['data']['arrCityCode']
    base['date'] = detail_data['data']['flight']['depTime'].split(' ')[0]
    base['airline'] = detail_data['data']['flight']['airlineCode']
    base['subFareId'] = ''
    base['depAirport'] = detail_data['data']['flight']['depAirport']
    base['arrAirport'] = detail_data['data']['flight']['arrAirport']
    for i in detail_data['data']['cabin']:
        base['cabin'] = i['cabin']
        base['discount'] = i['discount']
        base['ticketPrice'] = i['ticketPrice']
        base['agentId'] = i['agentId']
        base['fareType'] = i['fareType']
        base['fareId'] = i['fareId']
        base['policyId'] = i['policyId']
        if 'airlineProductCode' in i:
            base['productCode'] = i['airlineProductCode']
        else:
            base['productCode'] = ''
        base['price'] = i['price']
        base['basicCabinPrice'] = i['basicCabinPrice']
        base['sprodType'] = i['sprodType']
        base['salePrice'] = i['bestPrice']
        args[0]['cabin'] = i['cabin']
        args[0]['cabinName'] = i['specialType']
        args[0]['price'] = i['price']
        url = 'https://sjipiao.fliggy.com/nsearch/tuigaiqianJson.htm?'
        url = url+urlencode(base)
        get_detail_2(request(url), args[0])


data_list = []


def get_detail_2(data, *args):

    toupiao = data['data'][0]['tuigaiqian']
    args[0]['rule'] = toupiao
    data_list.append(args[0])


def main(depair, arrair, deptime, arrtime='', ca='jsonp159'):
    base(depair, arrair, deptime, rd=arrtime, ca=ca)
    return data_list


if __name__ == '__main__':
    time_start = time.time()
    main()
    time_end = time.time()
    print(time_end-time_start)

