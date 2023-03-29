import re
import jionlp as jio

def date_extract_transform(para):
    m = re.search("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", para)
    if m==None:
        return '00000000'
    strdate = m.group(1)
    year =  strdate[:4]
    month =  strdate[5:7]
    day =  strdate[8:10]
    hour = strdate[11:13]
    date = year + month + day + hour
    return date

def date_find(para):
    m = re.search("(\d{8})", para)
    if m==None:
        return para
    strdate = m.group(1)
    year =  strdate[:4]
    month =  strdate[4:6]
    day =  strdate[6:8]
    date = year + "年" + month + "月" + day + "日" 
    return date

def range_extract_transform(para):
    m = re.search("(\d{1,2})", para)
    if m==None:
        return '00'
    range = m.group(1)
    return range
    
def group_extract_transform(para):
    pattern = re.compile(r'\d{6}')
    group = pattern.findall(para)
    return group   

class ValueParsingSlotFilling():

    def parse(intent,slots,originload):
        date=slots['datetime'][0].replace(" ", "").replace("#", "")
        range=slots['range'][-1].replace(" ", "").replace("#", "") if 'range' in slots else "" 
        group=slots['group'][0].replace(" ", "").replace("#", "") if 'group' in slots else "" 
        if 'datetime' in slots: 
            slots['datetime']=slots['datetime'][0].replace(" ", "").replace("#", "")
        if 'range' in slots: 
            slots['range']=slots['range'][-1].replace(" ", "").replace("#", "")
        if 'group' in slots:
            slots['group']=slots['group'][0].replace(" ", "").replace("#", "")

        res = jio.ner.extract_time(date_find(date), time_base={'year': 2022,'month': 8,'day': 1})
        start=date_extract_transform(res[0]['detail']['time'][0])
        end=date_extract_transform(res[0]['detail']['time'][1])
        pre_sql=originload[intent]['template'].replace('slot_datetime_b',start)
        pre_sql=pre_sql.replace('slot_datetime_e',end)  
        if intent=='intent_12':
            start_compare,end_compare=date_extract_transform(res[1]['detail']['time'][0]),date_extract_transform(res[1]['detail']['time'][1])
            pre_sql=pre_sql.replace('slot_datetime2_b',start_compare) 
            pre_sql=pre_sql.replace('slot_datetime2_e',end_compare) 
        sql_range=range_extract_transform(range) 
        pre_sql=pre_sql.replace('slot_range',sql_range)    
        group_list=group_extract_transform(group) 
        sql_group='"'+group_list[0]+'", "'+group_list[-1]+'"' if len(group_list) >=2 else ""
        pre_sql=pre_sql.replace('slot_group',sql_group) 

        result={}
        result['slots']=slots
        result['pre_sql']= pre_sql

        return result