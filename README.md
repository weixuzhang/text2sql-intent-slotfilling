# 基于意图识别和槽填充的复杂SQL生成模型

代码pipline主要分为三个步骤，分别基于以下三个模块：

模块1：基于BERT的意图（intent）和槽位（slots）联合预测模块，其中意图分类用于确定SQL模板，槽位预测用于确定Value值。网络结构借鉴于[JoinBERT](https://arxiv.org/abs/1902.10909)，利用 [CLS]token对应的last hidden state去预测整句话的intent，并利用句子tokens的last hidden states做序列标注，找出包含slot values的tokens。
模块2：命名实体识别模块，用于抽取问题涉及到的关键特征和实体。这一模块主要由百度开源的中文词法工具LAC实现。
模块3：槽值解析模块，用于将value值解析为标准格式并填充到SQL模板中。这一模块主要由JioNLP时间语义解析工具包和自定义函数实现。


## 运行环境与依赖
- Python 3.9
- Pytorch 1.13
- transformers
- huggingface 
- jionlp
- lac
- rich

## 模型训练

### 数据准备

模型主要依赖以下几个数据文件：

1. 原始数据：以json格式给出，保存在data/data_origin.json中，每条数据包含以SQL意图的类别标签为键，值包含四个方面的信息：
`text`是此类意图的自然语言问题，`template`是对应的包含槽值的SQL模板，`slots`是问题中包括的所有槽位以及对应的槽值，`features`是问题涉及到的关键特征和实体，其中key为实体的自然语言表述，value为SQL模板中的对应别名
数据样例如下：

```json
{
    "intent_1":{
        "text":"查看支付有优惠优惠券曝光页面在20220801这天的每小时pv，uv",
        "template":"SELECT ds, count(1) as pv, count(distinct uin_) as uv FROM wxg_wechat_pay_intership2::t_dwd_tmp_wxpay_discount_event_log_hour WHERE ds BETWEEN slot_datetime_b AND slot_datetime_e AND event_code_ IN ('AwardListExposure') group by ds",
        "slots":{
            "datetime": "20220801这天"
        },
        "features":{
            "pv":"pv",
            "uv":"uv"
        }
    }
}
```

2. 衍生数据：以txt格式给出，包含意图标签(intent_labels.txt)、槽位标签(slot_labels.txt)、命名实体字典(dictionary.txt)三个文件，均可由原始数据文件通过data_processing.py处理得到
（1）意图标签：每行一个意图，未识别意图以`[UNK]`标签表示。
```txt
[UNK]
intent_1
intent_2
intent_3
...
```
（2）槽位标签：包括三个特殊标签： `[PAD]`表示输入序列中的padding token, `[UNK]`表示未识别序列标签, `[O]`表示没有槽位的token标签。对于有含义的槽位标签，又分为以'B_'开头的槽位开始的标签, 以及以'I_'开头的其余槽位标记两种。
```txt
[PAD]
[UNK]
[O]
I_datetime
B_datetime
...
```
（3）命名实体字典：用于标记问题涉及到的关键特征和实体，每行一个实体，"/"左边为实体的自然语言表述，右边为SQL模板中的对应别名
```txt
曝光率/expo_ratio
点击率/click_ratio
兑换率/obtain_ratio
...
```

### 训练过程
在数据准备完成后，可以进行意图与槽位预测模块的模型训练，这里我们选择在`bert-base-chinese`预训练模型基础上进行finetune：
可以直接执行train.sh文件，或直接输入以下命令：
```bash
python3 train.py\
       --cuda_devices 0\
       --tokenizer_path "bert-base-chinese"\
       --model_path "bert-base-chinese"\
       --train_data_path "data/train.json"\
       --intent_label_path "data/intent_labels.txt"\
       --slot_label_path "data/slot_labels.txt"\
       --save_dir "saved_models/new"\
       --batch_size 64\
       --train_epochs 20
```
注： savd_models中已保存有一版训练好的模型，可以直接使用


## SQL预测

模型训练完后，我们通过加载训练好的模型进行意图与槽位预测，进而通过实体识别和槽值解析填充生成完整SQL
可以直接输入以下命令：
```bash
python3 predict.py --q '查看支付有优惠优惠券曝光页面在8月1号这天的每小时pv，uv'
```
或执行 predict.sh 文件，修改模型位置等其他参数

### 注意：
为提高准确性，请尽量使用绝对和常见的时间表达，如“第一季度”，“八月份”，“8月10号”，“8月5日0-2时”等
尽量不用相对时间表达，如“上个星期”，“昨天”，“前两个小时”，“当前时刻”等，因时间基点设在了2022年8月1日，易产生混淆


### 输出结果分析

结果展示分为四个部分：`intent`,`slots`,`features`及`SQL`。
`intent`:指明自然语言对应的意图类别标签及对应的模板问题
`slots`：指明问题中包括的所有槽位以及对应的槽值
`features`：问题涉及到的关键特征和实体
`SQL`：输出的完整SQL


## 对于新加入数据（意图和SQL模板）的重新训练

1. 需要更新data_origin.json文件，并利用data_processing.py生成其他4个数据文件
2. 需要根据新加入的SQL模板自行定义槽值解析函数，即parsing.py，其要实现的功能是将识别出的槽值以标准格式填入SQL模板中。
   如将“top10”解析为SQL模板中的 "rank <=10"