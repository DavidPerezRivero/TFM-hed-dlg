## Commands

#### Convert-wordemb-dict2emb-matrix.py
`python convert-wordemb-dict2emb-matrix.py model_dictionary embedding_dictionary [--emb_dim n] [--std_dev] [--apply_spelling_corrections] output_matrix`


#### Convert_text2dict.py

`python convert-text2dict.py input output [--cutoff n] [--dict dict] [--use_all_dialogues] [--force_triple_format]`


#### Train.py

`THEANO_FLAGS=mode=FAST_RUN,floatX=float32,exception_verbosity=high,traceback.limit=0,optimizer=fast_compile python train.py [--resume state] [--force_train_all_wordemb] [--protoype prototype]`


#### Sample.py

`THEANO_FLAGS=mode=FAST_RUN,floatX=float32,exception_verbosity=high,traceback.limit=0,optimizer=fast_compile python sample.py model input_context output_context [--ignore-unk] [--beam_search] [--n-samples n] [--n-turns k] [--normalize] [--verbose]`


#### Chat.py

`THEANO_FLAGS=mode=FAST_RUN,floatX=float32,exception_verbosity=high,traceback.limit=0,optimizer=fast_compile python chat.py model [--ignore-unk] [--normalize]`


#### Evaluate.py

`THEANO_FLAGS=mode=FAST_RUN,floatX=float32,exception_verbosity=high,traceback.limit=0,optimizer=fast_compile
 python evaluate.py model input [--exclude-sos] [--plot-graphs]`  
 `[--exclude-stop-words] [--document-ids ruta_fichero_ids]`


#### Compute_dialogue_embeddings.py

`python Compute_dialogue_embeddings.py model dialogues output [--verbose] [--use-second-last-state]`
