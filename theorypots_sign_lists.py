def eliminate_one_list_from_another(list1, list2):
    ret = list()
    for el in list1:
        found = False
        for e in list2:
            if e == el:
                found = True
                break
        if not found:
            ret.append(el)
    return ret

def dedup(some_list):
    ret = list()
    for el in some_list:
        found = False
        for o in ret:
            if el == o:
                found = True
                break
        if not found:
            ret.append(el)
    return ret


def combine_two_signs_list(first_sign, second_sign):
    both = list()
    for e1 in first_sign:
        for e2 in second_sign:
            if e1 == e2: both.append(e1)

    first = eliminate_one_list_from_another(first_sign, both)
    second = eliminate_one_list_from_another(second_sign, both)
    both = dedup(both)

    return first, second, both

def combine_signs_list(sign_dict, first_sign, second_sign, target_sign):
    if first_sign not in sign_dict or second_sign not in sign_dict: return
    first, second, both = combine_two_signs_list(sign_dict[first_sign], sign_dict[second_sign])
    if len(both) == 0: return
    sign_dict[first_sign], sign_dict[second_sign] = first, second
    if target_sign not in sign_dict:
        sign_dict[target_sign] = list()
    for el in both:
        sign_dict[target_sign].append(el)

def check_sign_lists(sign_dict, first_sign, second_sign):
    if first_sign not in sign_dict or second_sign not in sign_dict: return True
    for el1 in sign_dict[first_sign]:
        for el2 in sign_dict[second_sign]:
            if el1 == el2:
                return False
    return True
