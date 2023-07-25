import fileinput
import zhconv
import re
import math


def changeEnglishSubtitles(input_url):
    remove_words = ['Özgür: ', 'Burcu: ']
    changeSymbol = ['...']
    for line in fileinput.input(input_url, inplace=1, encoding='UTF-8'):
        for remove_word in remove_words:
            line = line.replace(remove_word, "")
        for symbol in changeSymbol:
            line = line.replace(symbol, '. ')
        print(line, end='')
    format_englishsrt(input_url)
    return input_url


def changeChineseSubtitles(input_url):
    remove_words = ['Özgür：', 'Burcu：', '厄兹古尔：', '十二星座：', '十二生肖：'
                    , '标志：', '奥兹古尔：', '月光：', '征兆：', '布尔库：'
                    , '招牌：', '符号：', 'Zodiac：', '布尔库：'
                    , '星座：', '签名：', '生肖：', '签：']
    changeSymbol = ['...', '……']
    for line in fileinput.input(input_url, inplace=1, encoding='UTF-8'):
        for remove_word in remove_words:
            line = line.replace(remove_word, "")
        for symbol in changeSymbol:
            line = line.replace(symbol, '. ')
        print(line, end='')
    changeWords(input_url)
    return input_url


def changeWords(input_url):
    awords = ['标志', '月光', '免费', '十二生肖', '生肖', '征兆', '星座', '签名','Burcu']
    bwords = ['奥兹古尔', 'Ozgur', 'Özgür']
    cwords = ['……', '。 ', '。']  # 空格代替标点符号
    for line in fileinput.input(input_url, inplace=1, encoding='UTF-8'):
        for a in awords:
            line = line.replace(a, "布尔库")
        for b in bwords:
            line = line.replace(b, "厄兹古尔")
        for c in cwords:
            line = line.replace(c, ". ")
        print(line, end='')


def changeSimple(input_url):
    for line in fileinput.input(input_url, inplace=1, encoding='UTF-8'):
        line = zhconv.convert(line, 'zh-cn')
        print(line, end="")


def open_file(filename):
    filehandle_Chinese = open(filename, encoding='UTF-8')
    mystr_Chinese = filehandle_Chinese.readlines()
    filehandle_Chinese.close()
    return mystr_Chinese


def write_list_to_txt(file_name, data_list):  # 将列表按行写入到TXT文件中
    handle = open(file_name, 'w', encoding='utf-8')
    for element in data_list:
        handle.write(str(element))
        # handle.write('\n')
    handle.close()


def merge_subtitle(str_list_Chinese, str_list_English):
    new_str_list = str_list_Chinese  # 直接就让和和中文字幕相同，复制一份，然后间轴轴不变，只修具具体的字幕内容
    for index, element in enumerate(str_list_Chinese):
        if index % 4 == 0:
            str_Chinese = str_list_Chinese[index + 2]
            str_English = str_list_English[index + 2]
            # print(str_Chinese)
            # print(str_English)
            new_str = str_Chinese + str_English
            # print(new_str)
            new_str_list[index + 2] = new_str
    return new_str_list


def format_englishsrt(inputurl):
    with open(inputurl, "r", encoding="utf-8") as f:
        english_srt = f.readlines()
    merged_srt = []
    line_count = len(english_srt)
    i = 0
    while i < line_count:
        line = english_srt[i].strip()
        if line.isdigit():
            # 行号
            merged_srt.append(line)
            i += 1
            continue
        if ' --> ' in line:
            # 时间
            merged_srt.append(line)
            i += 1
            continue
        if line != "":
            # 字幕内容
            merged_line = line
            next_line = english_srt[i + 1].strip()
            if next_line != "":
                merged_line += " " + next_line
                i += 1
            merged_srt.append(merged_line)

            merged_srt.append("")  # 添加空白行

        i += 1

    merged_srt = "\n".join(merged_srt)
    with open(inputurl, "w", encoding="utf-8") as f:
        f.write(merged_srt)
    f.close()


def merge_caption(chinese_file, english_file):
    str_list_Chinese = open_file(chinese_file)
    str_list_English = open_file(english_file)
    new_str_list = merge_subtitle(str_list_Chinese, str_list_English)
    filename = chinese_file.rsplit("/", 1)[0] + '/中英文字幕.srt'
    write_list_to_txt(filename, new_str_list)
    print("合并字幕成功")


# 重命名
def remove_symbol(word):
    word = re.sub('([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u007a])', '', word)
    return word


