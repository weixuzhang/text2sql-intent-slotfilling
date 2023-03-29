import json
import argparse
from detector import JointIntentSlotDetector
from parsing import ValueParsingSlotFilling
from LAC import LAC
from rich.table import Column, Table
from rich import box
from rich.console import Console

lac = LAC()
lac.load_customization('data/dictionary.txt', sep=None)
with open("data/data_origin.json", "r") as read:
    originload: dict = json.load(read)
  
console=Console(record=True)
training_logger = Table( 
                        Column("Intent", justify="center"),
                        Column("Slots", justify="center"), 
                        Column("Features", justify="center"), 
                        Column("SQL", justify="center"), 
                        title="Text-to-SQL Output",pad_edge=False, box=box.ASCII)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", default="查看支付有优惠优惠券曝光页面在8月1号这天的每小时pv，uv", type=str, help="Input utterance for prediction")
    parser.add_argument("--model_path", default="saved_models/new/model/model_epoch19", type=str, help="Input path of the model")
    parser.add_argument("--tokenizer_path", default="saved_models/new/tokenizer/", type=str, help="Input path of the tokenizer")
    parser.add_argument("--intent_label_path", default="data/intent_labels.txt", type=str, help="Input path of the intent labels")
    parser.add_argument("--slot_label_path", default="data/slot_labels.txt", type=str, help="Input path of the slot labels")
    pred = parser.parse_args()

    ### intent and slot recognization
    model = JointIntentSlotDetector.from_pretrained(pred.model_path,pred.tokenizer_path,pred.intent_label_path,pred.slot_label_path)
    result=model.detect(pred.q) 
    intent,slots=result['intent'],result['slots']

    ### value parsing and slot filling
    parsing=ValueParsingSlotFilling.parse(intent,slots,originload)
    pre_sql,slots=parsing['pre_sql'],parsing['slots']

    ### name entity recognization and select features
    features_complete=[feature for feature in originload[intent]['features'].values()]      
    features_list=lac.run(pred.q)[1]                                                 
    sql_features=set(features_complete).intersection(set(features_list))         

    ### formatting output
    console.print(f'SQL prediction of {pred.q}')
    intent_txt=intent + "模板意图：" + originload[intent]['text']
    training_logger.add_row(str(intent_txt), str(slots),str(sql_features),str(pre_sql))
    console.print(training_logger)
    print("predicted sql:\n"+pre_sql)



    #select_list = re.findall(r'SELECT(.*?)FROM|from', originload[intent]['template'])[0].split(',')   
    # for item in set(features_complete)-set(features_list):
    #     for select in select_list:
    #         pre_sql = pre_sql.replace(','+select, ' ')  if item in select else pre_sql



    
