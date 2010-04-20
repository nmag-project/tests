.PHONY: clean test1

test1:
	python mesh_gen.py
	python run_perf_tests_1.py
	python plots_gen.py 

clean:
	rm -f *.nmesh.h5 *.old bigbar_dat.*

