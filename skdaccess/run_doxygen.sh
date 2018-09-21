rm -R latex/
doxygen dox.cfg &> out.log
cp fix_latex.sh latex
cd latex
./fix_latex.sh
make &> out.log
cd ..
