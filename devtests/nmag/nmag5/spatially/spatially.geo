algebraic3d

# cubes
solid soft = orthobrick (-5.0, -50.0, -50.0;  0.0, 50.0, 50.0) -maxh = 4;
solid hard = orthobrick ( 0.0, -50.0, -50.0; 10.0, 50.0, 50.0) -maxh = 4;
tlo soft;
tlo hard;

#solid film = soft or hard;
#tlo film;

