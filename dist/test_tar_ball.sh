mkdir -p tmp
cd tmp
wget http://nmag.soton.ac.uk/nmag/0.1/download/nmag-0.1-all.tar.gz 
tar xfvz nmag-0.1-all.tar.gz
cd nmag-0.1
time make
time make doc
make checkall


