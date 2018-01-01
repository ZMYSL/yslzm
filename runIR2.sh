sh filter_trec.sh
python3 execute.py --work-task Trec \
                    --data-pro-dir Data/Trec/   \
                    --cpn-dir RetrivalSys/components/Trec/

cd Data/Trec
perl sample_eval.pl qrels-sampleval-2015.txt trec_eval.txt
