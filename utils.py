from collections import Counter


def calculate_similarity(object1_tags, object2_tags):
    counter1 = Counter(object1_tags)
    counter2 = Counter(object2_tags)

    intersection = sum((counter1 & counter2).values())
    union = sum((counter1 | counter2).values())

    similarity = intersection / union
    return similarity


def get_simmilarity_marix(visits, recommended):
    matrix = []
    for visit in visits:
        row = []
        for rec in recommended:
            row.append([rec.get('id'), calculate_similarity(visit.get('tags'), rec.get('tags')), rec.get('name')])
        matrix.append([visit.get('category_id'), row, visit.get('name')])
    return matrix


def get_most_similar(matrix):
    result = []
    for row in matrix:
        max = 0.5
        for col in row[1]:
            if col[1] > max:
                # max = col[1]
                result.append([row[0], col[0], max, row[2], col[2]])
    return result


def sort_by_simmilarity_value(matrix):
    return matrix.sort(key=lambda x: x[2], reverse=True)


def summarize_coef(matrix):
    result_dict = {}
    while len(matrix):
        row = matrix.pop(0)
        if row[1] not in result_dict:
            result_dict[row[1]] = row[2]
        else:
            result_dict[row[1]] += row[2]
    return [(k, v) for k, v in result_dict.items()]


def levenshtein_distance(str1, str2):
    m = len(str1)
    n = len(str2)

    d = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j] + 1,
                              d[i][j - 1] + 1,
                              d[i - 1][j - 1] + 1 
                             )

            if i > 1 and j > 1 and str1[i - 1] == str2[j - 2] and str1[i - 2] == str2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)

    return d[m][n]


def dismiss_mutually_exclusive(simmilar_categories):
    exlude_online = []
    result = []
    for category in simmilar_categories:
        if category[2] >= 0.5:
            if category[1] in exlude_online:
                continue

            distance = levenshtein_distance(category[3].replace("ОНЛАЙН", "")
                                            .strip(' '),
                                            category[4].replace("ОНЛАЙН", "")
                                            .strip(' '))
            if distance > 0:
                result.append(category)
                continue

            exlude_online.append(category[1])
            if category[0] not in exlude_online:
                exlude_online.append(category[0])
        else:
            if category[1] not in exlude_online:
                result.append(category)
    return result