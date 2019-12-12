# -*-coding: utf-8 -*-
import sys
import getopt
import time
import random
import json
import six
MODELTYPE = {
    "NORMAL": 1
}


def buildHaffManTree(wordDict):
    wordDict_arr = sorted(
        wordDict.items(), key=lambda wordDict: wordDict[1], reverse=True)
    treeNode = {}
    mergeWord = []
    rootKey = ""
    i = 0
    while len(wordDict_arr) > 0:
        n0 = wordDict_arr.pop()
        if len(wordDict_arr) == 0:
            rootKey = n0[0]
            break
        else:
            n1 = wordDict_arr.pop()
            kn0 = n0[0]
            kn1 = n1[0]
            vn0 = n0[1]
            vn1 = n1[1]
            i = i + 1
            k = '_'+str(i)+"_"
            v = vn0 + vn1

            if treeNode.get(kn0):
                lChild = treeNode[kn0]
                treeNode.pop(kn0)
            else:
                lChild = {"k": kn0, "v": vn0}

            if treeNode.get(kn1):
                rChild = treeNode[kn1]
                treeNode.pop(kn1)
            else:
                rChild = {"k": kn1, "v": vn1}
            treeNode[k] = {"l": lChild, "r": rChild}
            wordDict_arr.append((k, v))
            wordDict_arr.sort(key=lambda elem: elem[1], reverse=True)
    return treeNode[rootKey]


def buildCodeBook(wordDict):
    haffManTree = buildHaffManTree(wordDict)
    encodeBook = {}
    decodeBook = {}
    nodeStack = [{"prefix": "1", "tree": haffManTree['r']},
                 {"prefix": "0", "tree": haffManTree['l']}]
    while len(nodeStack) > 0:
        node = nodeStack.pop()
        tree = node['tree']
        prefix = node['prefix']
        if tree.get('l') == None and tree.get('r') == None:
            decodeBook[prefix] = tree['k']
            encodeBook[tree['k']] = prefix
        else:
            nodeStack.append(
                {"prefix": prefix+"1", "tree": tree['r']})
            nodeStack.append(
                {"prefix": prefix+"0", "tree": tree['l']})
    return encodeBook, decodeBook


def encodeFile(filePath, model):
    try:
        fo = open(filePath, "r+", encoding='UTF-8')
        print("file open!")
        wordDict = {}
        encodeBook = {}
        decodeBook = {}
        model = 0
        encodeStr = ""
        encodeBitStr = ''
        while True:
            line = fo.readline()
            if not line:
                break
            for i in range(len(line)):
                word = line[i]
                if wordDict.get(word) == None:
                    wordDict[word] = 0
                wordDict[word] = wordDict[word] + 1

        encodeBook, decodeBook = buildCodeBook(wordDict)
        decodeBook['length'] = 0
        fo.seek(0)
        while True:
            line = fo.readline()
            if not line:
                if len(encodeBitStr) < 8:
                    for i in range(len(encodeBitStr), 8):
                        encodeBitStr = encodeBitStr + '0'
                    encodeStr = encodeStr + chr(int(encodeBitStr, 2))
                break
            for i in range(len(line)):
                word = line[i]
                encodeBitStr = encodeBitStr + encodeBook[word]
                decodeBook['length'] = decodeBook['length'] + \
                    len(encodeBook[word])
                if len(encodeBitStr) >= 8:
                    b = encodeBitStr[0:8]
                    encodeBitStr = encodeBitStr[8:]
                    encodeStr = encodeStr + chr(int(b, 2))
        fo.close()
    except Exception as e:
        print(e)
        fo.close()
    logfile = open("encode.log", mode='w', encoding='utf-8')
    logfile.write(encodeStr)
    logfile.close()
    logfile = open("decodebook.log", mode='w', encoding='utf-8')
    logfile.write(json.dumps(decodeBook))
    logfile.close()
    return encodeStr, decodeBook


def decodeStr(encodeStr, decodeBook):
    raw_str = ""
    key = ""
    encodeBitStr = ''
    length = decodeBook['length']
    for i in range(len(encodeStr)):
        encodeBitStr = encodeBitStr + '{:08b}'.format(ord(encodeStr[i]))
        j = 0
        while True:
            key = key + encodeBitStr[j]
            j = j + 1
            length = length - 1
            if decodeBook.get(key):
                raw_str = raw_str + decodeBook[key]
                key = ""
                encodeBitStr = encodeBitStr[j:]
                j = 0
            if len(encodeBitStr) <= j:
                encodeBitStr = ''
            if length == 0 or len(encodeBitStr) == 0:
                break
    logfile = open("decode.log", mode='w', encoding='utf-8')
    logfile.write(raw_str)
    logfile.close()
    return raw_str


def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])


def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])


def main(argv):
    global MODELTYPE
    try:
        options, args = getopt.getopt(argv, "m:", ["model="])
    except getopt.GetoptError:
        sys.exit()
    model = MODELTYPE["NORMAL"]
    for option, value in options:
        if option in ("-m", "--help"):
            model = int(value)

    filePath = "黄金时代-王小波.txt"  # "/var/log/v2ray/"
    encodeStr, decodeBook = encodeFile(filePath, model)
    rawStr = decodeStr(encodeStr, decodeBook)


if __name__ == '__main__':
    print('启动成功！')
    main(sys.argv[1:])
    # getIPInfoByPconline("111.224.235.72")
    print('执行完毕！')
