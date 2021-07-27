import nltk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

"""
先看一句话是否有在预定义好的动词列表里的词
有的话就继续寻找 quotation marks
然后基于这两个因素再归给最近的实体
"""

# 一. Linguistic & Semantic Analysis
# 1. Sentence splitting
file_path = 'train_text(ENG).txt'
train_text = []

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        if len(line) > 0:
            train_text.append(line)
# print('train_text - {}'.format(train_text))

# 2. POS Tagging
# assign POS tags
tokens = []
tags = []
words = []
for i in range(len(train_text)):
    token = word_tokenize(train_text[i])
    tokens.append(token)
    tag = pos_tag(token)
    tags.append(tag)
# print('tokens - {}'.format(tokens))
# print('tags - {}'.format(tags))


# 3. Entity recognition
ne_chunked_sents = [nltk.ne_chunk(tag) for tag in tags]
# print(ne_chunked_sents)

# extract all named entities
named_entities = []
for i in range(len(ne_chunked_sents)):
    named_entity = []
    for tagged_tree in ne_chunked_sents[i]:
        # extract only chunks having NE labels
        if hasattr(tagged_tree, 'label'):
            entity_name = ' '.join(c[0] for c in tagged_tree.leaves())  # get NE name
            entity_type = tagged_tree.label()  # get NE category
            named_entity.append((entity_name, entity_type))
    named_entities.append(named_entity)
    # get unique named entities
    # named_entities = list(set(named_entities))
# print('named_entities - {}'.format(named_entities))

# store named entities in a data frame
# entity_frame = pd.DataFrame(named_entities, columns=['Entity Name', 'Entity Type'])
# print(entity_frame)

# 4. Coreference resolution

# 二. Quotation Detection
# 1. 检查动词 check verbs
attributional_verbs = []
with open('Attributional Verbs(ENG)', 'r') as f:
    for line in f.readlines():
        line = line.strip()
        attributional_verbs.append(line)
# print(attributional_verbs)

# 提取实体
entities = []
# print(len(named_entities))
for i in range(len(named_entities)):
    a = []
    for j in range(len(named_entities[i])):
        a.append(named_entities[i][j][0])
    entities.append(a)
    # print(named_entities[i])
# print('entities - {}'.format(entities))

# 每个实体分成单个单词
a = []
splitted_entities = []
for i in range(len(entities)):
    a = []
    for j in range(len(entities[i])):
        if ' ' in entities[i][j]:
            splitted_entity = entities[i][j].split()
            for word in splitted_entity:
                a.append(word)
        else:
            a.append(entities[i][j])
    splitted_entities.append(a)
# splitted_entities = list(set(splitted_entities))
# print('splitted_entities - {}'.format(splitted_entities))

# 每个实体创建索引 (句子索引，在每句话中的位置)
entityidx = []
for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        for k in range(len(splitted_entities)):
            if tokens[i][j] in splitted_entities[k]:
                # print(tokens[i][j])
                # print(splitted_entities[k])
                entityidx.append((i, j))
                # entityidx.append(tokens[i][j])
entityidx = list(set(entityidx))
# print('entityidx - {}'.format(entityidx))


verbidx = []
for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        if tokens[i][j] in attributional_verbs:  # 检测动词是否在list中
            verbidx.append((i, j))
            # print(tokens[i][j])
# print('verbidx - {}'.format(verbidx))


# 2. check quotation marks
qmarkidx = []
qmarkidx_sents = []
qmarkidx_rng = []
for i in range(len(tokens)):
    flag_s = False
    flag_e = False
    j = 0
    while j < len(tokens[i]):
        if tokens[i][j] == '“':
            mark_s = j
            flag_s = True
            # print(mark_s)
            for k in range(j+1, len(tokens[i])):
                if tokens[i][k] == '”':
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
# print("qmarkidx - {}".format(qmarkidx))
# print(qmarkidx_sents)
# print('qmarkidx_rng - {}'.format(qmarkidx_rng))


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
# print('qverbidx - {}'.format(qverbidx))


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
# print('qentityidx - {}'.format(qentityidx))

# 根据index找到对应的verb
qverbs = []
for i in range(len(qverbidx)):
    qverbs.append(tokens[qverbidx[i][0]][qverbidx[i][1]])
print('qverbs - {}'.format(qverbs))


# 根据index找到对应的entity
qentities_sin = []
for i in range(len(qentityidx)):
    qentities_sin.append(tokens[qentityidx[i][0]][qentityidx[i][1]])
# print(qentities_sin)

# 根据entity找到完整的entity full name
qentities = []
for k in qentityidx:
    for i in range(len(entities)+1):
        if i == k[0]:
            for j in range(len(entities[i])):
                # print(entities[i][j])
                if tokens[k[0]][k[1]] in entities[i][j]:
                    qentities.append(entities[i][j])
print(qentities)

# 标注BIO
rst_tokens = []
rst_labels = []
quotation = []
stop_words = ['is', 'a', 'an', 'are', 'was', 'were', 'am', 'the']
f = open('pred(ENG).txt', 'w')
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
                            if (tokens[a][i] == qentities[d].split()[0]) and (tokens[a][i] not in stop_words):
                                labels.append("B-source")
                                isAppend = True
                                break
                            elif (tokens[a][i] in qentities[d]) and (tokens[a][i] != qentities[d].split()[0]) and (tokens[a][i] not in stop_words):
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

    print(len(pred_dict['tokens']))
    print(len(pred_dict['labels']))

    # 写入文件
    f.write(str(pred_dict).replace("'", "\""))
    f.write('\n')

f.close()

# 三. Attribution & Collapsing
# 四. Indexing
