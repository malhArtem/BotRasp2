from config import day_chisl, sokr


def normalize(target_str):
    if target_str is None:
        target_str = ''
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in sokr.items():
        # меняем все target_str на подставляемое
        target_str = target_str.strip()
        target_str = (" ".join(target_str.split())).replace(i, j)
    return target_str


def cut_teach(s: str):
    split_s = list()
    if s is not None:
        list_s = s.split()
        j = len(list_s)
        for i in range(len(list_s)):
            # print(list_s[i])
            if len(list_s[i]) == 4:
                if list_s[i][0].isalpha() and list_s[i][1] == '.' and list_s[i][2].isalpha() and list_s[i][3] == '.':
                    j = i
                    break
            elif len(list_s) >= i + 1 and len(list_s[i]) == 2 and len(list_s[i + 1]) == 2:
                if list_s[i][0].istitle() and list_s[i][1] == '.' and list_s[i + 1][0].istitle() and list_s[i][
                    1] == '.':
                    j = i
                    list_s[i] += list_s[i + 1]
                    list_s.pop(i + 1)
                    break

        if j == len(list_s):
            split_s.append(" ".join(list_s))
            split_s.append(None)
            split_s.append(None)
        else:
            split_s.append(" ".join(list_s[:j - 1]))
            split_s.append(" ".join(list_s[j - 1: j + 1]))
            split_s.append(" ".join(list_s[j + 1:]))

        if split_s[1] is None and split_s[0] is not None:
            for i in range(len(split_s[0]) - 3):
                if (split_s[0][i].isalpha() and split_s[0][i].istitle()) and split_s[0][i + 1] == '.' \
                        and (split_s[0][i + 2].isalpha() and split_s[0][i + 2].istitle()) \
                        and (split_s[0][i + 3] == '.' or split_s[0][i + 3].isspace()):
                    j = i

                    spaces = 0
                    while spaces != 2 and j != 0:
                        if split_s[0][j].isspace():
                            j += -1
                            spaces += 1
                        else:
                            j += -1

                    split_s[1] = split_s[0][j + 1: i + 4].strip()
                    split_s[2] = split_s[0][i + 4:].strip()
                    split_s[0] = split_s[0][:j + 1].strip()
                    if split_s[1][-1] != '.':
                        split_s[1] = split_s[1] + '.'

                    break
        if split_s[1] is not None:
            for i in range(len(split_s[1])):
                if split_s[1][i:].istitle():
                    split_s[0] = split_s[0] + split_s[1][:i]
                    split_s[1] = split_s[1][i:]
                    break
    else:
        split_s.append(None)
        split_s.append(None)
        split_s.append(None)

    if split_s[0] is not None:
        split_s[0] = split_s[0].strip(',')
    if split_s[1] is not None:
        split_s[1] = split_s[1].strip(',')
    if split_s[2] is not None:
        split_s[2] = split_s[2].strip(',')
    return split_s


def chisl_or_znam(now):
    delta = now - day_chisl
    if (delta.days // 7) % 2 == 0:
        return 4
    else:
        return 7