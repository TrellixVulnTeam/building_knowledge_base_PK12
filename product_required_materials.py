import numpy as np
import pandas as pd

import json
import pickle
import importlib
import utils_product
importlib.reload(utils_product)

from utils_product import slot_and_intent_classified_request, full_token_and_slot_constructor, all_product_names_with_given_slot, word_difference_count, min_word_difference_indexes, possible_products_info

load_path = 'knowledge_base/'
# Loading knowledge_bases
with open(f'{load_path}product_names.pickle', 'rb') as handle:
    product_names = pickle.load(handle)

with open(f'{load_path}depo.json'.format(1), 'r', encoding = 'utf-8') as json_file:
    depo = json.load(json_file)

with open(f'{load_path}account.json'.format(1), 'r', encoding = 'utf-8') as json_file:
    account = json.load(json_file)

with open(f'{load_path}loan.json'.format(1), 'r', encoding = 'utf-8') as json_file:
    loan = json.load(json_file)

with open(f'{load_path}card.json'.format(1), 'r', encoding = 'utf-8') as json_file:
    card = json.load(json_file)

# Sample request for seeing how things are working now.
req = 'Урьдчилсан:B-depo хүүт:I-depo хугацаатай:I-depo хадгаламжын:I-depo данс:B-condition нээх:I-condition доод:I-condition үлдэгдэл:I-condition гэж:O байдаг:O уу:O хэд:B-question_type вэ:O <=> product_conditions'

# depo, loan, card, digital_bank, account, product
product_slots = ['B-depo', 'B-loan', 'B-card', 'B-digital_bank', 'B-account', 'B-product']
# question types
question_type_slots = ['B-question_type']
# product_conditions, currency
condition_slots = ['B-condition', 'B-currency']
# issue, curse
issue_slots = ['B-issue', 'B-curse']
# action, request, transaction, service
action_slots = ['B-action', 'B-request', 'B-transaction', 'B-service']
# brach, day, location, district
branch_slots = ['B-branch', 'B-day', 'B-location', 'B-district']
# ebank_item, channel
ebank_item_slots = ['B-ebank_item', 'B-channel']
# greeting, gratitude
irrelevant_slots = ['B-greeting', 'B-gratitude']

slots_b, all_slots, sent = slot_and_intent_classified_request(req)

# Finding info on product
product_full_token = full_token_and_slot_constructor(product_slots, slots_b, all_slots, sent)
# For looking up conditions in knowledge base table (TODO)
condition_full_token = full_token_and_slot_constructor(condition_slots, slots_b, all_slots, sent)
# Extra at the moment
question_type_full_token = full_token_and_slot_constructor(question_type_slots, slots_b, all_slots, sent)
issue_full_token = full_token_and_slot_constructor(issue_slots, slots_b, all_slots, sent)
action_full_token = full_token_and_slot_constructor(action_slots, slots_b, all_slots, sent)
branch_full_token = full_token_and_slot_constructor(branch_slots, slots_b, all_slots, sent)
ebank_item_full_token = full_token_and_slot_constructor(ebank_item_slots, slots_b, all_slots, sent)
irrelevant_full_token = full_token_and_slot_constructor(irrelevant_slots, slots_b, all_slots, sent)

answer_set = []
query_list = product_full_token

for idx in range(len(query_list)):
    slot = query_list[idx][1][2:]
    name_which_user_input = query_list[idx][0].split()
    
    if slot == 'depo':
        knowledge_base = depo
        substitute_word = 'хадгаламж'
    elif slot == 'account':
        knowledge_base = account
        substitute_word = 'данс'
    elif slot == 'card':
        knowledge_base = card
        substitute_word = 'карт'
    elif slot == 'loan':
        knowledge_base = loan
        substitute_word = 'зээл'
    
    # Getting all product names on knowledge base
    all_product_names_with_given_slot = all_product_names_with_given_slot(knowledge_base)
    
    # Calculating word difference between product names in knowledge base and name which user input
    diff_between_names = []
    for kb_name in all_product_names_with_given_slot:
        diff = word_difference_count(kb_name, name_which_user_input, substitute_word)
        diff_between_names.append(diff)

    # Minimum word differences index
    min_diff_idx = min_word_difference_indexes(diff_between_names)

    for idx in min_diff_idx:
        temp = possible_products_info(knowledge_base, idx)

        answer_set.append(temp)


print(req, '\n')

# Print required materials for possible product matches
if len(answer_set):
    for item in answer_set:
        basic_info = item[0]
        tables = item[1]

        product_name = basic_info[0]
        about_product = basic_info[1]
        required_materials = basic_info[2]
        additional_info = basic_info[3]

        if len(condition_full_token):
            # required materials
            for item in condition_full_token:
                token = item[0].split()

                if ('бүрдүүлэх' in token) or ('материал' in token) or ('шаардпагатай' in token):
                    print(f'Product: {product_name}')
                    print('Бүрдүүлэх материал:')

                    for item in required_materials:
                        print(item)
                    print('\n')
                    
                else:
                    print(f'Product: {product_name}')
                    
                    for table in tables:
                        pd.display(table)
                    
            # TODO: Tidy up knowledge base tables so that it will be easy to look up conditions in tables.
            # I am really sorry!!
