def cell_value(sheet, raw, col):
    cell = sheet[raw][col]
    coord = cell.coordinate
    if not isinstance(cell, MergedCell):
        return cell.value

    # "Oh no, the cell is merged!"
    for range in sheet.merged_cells.ranges:
        if coord in range:
            return range.start_cell.value

    raise AssertionError('Merged cell is not in any merge range!')





def parse_kurs(col_begin):
    book = openpyxl.open("xl.xlsx")  # открытие excel файла
    sheet = book.active  # делаем лист активным

    corr = 0

    if cell_value(sheet, 3, col_begin) == 'Дни недели':
        corr += 1
    if cell_value(sheet, 3, col_begin + 1) == 'Часы звонков':
        corr += 1

    col = corr + col_begin

    # проходим все ячейки с расписанием и записываем данные в списки
    while (cell_value(sheet, 4, col)) is not None:
        row = 5
        group_para = list()
        while row < sheet.max_row:
            if cell_value(sheet, row, 1) is not None:
                print(cell_value(sheet, row, 1))
                para = list()
                para.append(cell_value(sheet, row, 0))
                para.append(cell_value(sheet, row, 1))
                para.append(cell_value(sheet, 3, col))
                para.append(cell_value(sheet, 4, col))
                try:
                    para.extend(cut_teach(cell_value(sheet, row, col)))
                except Exception as e:
                    para.extend([cell_value(sheet, row, col), None, None])

                try:
                    para.extend(cut_teach(cell_value(sheet, row + 1, col)))
                except Exception as e:
                    para.extend([cell_value(sheet, row + 1, col), None, None])

                para[0] = days_in_number.get(para[0])

                split_spec = para[2].split()
                para[2] = ''
                for i in range(1, len(split_spec)):
                    if len(split_spec[i]) > 1:
                        para[2] += split_spec[i][0].upper()

                # for i in range(1, len(para[3])):
                #     if para[3][len(para[3]) - i].isalpha() and para[3][len(para[3]) - i] != '.':
                #         para[3] = para[3][len(para[3]) - i + 2:]
                #         break

                if para[3] != '':
                    if para[3].split()[0] == "Группа" and len(para[3].split()) > 1:
                        para[3] = para[3].split()[1:]
                        para[3] = ''.join(para[3])

                if para[3] == '':
                    para[3] = cell_value(sheet, 4, col)
                    for i in range(len(para[3])):
                        if para[3].isspace():
                            para[3] = para[3][:i]
                            break

                if len(para[3]) > 10:
                    para[3] = (para[3].split())[0]
                print(para[3])
                group_para.append(para)

                row += 2
            else:
                row += 1

        create_table_rasp(cell_value(sheet, 2, col))
        for par in group_para:
            add_rasp(par, cell_value(sheet, 2, col))

        col += 1
        if col == sheet.max_column:
            break


async def parse_xl():
    book = openpyxl.open("xl.xlsx")
    sheet = book.active
    print(sheet.max_row)
    print(sheet.max_column)
    col_begin = 0

    parse_kurs(col_begin)
    for j in range(sheet.max_column):
        if (cell_value(sheet, 4, j)) is None:
            if cell_value(sheet, 4, j + 1) is None and cell_value(sheet, 4, j + 2) is None:
                return 0

            j += 1
            col_begin = j
            parse_kurs(col_begin)


def parse_spo():
    book = openpyxl.open("spo.xlsx")
    print("открыто")
    sheet = book.active  # делаем лист активным

    col = 2

    # проходим все ячейки с расписанием и записываем данные в списки
    while (cell_value(sheet, 3, col)) is not None:
        row = 5
        group_para = list()
        while cell_value(sheet, row, 1) is not None or cell_value(sheet, row + 1, 1) is not None or cell_value(sheet,
                                                                                                               row + 2,
                                                                                                               1) or cell_value(
                sheet, row + 3, 1) or cell_value(sheet, row + 4, 1):
            if cell_value(sheet, row, 1) is not None:
                print(cell_value(sheet, row, 1))
                para = list()
                para.append(cell_value(sheet, row, 0))
                para.append(cell_value(sheet, row, 1))
                para.append(cell_value(sheet, 2, col))
                para.append(cell_value(sheet, 3, col))
                para.extend(cut_teach(cell_value(sheet, row, col)))

                if cell_value(sheet, row, 1) == cell_value(sheet, row + 1, 1):
                    para.extend(cut_teach(cell_value(sheet, row + 1, col)))
                    step = 2
                else:
                    para.extend(cut_teach(cell_value(sheet, row, col)))
                    step = 1

                if para[4] is not None and len(para[4]) < 2:
                    para[4] = None

                if para[7] is not None and len(para[7]) < 2:
                    para[7] = None

                para[0] = "".join(para[0].split('\n'))
                para[0] = "".join(para[0].split())
                para[0] = days_in_number.get(para[0].capitalize())

                split_spec = para[3].split()
                para[3] = ''
                for word in split_spec:
                    if word.strip(')') == 'чел' or word.strip(')') == "после" or word.strip(')') == "курс":
                        pass

                    elif word.strip('(').strip(')') == '9' or word.strip('(').strip(')') == '11':
                        para[3] += '(' + word.strip('(').strip(')') + ')'

                    elif '(' in word or ')' in word:
                        pass

                    else:
                        if len(word) > 1:
                            para[3] += word[0].upper()
                        else:
                            para[3] += word

                para[3] = para[2] + " " + para[3]
                para[2] = None

                # if para[3] != '':
                #     if para[3].split()[0] == "Группа" and len(para[3].split()) > 1:
                #         para[3] = para[3].split()[1:]
                #         para[3] = ''.join(para[3])
                #
                # if para[3] == '':
                #     para[3] = cell_value(sheet, 4, col)
                #     for i in range(len(para[3])):
                #         if para[3].isspace():
                #             para[3] = para[3][:i]
                #             break

                # if len(para[3]) > 10:
                #     para[3] = (para[3].split())[0]
                # print(para[3])

                group_para.append(para)

                row += step
            else:
                row += 1

        create_table_rasp("СПО")

        for par in group_para:
            add_rasp(par, "СПО")

        col += 1
