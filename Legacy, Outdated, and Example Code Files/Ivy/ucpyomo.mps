* Source:     Pyomo MPS Writer
* Format:     Free MPS
*
NAME Unit Commitment Model
OBJSENSE
 MIN
ROWS
 N  x37
 L  c_u_x38_
 E  c_e_x39_
 L  c_u_x40_
 E  c_e_x41_
 L  c_u_x42_
 E  c_e_x43_
 L  c_u_x44_
 E  c_e_x45_
 L  c_u_x46_
 E  c_e_x47_
 L  c_u_x48_
 E  c_e_x49_
 L  c_u_x50_
 E  c_e_x51_
 L  c_u_x52_
 E  c_e_x53_
 L  c_u_x54_
 E  c_e_x55_
 L  c_u_x56_
 L  c_u_x57_
 L  c_u_x58_
 L  c_u_x59_
 L  c_u_x60_
 L  c_u_x61_
 L  c_u_x62_
 L  c_u_x63_
 L  c_u_x64_
 L  c_u_x65_
 L  c_u_x66_
 L  c_u_x67_
 L  c_u_x68_
 L  c_u_x69_
 L  c_u_x70_
 L  c_u_x71_
 L  c_u_x72_
 L  c_u_x73_
 E  c_e_x74_
 E  c_e_x75_
 E  c_e_x76_
 G  c_l_x77_
 G  c_l_x78_
 G  c_l_x79_
 L  c_u_x80_
 L  c_u_x81_
 L  c_u_x82_
 L  c_u_x83_
 L  c_u_x84_
 L  c_u_x85_
 L  c_u_x86_
 L  c_u_x87_
 L  c_u_x88_
 L  c_u_x89_
 L  c_u_x90_
 L  c_u_x91_
 L  c_u_x92_
 L  c_u_x93_
 L  c_u_x94_
 L  c_u_x95_
 L  c_u_x96_
 L  c_u_x97_
