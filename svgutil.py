#标签转汉字
import re

def convert_unicode(text):
    text = text.replace('&#','')
    text = [i for i in text.split(';') if i]
    text = [hex(int(i)) for i in text]
    text = [i.replace('0x','') for i in text]
    string = ' '
    flag = '\\u'
    for i in text:
        string += flag+format(i,'0>4s')
    return string.encode('utf-8').decode('unicode-escape')


def svg2word(content, css_html, svg_html):
    # 得到所有加密的文字组成列表
    cssls = re.findall('<svgmtsi class="(.*?)"></svgmtsi>', content)
    # print(cssls)
    replace_content_list = []
    # 开始解析每个标签应该对应的汉字
    for charcb in cssls:
        # css 文件中取出 需要替换字符的 横坐标 和 纵坐标
        #print(charcb)
        # 提取横纵坐标
        css = re.search(charcb + "\{background:-(\d+)\.0px -(\d+)\.0px;\}", css_html).groups()
        x_px = css[0]  # 横坐标
        y_px = css[1]  # 纵坐标
        # 计算出来 需要 替换汉字的位置
        #print("x_px",x_px)
        #print("y_px",y_px)

        x_num = int(x_px) / 14

        # 取出 每一行的汉字 结构 如下所示
        # 在svg html里得到y坐标组成列表
        text_y_list = re.findall('<text x="0" y="(.*?)">.*?</text>', svg_html)
        # 在svg html里得到汉字的行，组成列表
        text_list = re.findall('<text x="0" y=".*?">(.*?)</text>', svg_html)

        # 找到含有这个汉字的行，如下
        y_num_list = []
        # 在text_y_list里，y的坐标是由小到大排列的，找到第一个大于y_px的行标
        for i in text_y_list:
            if int(i) > int(y_px):
                y_num_list.append(i)
        y_num = text_y_list.index(y_num_list[0])

        #替换的字就是第y_num行的第x_num个汉字
        replace_chinese = text_list[int(y_num)][int(x_num)]
        #print(replace_chinese)
        #组成列表
        replace_content_list.append(replace_chinese)
    #print(replace_content_list)
    # 把原始内容分割开，得到的每个元素都以<svgmtsi class="*">的形式结尾，最后一个元素没有svgmtsi，需要最后补上
    content_list = content.split('</svgmtsi>')
    #print(content_list)
    # return_content是返回的列表
    return_content = []
    for ii in content_list:
        #print(ii)
        #print(content_list.index(ii))
        # content_list和replace_content_list是一一对应的，一一替换后加到return_content里
        if '<svgmtsi' in ii:
           word = re.sub(r'<svgmtsi class=".*?">', '', ii)
           return_content.append(word + replace_content_list[content_list.index(ii)])
    # 补上最后一个元素
    if len(content_list) > len(replace_content_list):
        return_content.append(content_list[len(content_list)-1])
    #print(return_content)
    return_content_str = ''.join(return_content)
    return_content_str = return_content_str + '\n###next_review###\n'
    # print(return_content_str)

    return return_content_str