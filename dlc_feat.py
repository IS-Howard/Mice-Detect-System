from feature_process import *
import joblib
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("csv", type=str)
args = parser.parse_args()
dst = args.csv
### feature preprocess ###################################################################################################################
dlc_raw = read_dlc(dst)
print(dst)
print(dlc_raw)
feat = count_feature(dlc_raw, feat_type='bsH')
featsav = dst.replace('.csv','_feat.sav')
print(feat)
# joblib.dump(feat, featsav)
#python dlc_feat.py  "./datadb/t3.csv"
#os.system(f'docker exec -i dlc python3 dlc_feat.py "./datadb/t3.csv" &')