COLUMNS
     x1 x37 0.10000000000000001
     x1 c_u_x56_ 1
     x1 c_u_x65_ -1
     x1 c_e_x74_ 1
     x1 c_u_x80_ 1
     x1 c_u_x83_ -1
     x1 c_u_x89_ -1
     x1 c_u_x92_ 1
     x2 x37 0.10000000000000001
     x2 c_u_x59_ 1
     x2 c_u_x68_ -1
     x2 c_e_x75_ 1
     x2 c_u_x83_ 1
     x2 c_u_x86_ -1
     x2 c_u_x92_ -1
     x2 c_u_x95_ 1
     x3 x37 0.10000000000000001
     x3 c_u_x62_ 1
     x3 c_u_x71_ -1
     x3 c_e_x76_ 1
     x3 c_u_x86_ 1
     x3 c_u_x95_ -1
     x4 x37 0.125
     x4 c_u_x57_ 1
     x4 c_u_x66_ -1
     x4 c_e_x74_ 1
     x4 c_u_x81_ 1
     x4 c_u_x84_ -1
     x4 c_u_x90_ -1
     x4 c_u_x93_ 1
     x5 x37 0.125
     x5 c_u_x60_ 1
     x5 c_u_x69_ -1
     x5 c_e_x75_ 1
     x5 c_u_x84_ 1
     x5 c_u_x87_ -1
     x5 c_u_x93_ -1
     x5 c_u_x96_ 1
     x6 x37 0.125
     x6 c_u_x63_ 1
     x6 c_u_x72_ -1
     x6 c_e_x76_ 1
     x6 c_u_x87_ 1
     x6 c_u_x96_ -1
     x7 x37 0.14999999999999999
     x7 c_u_x58_ 1
     x7 c_u_x67_ -1
     x7 c_e_x74_ 1
     x7 c_u_x82_ 1
     x7 c_u_x85_ -1
     x7 c_u_x91_ -1
     x7 c_u_x94_ 1
     x8 x37 0.14999999999999999
     x8 c_u_x61_ 1
     x8 c_u_x70_ -1
     x8 c_e_x75_ 1
     x8 c_u_x85_ 1
     x8 c_u_x88_ -1
     x8 c_u_x94_ -1
     x8 c_u_x97_ 1
     x9 x37 0.14999999999999999
     x9 c_u_x64_ 1
     x9 c_u_x73_ -1
     x9 c_e_x76_ 1
     x9 c_u_x88_ 1
     x9 c_u_x97_ -1
     x10 x37 5
     x10 c_e_x39_ -1
     x10 c_e_x45_ 1
     x10 c_u_x56_ -350
     x10 c_u_x65_ 50
     x10 c_l_x77_ 350
     x10 c_u_x83_ -200
     x10 c_u_x89_ -300
     x11 x37 5
     x11 c_e_x45_ -1
     x11 c_e_x51_ 1
     x11 c_u_x59_ -350
     x11 c_u_x68_ 50
     x11 c_l_x78_ 350
     x11 c_u_x86_ -200
     x11 c_u_x92_ -300
     x12 x37 5
     x12 c_e_x51_ -1
     x12 c_u_x62_ -350
     x12 c_u_x71_ 50
     x12 c_l_x79_ 350
     x12 c_u_x95_ -300
     x13 x37 7
     x13 c_e_x41_ -1
     x13 c_e_x47_ 1
     x13 c_u_x57_ -200
     x13 c_u_x66_ 80
     x13 c_l_x77_ 200
     x13 c_u_x84_ -100
     x13 c_u_x90_ -150
     x14 x37 7
     x14 c_e_x47_ -1
     x14 c_e_x53_ 1
     x14 c_u_x60_ -200
     x14 c_u_x69_ 80
     x14 c_l_x78_ 200
     x14 c_u_x87_ -100
     x14 c_u_x93_ -150
     x15 x37 7
     x15 c_e_x53_ -1
     x15 c_u_x63_ -200
     x15 c_u_x72_ 80
     x15 c_l_x79_ 200
     x15 c_u_x96_ -150
     x16 x37 6
     x16 c_e_x43_ -1
     x16 c_e_x49_ 1
     x16 c_u_x58_ -140
     x16 c_u_x67_ 40
     x16 c_l_x77_ 140
     x16 c_u_x85_ -100
     x16 c_u_x91_ -100
     x17 x37 6
     x17 c_e_x49_ -1
     x17 c_e_x55_ 1
     x17 c_u_x61_ -140
     x17 c_u_x70_ 40
     x17 c_l_x78_ 140
     x17 c_u_x88_ -100
     x17 c_u_x94_ -100
     x18 x37 6
     x18 c_e_x55_ -1
     x18 c_u_x64_ -140
     x18 c_u_x73_ 40
     x18 c_l_x79_ 140
     x18 c_u_x97_ -100
     x19 x37 20
     x19 c_u_x38_ 1
     x19 c_e_x39_ 1
     x19 c_u_x80_ -200
     x20 x37 20
     x20 c_u_x44_ 1
     x20 c_e_x45_ 1
     x20 c_u_x83_ -200
     x21 x37 20
     x21 c_u_x50_ 1
     x21 c_e_x51_ 1
     x21 c_u_x86_ -200
     x22 x37 18
     x22 c_u_x40_ 1
     x22 c_e_x41_ 1
     x22 c_u_x81_ -100
     x23 x37 18
     x23 c_u_x46_ 1
     x23 c_e_x47_ 1
     x23 c_u_x84_ -100
     x24 x37 18
     x24 c_u_x52_ 1
     x24 c_e_x53_ 1
     x24 c_u_x87_ -100
     x25 x37 5
     x25 c_u_x42_ 1
     x25 c_e_x43_ 1
     x25 c_u_x82_ -100
     x26 x37 5
     x26 c_u_x48_ 1
     x26 c_e_x49_ 1
     x26 c_u_x85_ -100
     x27 x37 5
     x27 c_u_x54_ 1
     x27 c_e_x55_ 1
     x27 c_u_x88_ -100
     x28 x37 0.5
     x28 c_u_x38_ 1
     x28 c_e_x39_ -1
     x28 c_u_x89_ -300
     x29 x37 0.5
     x29 c_u_x44_ 1
     x29 c_e_x45_ -1
     x29 c_u_x92_ -300
     x30 x37 0.5
     x30 c_u_x50_ 1
     x30 c_e_x51_ -1
     x30 c_u_x95_ -300
     x31 x37 0.29999999999999999
     x31 c_u_x40_ 1
     x31 c_e_x41_ -1
     x31 c_u_x90_ -150
     x32 x37 0.29999999999999999
     x32 c_u_x46_ 1
     x32 c_e_x47_ -1
     x32 c_u_x93_ -150
     x33 x37 0.29999999999999999
     x33 c_u_x52_ 1
     x33 c_e_x53_ -1
     x33 c_u_x96_ -150
     x34 x37 1
     x34 c_u_x42_ 1
     x34 c_e_x43_ -1
     x34 c_u_x91_ -100
     x35 x37 1
     x35 c_u_x48_ 1
     x35 c_e_x49_ -1
     x35 c_u_x94_ -100
     x36 x37 1
     x36 c_u_x54_ 1
     x36 c_e_x55_ -1
     x36 c_u_x97_ -100
