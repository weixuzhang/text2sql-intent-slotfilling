import json
import random

if __name__ == '__main__':
    with open('data_origin.json', 'r') as f:
        originload = json.load(f)
    dictionary=[]
    for item in originload.values():
        for feature_k,feature_v in item['features'].items():
            if feature_k + '/' + feature_v not in dictionary:
                dictionary.append(feature_k + '/' + feature_v)
    data=[]
    for k,v in originload.items():
        v['intent'],v['domain']=k,'wechatpay'
        del v['template'], v['features']
        data.append(v)
    data_all=50*data
    random.shuffle(data_all)

    intent_labels = ['[UNK]']
    slot_labels = ['[PAD]','[UNK]', '[O]']
    for item in data:
        if item['intent'] not in intent_labels:
            intent_labels.append(item['intent'])

        for slot_name, slot_value in item['slots'].items():
            if 'B_'+slot_name not in slot_labels:
                slot_labels.extend(['I_'+slot_name, 'B_'+slot_name])
    
    with open('slot_labels.txt', 'w') as f:
        f.write('\n'.join(slot_labels))

    with open('intent_labels.txt', 'w') as f:
        f.write('\n'.join(intent_labels))

    # with open('dictionary.txt', 'w') as f:
    #     f.write('\n'.join(dictionary))

    with open('train.json', "w",encoding='utf-8') as outfile:
            json.dump(data_all, outfile,ensure_ascii=False, indent=2)