# 文件大小单位转换
def pybyte(size, dot=2):
    size = float(size)
    # 位 比特 bit
    if 0 <= size < 1:
        human_size = str(round(size / 0.125, dot)) + 'b'
    # 字节 字节 Byte
    elif 1 <= size < 1024:
        human_size = str(round(size, dot)) + 'B'
    # 千字节 千字节 Kilo Byte
    elif math.pow(1024, 1) <= size < math.pow(1024, 2):
        human_size = str(round(size / math.pow(1024, 1), dot)) + 'KB'
    # 兆字节 兆 Mega Byte
    elif math.pow(1024, 2) <= size < math.pow(1024, 3):
        human_size = str(round(size / math.pow(1024, 2), dot)) + 'MB'
    # 吉字节 吉 Giga Byte
    elif math.pow(1024, 3) <= size < math.pow(1024, 4):
        human_size = str(round(size / math.pow(1024, 3), dot)) + 'GB'
    # 太字节 太 Tera Byte
    elif math.pow(1024, 4) <= size < math.pow(1024, 5):
        human_size = str(round(size / math.pow(1024, 4), dot)) + 'TB'
    # 拍字节 拍 Peta Byte
    elif math.pow(1024, 5) <= size < math.pow(1024, 6):
        human_size = str(round(size / math.pow(1024, 5), dot)) + 'PB'
    # 艾字节 艾 Exa Byte
    elif math.pow(1024, 6) <= size < math.pow(1024, 7):
        human_size = str(round(size / math.pow(1024, 6), dot)) + 'EB'
    # 泽它字节 泽 Zetta Byte
    elif math.pow(1024, 7) <= size < math.pow(1024, 8):
        human_size = str(round(size / math.pow(1024, 7), dot)) + 'ZB'
    # 尧它字节 尧 Yotta Byte
    elif math.pow(1024, 8) <= size < math.pow(1024, 9):
        human_size = str(round(size / math.pow(1024, 8), dot)) + 'YB'
    # 千亿亿亿字节 Bront Byte
    elif math.pow(1024, 9) <= size < math.pow(1024, 10):
        human_size = str(round(size / math.pow(1024, 9), dot)) + 'BB'
    # 百万亿亿亿字节 Dogga Byte
    elif math.pow(1024, 10) <= size < math.pow(1024, 11):
        human_size = str(round(size / math.pow(1024, 10), dot)) + 'NB'
    # 十亿亿亿亿字节 Dogga Byte
    elif math.pow(1024, 11) <= size < math.pow(1024, 12):
        human_size = str(round(size / math.pow(1024, 11), dot)) + 'DB'
    # 万亿亿亿亿字节 Corydon Byte
    elif math.pow(1024, 12) <= size:
        human_size = str(round(size / math.pow(1024, 12), dot)) + 'CB'
    # 负数
    else:
        raise ValueError('{}() takes number than or equal to 0, but less than 0 given.'.format(
            pybyte.__name__))
    return human_size


def get_user_choice():
    while True:
        print("选择要使用的功能：")
        print("0. 1和2的组合")
        print("1. 英文字幕加工")
        print("2. 转换字幕")
        print("3. 繁体转简体")
        print("4. 合并中英文字幕")

        choice = input("输入选项编号：")

        if choice.isdigit():
            choice = int(choice)

            if choice == 0:
                input_url = input("输入英文字幕文件：")
                changeEnglishSubtitles(input_url)
                mix_url = input("输入中英文字幕文件：")
                changeWords(mix_url)
                break

            elif choice == 1:
                input_url = input("输入字幕文件：")
                changeEnglishSubtitles(input_url)
                break
            elif choice == 2:
                input_url = input("输入字幕文件：")
                changeWords(input_url)
                break
            elif choice == 3:
                simplefile = input("输入要转换简体字幕文件：")
                changeSimple(simplefile)
                break

            elif choice == 4:
                chinesefile = input("输入中文字幕文件：")
                englishfile = input("输入英文字幕文件：")
                changeWords(chinesefile)
                str_list_Chinese = open_file(chinesefile)
                str_list_English = open_file(englishfile)
                new_str_list = merge_subtitle(str_list_Chinese, str_list_English)
                filename = chinesefile.rsplit("\\", 1)[0] + '/中英文字幕.srt'
                write_list_to_txt(filename, new_str_list)
                break

        print("无效的选项，请重新输入。")


if __name__ == '__main__':
    # changeChineseSubtitles(r'D:\油管资料\露营\AtikAilesi\2023-07-07_DEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP\zh-HansDEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP (zh-Hans).srt')
    # get_user_choice()
    # englishsrt(r'D:\油管资料\露营\AtikAilesi\2023-07-07_DEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP\enDEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP (en).srt')
    merge_caption(
        r"D:/油管资料/露营/AtikAilesi/2023-07-07_DEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP/zh-HansDEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP (zh-Hans).srt",
        r"D:/油管资料/露营/AtikAilesi/2023-07-07_DEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP/enDEVASAPENCEREL2BALKONLUADIRIMIZLAKAMP (en).srt")
