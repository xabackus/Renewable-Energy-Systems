NAME unit_commitment
ROWS
 N  OBJ
 E  demand_1
 L  max_power_G1_1
 G  min_power_G1_1
 L  max_power_G2_1
 G  min_power_G2_1
 E  demand_2
 L  max_power_G1_2
 G  min_power_G1_2
 L  max_power_G2_2
 G  min_power_G2_2
 E  demand_3
 L  max_power_G1_3
 G  min_power_G1_3
 L  max_power_G2_3
 G  min_power_G2_3
COLUMNS
    MARKER    'MARKER'                 'INTORG'
    commitment[G1,1]  OBJ       50
    commitment[G1,1]  max_power_G1_1  -60
    commitment[G1,1]  min_power_G1_1  -20
    commitment[G1,2]  OBJ       50
    commitment[G1,2]  max_power_G1_2  -60
    commitment[G1,2]  min_power_G1_2  -20
    commitment[G1,3]  OBJ       50
    commitment[G1,3]  max_power_G1_3  -60
    commitment[G1,3]  min_power_G1_3  -20
    commitment[G2,1]  OBJ       40
    commitment[G2,1]  max_power_G2_1  -40
    commitment[G2,1]  min_power_G2_1  -10
    commitment[G2,2]  OBJ       40
    commitment[G2,2]  max_power_G2_2  -40
    commitment[G2,2]  min_power_G2_2  -10
    commitment[G2,3]  OBJ       40
    commitment[G2,3]  max_power_G2_3  -40
    commitment[G2,3]  min_power_G2_3  -10
    MARKER    'MARKER'                 'INTEND'
    power[G1,1]  demand_1  1
    power[G1,1]  max_power_G1_1  1
    power[G1,1]  min_power_G1_1  1
    power[G1,2]  demand_2  1
    power[G1,2]  max_power_G1_2  1
    power[G1,2]  min_power_G1_2  1
    power[G1,3]  demand_3  1
    power[G1,3]  max_power_G1_3  1
    power[G1,3]  min_power_G1_3  1
    power[G2,1]  demand_1  1
    power[G2,1]  max_power_G2_1  1
    power[G2,1]  min_power_G2_1  1
    power[G2,2]  demand_2  1
    power[G2,2]  max_power_G2_2  1
    power[G2,2]  min_power_G2_2  1
    power[G2,3]  demand_3  1
    power[G2,3]  max_power_G2_3  1
    power[G2,3]  min_power_G2_3  1
RHS
    RHS1      demand_1  50
    RHS1      demand_2  60
    RHS1      demand_3  55
BOUNDS
 BV BND1      commitment[G1,1]
 BV BND1      commitment[G1,2]
 BV BND1      commitment[G1,3]
 BV BND1      commitment[G2,1]
 BV BND1      commitment[G2,2]
 BV BND1      commitment[G2,3]
QUADOBJ
    commitment[G1,1]  power[G1,1]  20
    commitment[G1,2]  power[G1,2]  20
    commitment[G1,3]  power[G1,3]  20
    commitment[G2,1]  power[G2,1]  25
    commitment[G2,2]  power[G2,2]  25
    commitment[G2,3]  power[G2,3]  25
ENDATA
