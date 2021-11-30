import numpy as np
import pandas as pd

def slot_and_intent_classified_request(req):
    """
    slot_and_intent_classified_request function takes already classified request and split it to it's components.
    :param req: classified request
    :return: leading slots (B-), 
             all slots, 
             sent: [[token, slot], [token, slot], ... , [token_slot]]
    
    """
    intent = req.split('<=>')[1].strip()
    sent = req.split('<=>')[0].strip().split()

    slots_b = []

    for pair in sent:
        token = pair.split(':')[0]
        slot = pair.split(':')[1]

        if slot.split('-')[0] == 'B':
            slots_b.append(slot)

    slots_b = list(set(slots_b))
    all_slots = [item.split(':')[-1] for item in sent]
    sent = [[pair.split(':')[0].lower(), pair.split(':')[1]] for pair in sent]
    
    return slots_b, all_slots, sent

def full_token_and_slot_constructor(slots, slots_b, all_slots, sent):
    """
    full_token_and_slot_constructor function takes slots and returns every leading slots separately
    :param slots: өгүүлбэрээс product-д хамаарах slot-ууд хайх уу, action эсвэл branch-д хамаарах slot-уудыг хайх уу гэдгээ өгнө. (e.g product_slots)
    :param slots_b: өгүүлбэрт байгаа "B-" ээр эхэлсэн slot-ууд
    :param all_slots: өгүүлбэрт байгаа бүх slot
    :param sent: user input request
    :return: хэрвээ өгүүлбэр slots дотор байгаа slot-уудыг агуулсан байвал өгүүлбэрийн бүх "B-" эхэлсэх slot-уудыг тусад нь салгаад хэвлэнэ.

    Жишээ нь: 
    'Орон:B-loan сууцны:I-loan зээл:O авахад:B-action бүрдүүлэх:B-condition материал:I-condition талаар:O мэдээлэл:O авмаар:I-action байна:O <=> product_conditions'

    өгүүлбэр байхад 'loan', 'action', 'condition' гэсэн slot-уудыг тус тусад хадгалана.
    [['орон сууцны', 'loan']], [['бүрдүүлэх материал', 'condition']] гэх мэтээр.

    """
    for slot in slots:
        slot_full_token = []

        if slot in slots_b:
            slot_b_ind = np.where(np.array(all_slots) == slot)[0].tolist()

            for i in range(len(slot_b_ind)):
                new_item = [sent[slot_b_ind[i]][0]]
                new_item += [pair[0] for pair in sent[slot_b_ind[i] + 1:] if pair[1][2:] == slot[2:]]
                slot_full_token.append([' '.join(new_item), slot])

            return slot_full_token


def all_product_names_with_given_slot(knowledge_base):
    """
    all_product_names_with_given_slot function returns all product names in given knowledge_base
    :param knowledge_base: knowledge_base on the product user is asking about
    :return: all product names in the given knowledge base
    """
    all_product_names_with_given_slot = []

    for idx in range(len(knowledge_base)):
        product_name = knowledge_base[idx][0]['product_name'].lower().split()
        all_product_names_with_given_slot.append(product_name)

    return all_product_names_with_given_slot

def word_difference_count(kb_name, user_input_name, substitute_word):
    """
    word_difference_count function calculates word difference between product_name in knowledge_base and name which user input
    :param kb_name: product name in knowledge base (full name)
    :param user_input_name: product name which the user is asking about (user input)
    :param substitute_word: дата үүсгэх үед зээл болон карт гэсэн үгнүүдийг I-loan, I-card гэж аваагүй. Харин knowledge base дотор эдгээр үгнүүд
                            нь бүтээгдэхүүний нэрэнд орсон байгаа тул хасч өгөх үг. Жишээ нь 'карт'. Хадгаламж гэдэг үг харин I-depo гэж label
                            хийсэн болохоор хасаагүй
    :return: word differences between full product name and name which user input.
    """
    if substitute_word == 'хадгаламж':
        substitute_word = ''

    substitute_word_count = kb_name.count(substitute_word)
    kb_name_len = len(kb_name) - substitute_word_count
    user_input_name_len = len(user_input_name)

    if kb_name_len >= user_input_name_len:
        diff = len(set(kb_name) - set(user_input_name)) - substitute_word_count

        if diff < kb_name_len:
            diff = diff
        elif diff <= 0:
            diff = 0
        else:
            diff = np.nan
    else:
        diff = len(set(user_input_name) - set(kb_name)) - substitute_word_count

        if diff != 0:
            diff = np.nan

    return diff


def min_word_difference_indexes(diff_between_names):
    """
    min_word_difference_indexes function takes all differences between knowledge base names and user input name then returns minimum word
    difference indexes
    :param diff_between_names: all differences between every product name in given knowledge base and name which user input.
    :return: minimum word difference indexes
    """
    all_diff_and_idx = [[diff_between_names[idx], idx] for idx in range(len(diff_between_names)) if diff_between_names[idx] is not np.nan]
    only_diff = [pair[0] for pair in all_diff_and_idx]

    min_diff_values = np.where(np.array(only_diff) == min(only_diff))[0].tolist()
    min_diff_idx = []

    for val in min_diff_values:
        min_diff_idx.append(all_diff_and_idx[val][1])

    return min_diff_idx

def possible_products_info(knowledge_base, idx):
    """
    possible_products_info function returns product info with given idx from knowledge base
    :param knowledge base: given knowledge base which we are looking for product names
    :param idx: minimum word difference index
    :return: product info with given index from knowledge base
    """
    temp = []

    product_name = knowledge_base[idx][0]['product_name']
    about_product = knowledge_base[idx][0]['about_product']
    required_materials = knowledge_base[idx][0]['required_materials']
    additional_info = knowledge_base[idx][0]['additional_info']

    basic_info = [
        product_name,
        about_product,
        required_materials,
        additional_info
    ]

    tables = []
    for table in knowledge_base[idx][1:]:
        tables.append(pd.DataFrame(table))


    temp.append(basic_info)
    temp.append(tables)

    return temp
