MODEL_NAME="wechat_text2sql"


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

