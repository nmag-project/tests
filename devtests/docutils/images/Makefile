html:
	rst2html --strict -v test.txt test.html -r 1 -g -t -d -s

pdf:
	rst2latex --strict -v test.txt test.tex -g -t -d
	pdflatex test.tex

setscale:
	convert data_M.png.org -density 55 data_M.png
	

