import jieba
import jieba.posseg as pseg  # 词性标注

# 一. Linguistic & Semantic Analysis

# 1. Sentence splitting
file_path = 'train_text1.txt'
train_text = []

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        if len(line) > 0:
            train_text.append(line)
print('train_text - {}'.format(train_text))

# 2. POS Tagging
tokens = []
for sentence in train_text:
    a = []
    for char in sentence:
        a.append(char)
    tokens.append(a)
tokens = list(tokens)
print(type(tokens))
print('tokens - {}'.format(tokens))
# print(len(tokens))

# assign POS tags
tags = []
for i in range(len(train_text)):
    a = []
    tmp = pseg.cut(train_text[i])
    for t in tmp:
        a.append((t.word, t.flag))
    tags.append(a)
print('tags - {}'.format(tags))


splitted_text = []
for i in range(len(tags)):
    a = []
    for j in range(len(tags[i])):
        a.append(tags[i][j][0])
    splitted_text.append(a)
print('splitted_text - {}'.format(splitted_text))


# 3. Entity recognition
# extract all named entities
entities = []
for i in range(len(tags)):
    for j in range(len(tags[i])):
        if tags[i][j][1] == 'nr':
            entities.append(tags[i][j][0])
print('entities - {}'.format(entities))


# 二. Quotation Detection
# 1. check verbs
attributional_verbs = []
with open('Attributional Verbs(CHN)', 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        attributional_verbs.append(line)
print('attributional_verbs - {}'.format(attributional_verbs))


entityidx = []
for i in range(len(splitted_text)):
    for j in range(len(splitted_text[i])):
        if splitted_text[i][j] in entities:
            # print(tokens[i][j])
            # print(splitted_entities[k])
            entityidx.append((i, j))
            # entityidx.append(tokens[i][j])
entityidx = list(set(entityidx))
print('entityidx - {}'.format(entityidx))


verbidx = []
for i in range(len(splitted_text)):
    for j in range(len(splitted_text[i])):
        if splitted_text[i][j] in attributional_verbs:  # 检测动词是否在list中
            verbidx.append((i, j))
            # print(tokens[i][j])
print('verbidx - {}'.format(verbidx))


# 2. check quotation marks
qmarkidx = []
qmarkidx_sents = []
qmarkidx_rng = []
for i in range(len(splitted_text)):
    flag_s = False
    flag_e = False
    j = 0
    while j < len(splitted_text[i]):
        if splitted_text[i][j] == '「':
            mark_s = j
            flag_s = True
            # print(mark_s)
            for k in range(j+1, len(splitted_text[i])):
                if splitted_text[i][k] == '」':
                    mark_e = k
                    flag_e = True
                    # print(mark_e)
                    break
        j += 1
        if flag_s and flag_e:
            qmarkidx.append((i, (mark_s+mark_e)/2))
            qmarkidx_sents.append(i)
            qmarkidx_rng.append((i, mark_s, mark_e))
            flag_s = False
            flag_e = False
            j = k + 1
        # print(j)
        # if '“' in tokens[i] and '”' in tokens[i]:
        #     print(tokens[i])
        #     break
# qmarkidx = list(set(qmarkidx))
qmarkidx_sents = list(set(qmarkidx_sents))
print('qmarkidx - {}'.format(qmarkidx))
print('qmarkidx_sents - {}'.format(qmarkidx_sents))
print('qmarkidx_rng - {}'.format(qmarkidx_rng))


# 3. determine quotation candidates
# 找到距离quotation最近的verb
qverbidx = []
for i in range(len(qmarkidx)):
    j = verbidx[0][0]
    min_dist = 10000
    qverb = -1
    while j < len(verbidx):
        if verbidx[j][0] == qmarkidx[i][0]:
            tmp = min(abs(qmarkidx[i][1] - verbidx[j][1]), min_dist)
            # print(qmarkidx[i][1])
            # print(verbidx[j][1])
            if tmp != min_dist:
                min_dist = tmp
                qverb = j
        j += 1
    if qverb >= 0:
        # print(qverb, min_dist)
        qverbidx.append(verbidx[qverb])

qverbidx = list(set(qverbidx))
print('qverbidx - {}'.format(qverbidx))


# 找到离verb最近的entity
qentityidx = []
for i in range(len(qverbidx)):
    j = entityidx[0][0]
    min_dist = 10000
    qentity = -1
    while j < len(entityidx):
        if entityidx[j][0] == qverbidx[i][0]:
            tmp = min(abs(qverbidx[i][1] - entityidx[j][1]), min_dist)
            # print(qverbidx[i][1])
            # print(entityidx[j][1])
            if tmp != min_dist:
                min_dist = tmp
                qentity = j
        j += 1
    if qentity >= 0:
        # print(qentity, min_dist)
        qentityidx.append(entityidx[qentity])

qentityidx = list(set(qentityidx))
print('qentityidx - {}'.format(qentityidx))


# 根据index找到对应的entity
qentities = []
for i in range(len(qentityidx)):
    qentities.append(splitted_text[qentityidx[i][0]][qentityidx[i][1]])
print('qentities - {}'.format(qentities))


# 根据index找到对应的verb
qverbs = []
for i in range(len(qverbidx)):
    qverbs.append(splitted_text[qverbidx[i][0]][qverbidx[i][1]])
print('qverbs - {}'.format(qverbs))


# 根据entity找到完整的entity full name
# qentities = []
# for k in qentityidx:
#     for i in range(len(entities)+1):
#         if i == k[0]:
#             for j in range(len(entities[i])):
#                 # print(entities[i][j])
#                 if splitted_text[k[0]][k[1]] in entities[i][j]:
#                     qentities.append(entities[i][j])
# print('qentities - {}'.format(qentities))

# 标注BIO
rst_tokens = []
rst_labels = []
quotation = []
f = open('pred(CHN).txt', 'w')
for a in range(len(tokens)):
    pred_dict = {}
    quotation = []
    labels = []
    pred_dict["tokens"] = tokens[a]
    if a not in qmarkidx_sents:
        for b in range(len(tokens[a])):
            labels.append("O")
        pred_dict["labels"] = labels
    else:
        for j in range(len(qmarkidx_rng)):
            if a == qmarkidx_rng[j][0]:
                quote_s = qmarkidx_rng[j][1]
                quote_e = qmarkidx_rng[j][2]
                for i in range(len(tokens[a])):
                    if i <= quote_s or i >= quote_e:
                        isAppend = False
                        for d in range(len(qentities)):
                            if tokens[a][i] == qentities[d][0]:
                                labels.append("B-source")
                                isAppend = True
                                break
                            elif (tokens[a][i] in qentities[d]) and (tokens[a][i] != qentities[d][0]):
                                labels.append("I-source")
                                # print(tokens[a][i], qentities[d].split()[0])
                                isAppend = True
                                break
                            if isAppend:
                                break
                        if not isAppend and tokens[a][i] in qverbs:
                            labels.append("B-cue")
                            isAppend = True
                        if not isAppend:
                            labels.append("O")
                    elif i == quote_s + 1:
                        labels.append("B-content")
                        is1st_con = False
                    else:
                        labels.append("I-content")
            pred_dict["labels"] = labels

    # print(len(pred_dict['tokens']))
    # print(len(pred_dict['labels']))

    # 写入文件
    f.write(str(pred_dict).replace("'", "\""))
    f.write('\n')

f.close()

# 三. Attribution & Collapsing


# 四. Indexing

