.PHONY: clean test1

test1:
	python mesh_gen.py
	python run_perf_tests_1.py
	python plots_gen_1.py 

test2:
	python run_perf_tests_2.py
	python collect_data_2.py

clean:
	rm -f *.nmesh.h5 *.old bigbar_dat.*

