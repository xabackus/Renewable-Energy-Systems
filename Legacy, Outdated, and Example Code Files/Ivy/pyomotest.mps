* Source:     Pyomo MPS Writer
* Format:     Free MPS
*
NAME my model
OBJSENSE
 MAX
ROWS
 N  x3
 G  c_l_x4_
 L  c_u_x5_
COLUMNS
     x1 x3 1
     x1 c_l_x4_ 1
     x1 c_u_x5_ 3
     x2 x3 1
     x2 c_l_x4_ -1
     x2 c_u_x5_ 2
RHS
     RHS c_l_x4_ 5
     RHS c_u_x5_ 9
BOUNDS
 FR BOUND x1
 FR BOUND x2
ENDATA
