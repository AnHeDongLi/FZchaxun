import requests
from requests.exceptions import ConnectionError


def get_proxy():
    global res
    try:
        url = '1111'
        res = requests.get(url).json()
        if res['ret'] == 1:
            proxy = '11111'
            proxies = {'http': 'http://'+proxy, 'https': 'https://'+proxy}
            print('获取代理成功:', res['data']['ip'])
            return proxies
        else:
            print('获取代理失败，正在重试')
            return get_proxy()
    except ConnectionError:
        print('请求代理出错，正在重试')
        return get_proxy()
    finally:
        requests.get(
            '1111')
        # print('释放代理成功')


if __name__ == '__main__':

    print(requests.get('http://httpbin.org/get', proxies=get_proxy()).text)