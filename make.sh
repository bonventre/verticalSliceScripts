rootcling -f event/Dict.cc -c event/Hit.h event/LinkDef.h
g++ -shared -fPIC -o event/Dict.so event/Dict.cc `root-config --cflags` -I. `root-config --libs` -I`root-config --incdir`
