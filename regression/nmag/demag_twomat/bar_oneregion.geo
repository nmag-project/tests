algebraic3d
solid bar1 = orthobrick (-50, -15, -15; 0, 15, 15) -maxh = 4.0;
solid bar2 = orthobrick (0, -15, -15; 50, 15, 15) -maxh = 4.0;
solid bar = bar1 or bar2;
tlo bar;


