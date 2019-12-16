# -*-coding:utf-8-*-
# 爬取大众点评评论
import requests
import time
import re

data_dict = {
}

def get_css_url(html):
    # 获取css文件的内容
    regex = re.compile(r'(s3plus\.meituan\.net.*?)\"')
    css_url = re.search(regex, html).group(0)
    css_url = 'http://' + css_url
    return css_url

def dzdp_spider(item, cookies):
    addr = item
    # 拿到shop_id
    shop_id = addr.split('/')[-1]
    print("shop_id: ", shop_id)
    f = open('/Users/mac/Documents/projects/dataAnalyse/python/dzdpSpider/' + shop_id + '.txt', mode='a')

    for page in range(378, 379):
        print('page: ' + str(page))
        url = ''
        if page == 1:
            url = "http://www.dianping.com/shop/" + shop_id + "/review_all"
        else:
            url = "http://www.dianping.com/shop/" + shop_id + "/review_all/p" + str(page)
        print(url)

        headers = {

            "Host": "www.dianping.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "http://www.dianping.com/shop/8944191/review_all/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": cookies,
        }
        def requests_download(request_max=101):

            result_html = ""
            result_status_code = ""
            try:
                # proxies = get_proxies()
                s = requests.session()
                result = s.get(url=url, headers=headers, verify=False,timeout=20)
                result_html = result.content
                result_status_code = result.status_code
                # print('trace: 1')
                # print('result_status_code ' + str(result_status_code))
                if result_status_code != 200:
                    result = s.get(url=url, headers=headers, verify=False, timeout=20)
                    result_html = result.content
                    result_status_code = result.status_code
                    print('trace: 2')
                    # print('result_status_code ' + str(result_status_code))
            except Exception as e:
                print('trace: 3')
                # print('result_status_code ' + str(result_status_code))

                if request_max > 0:
                    if result_status_code != 200:
                        time.sleep(2)
                        return requests_download(request_max - 1)
            return result_html
        # 得到全部的html

        result_all = requests_download(request_max=11)
        result_all = result_all.decode('utf-8')
        print(str(result_all))
        result_all = re.sub(r'\n*', '', result_all)
        #if 'login' in result_all:
        #    raise Exception('出现登录窗口，重新设置cookie.')

        # 得到css的路径
        css_url = get_css_url(result_all)
        css_url = css_url.replace('"', '')
        # print(css_url)
        # 得到css文件内容
        resp = requests.get(css_url)
        css_html = resp.content.decode('utf-8')
        #print(css_html)
        # 得到svg地址列表，css里有三个svg地址，找到含有svgmtsi的那一个
        svg_url = re.findall('svgmtsi\[.*?background-image: url\((.*?)\);background-repeat: no-repeat;', css_html)[0]
        # print(svg_url)
        if svg_url.startswith('//'):
            svg_url = 'http:' + svg_url
        # 得到svg对应的html
        resp = requests.get(svg_url, verify=False).text
        svg_html = resp.replace("\n", "")

        # print(result_all)
        # 得到评论列表
        result_replaces = re.findall('<div class="reviews-items">(.*?)<div class="bottom-area clearfix">', result_all)[0]
        # print(str(result_replaces))
        # 把评论存进列表
        comment_list = re.findall('<li>.*?<a class="dper-photo-aside(.*?)>投诉</a>.*?</li>', result_replaces)
        for data in comment_list:
            data = str(data)
            # print(data)
            # 得到用户名的部分
            try:
                username = re.findall('data-click-name="用户名.*?data-click-title="文字".*?>(.*?)<img class=".*?" src=', data)[0]
            except:
                username = re.findall('data-click-name="用户名.*?data-click-title="文字".*?>(.*?)<div class="review-rank">', data)[0]
            # print(username)
            # 得到用户评论

            if '展开评论' in data:
                content = re.findall('<div class="review-words Hide">(.*?)<div class="less-words">', data)[0]
            else:
                try:
                    content = re.findall('<div class="review-words">(.*?)</div>.*?<div class="review-pictures">',data)[0]
                except:
                    content = re.findall('<div class="review-words">(.*?)</div>.*?<div class="misc-info clearfix">',data)[0]
            #print(content)

            from svgutil import svg2word

            if '</svgmtsi>' in content:
                content = svg2word(content, css_html, svg_html)
            else:
                content = content
            # 写入文件
            f.write(content)

        time.sleep(3)

    f.close()

if __name__ == "__main__":

    cookies = "dper=00c5f740c5a8886c10b5245d53ffd9c41e68e2d6ff69625188a4e1847f1b6173298be04fcff8af2df9c607854be52eb7acfeb25c584d5016f68cf9a7c65f2374ef82f6c37a7b506b78a249c5368cdafafea7aac49b9241ff6c33124bb08f90a3;ua=cugher"
    result_list = [
        "http://www.dianping.com/shop/8944191"
    ]
    for item in result_list:
        print("正在采集的位置是：", item)
        dzdp_spider(item, cookies)
