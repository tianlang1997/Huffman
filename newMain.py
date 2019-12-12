# -*-coding: utf-8 -*-
import sys
import time
import json
import six
MODELTYPE = {
    "NORMAL": 1
}


def buildHuffManTree(wordDict):
    wordDict_arr = sorted(
        wordDict.items(), key=lambda wordDict: wordDict[1], reverse=True)
    treeNode = {}
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
            k = '_'+str(i)+"_"
            i = i + 1
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
    huffManTree = buildHuffManTree(wordDict)

    logfile = open("huffManTree.log", mode='w')
    logfile.write(json.dumps(huffManTree))
    logfile.close()

    encodeBook = {}
    nodeStack = [{"prefix": "1", "tree": huffManTree['r']},
                 {"prefix": "0", "tree": huffManTree['l']}]
    while len(nodeStack) > 0:
        node = nodeStack.pop()
        tree = node['tree']
        prefix = node['prefix']
        if tree.get('k') != None:
            encodeBook[tree['k']] = prefix
        else:
            if tree.get('r'):
                nodeStack.append({"prefix": prefix+"1", "tree": tree['r']})
            if tree.get('l'):
                nodeStack.append({"prefix": prefix+"0", "tree": tree['l']})
    return encodeBook, huffManTree


def encodeFile(inputFile, outputFile):
    fi = open(inputFile, 'rb')
    filedata = fi.read()
    filesize = fi.tell()
    print("file open!")
    wordDict = {}
    encodeStr = ""
    # 统计字节频率
    for x in range(filesize):
        tem = filedata[x]
        if tem in wordDict.keys():
            wordDict[tem] = wordDict[tem] + 1
        else:
            wordDict[tem] = 1

    encodeBook, huffManTree = buildCodeBook(wordDict)
    fo = open(outputFile, mode='wb')
    bytesArr = []  # 字节缓存
    for x in range(filesize):
        word = filedata[x]
        encodeStr = encodeStr + encodeBook[word]
        out = 0
        while len(encodeStr) > 8:
            for x in range(8):
                out = out << 1
                if encodeStr[x] == '1':
                    out = out | 1
            encodeStr = encodeStr[8:]
            bytesArr.append(out)
            out = 0
        if len(bytesArr) == 2048:
            fo.write(bytes(bytesArr))
            bytesArr = []
    # 处理剩下来的不满8位的code 剩下bit个数（小于8个）+ 剩下的bit(不够8位后面用0补全)
    bytesArr.append(len(encodeStr))
    out = 0
    for i in range(len(encodeStr)):
        out = out << 1
        if encodeStr[i] == '1':
            out = out | 1
    for i in range(8-len(encodeStr)):
        out = out << 1
    bytesArr.append(out)
    fo.write(bytes(bytesArr))
    fo.close()
    fi.close()
    return huffManTree


def decodeFile(filePath, outFile, huffManTree):
    fi = open(filePath, 'rb')
    filedata = fi.read()
    filesize = fi.tell()
    fo = open(outFile, mode='wb')
    currentNode = huffManTree
    bytesArr = []
    # 内容长度  文档结构：内容+不足8位个数+不足8位
    contentLen = filesize-2
    for x in range(contentLen):
        c = filedata[x]
        for i in range(8):
            if c & 128:
                currentNode = currentNode['r']
            else:
                currentNode = currentNode['l']
            if currentNode.get('k') != None:
                bytesArr.append(currentNode['k'])
                currentNode = huffManTree
            c = c << 1
        if len(bytesArr) == 2048:
            fo.write(bytes(bytesArr))
            bytesArr = []
    c = filedata[-1]
    restLen = filedata[-2]
    for x in range(restLen):
        if c & 128:
            currentNode = currentNode['r']
        else:
            currentNode = currentNode['l']
        c = c << 1
    bytesArr.append(currentNode['k'])
    fo.write(bytes(bytesArr))
    fo.close()
    fi.close()
    return


def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])


def decode(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])


def main(argv):
    #  "test.log" #  # "img.png" #  # "黄金时代-王小波.txt" "绿妖水怪.txt""bytes.txt"
    inputFilePath = "img.png"
    outputFilePath = 'img.huff'
    huffManTree = encodeFile(inputFilePath, outputFilePath)
    decodeFile(outputFilePath, "imgd.png", huffManTree)

if __name__ == '__main__':
    print('启动成功！')
    main(sys.argv[1:])
    print('执行完毕！')
