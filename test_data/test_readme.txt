1. k=3, max_iter = 333, eps=0, input_1_db_1, input_1_db_2
2. k=7, max_iter = not provided, eps=0, input_2_db_1, input_2_db_2
3. k=15, max_iter = 750, eps=0, input_3_db_1, input_3_db_2

python3 kmeans_pp.py 3 333 0 test_data/input_1_db_1.txt test_data/input_1_db_2.txt
python3 kmeans_pp.py 7 0 test_data/input_2_db_1.txt test_data/input_2_db_2.txt
python3 kmeans_pp.py 15 750 0 test_data/input_3_db_1.txt test_data/input_3_db_2.txt