RHS
     RHS c_u_x38_ 1
     RHS c_e_x39_ 0
     RHS c_u_x40_ 1
     RHS c_e_x41_ 0
     RHS c_u_x42_ 1
     RHS c_e_x43_ -1
     RHS c_u_x44_ 1
     RHS c_e_x45_ 0
     RHS c_u_x46_ 1
     RHS c_e_x47_ 0
     RHS c_u_x48_ 1
     RHS c_e_x49_ 0
     RHS c_u_x50_ 1
     RHS c_e_x51_ 0
     RHS c_u_x52_ 1
     RHS c_e_x53_ 0
     RHS c_u_x54_ 1
     RHS c_e_x55_ 0
     RHS c_u_x56_ 0
     RHS c_u_x57_ 0
     RHS c_u_x58_ 0
     RHS c_u_x59_ 0
     RHS c_u_x60_ 0
     RHS c_u_x61_ 0
     RHS c_u_x62_ 0
     RHS c_u_x63_ 0
     RHS c_u_x64_ 0
     RHS c_u_x65_ 0
     RHS c_u_x66_ 0
     RHS c_u_x67_ 0
     RHS c_u_x68_ 0
     RHS c_u_x69_ 0
     RHS c_u_x70_ 0
     RHS c_u_x71_ 0
     RHS c_u_x72_ 0
     RHS c_u_x73_ 0
     RHS c_e_x74_ 160
     RHS c_e_x75_ 500
     RHS c_e_x76_ 400
     RHS c_l_x77_ 176
     RHS c_l_x78_ 550
     RHS c_l_x79_ 440
     RHS c_u_x80_ 0
     RHS c_u_x81_ 0
     RHS c_u_x82_ 200
     RHS c_u_x83_ 0
     RHS c_u_x84_ 0
     RHS c_u_x85_ 0
     RHS c_u_x86_ 0
     RHS c_u_x87_ 0
     RHS c_u_x88_ 0
     RHS c_u_x89_ 0
     RHS c_u_x90_ 0
     RHS c_u_x91_ -100
     RHS c_u_x92_ 0
     RHS c_u_x93_ 0
     RHS c_u_x94_ 0
     RHS c_u_x95_ 0
     RHS c_u_x96_ 0
     RHS c_u_x97_ 0
BOUNDS
 LO BOUND x1 0
 LO BOUND x2 0
 LO BOUND x3 0
 LO BOUND x4 0
 LO BOUND x5 0
 LO BOUND x6 0
 LO BOUND x7 0
 LO BOUND x8 0
 LO BOUND x9 0
 BV BOUND x10
 BV BOUND x11
 BV BOUND x12
 BV BOUND x13
 BV BOUND x14
 BV BOUND x15
 BV BOUND x16
 BV BOUND x17
 BV BOUND x18
 BV BOUND x19
 BV BOUND x20
 BV BOUND x21
 BV BOUND x22
 BV BOUND x23
 BV BOUND x24
 BV BOUND x25
 BV BOUND x26
 BV BOUND x27
 BV BOUND x28
 BV BOUND x29
 BV BOUND x30
 BV BOUND x31
 BV BOUND x32
 BV BOUND x33
 BV BOUND x34
 BV BOUND x35
 BV BOUND x36
ENDATA
