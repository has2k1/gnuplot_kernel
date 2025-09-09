# set terminal pngcairo enhanced color size 1000, 1077 crop
set terminal pngcairo enhanced transparent size 147, 171 crop
set output 'logo-64x64.png'
set parametric
set urange [-pi:pi]
set vrange [-pi:pi]
set isosamples 50,20

unset key
unset xtics
unset ytics
unset ztics
unset colorbox
unset border

set pm3d depthorder

splot cos(u)+.5*cos(u)*cos(v),sin(u)+.5*sin(u)*cos(v),.5*sin(v) with pm3d, \
      1+cos(u)+.5*cos(u)*cos(v),.5*sin(v),sin(u)+.5*sin(u)*cos(v) with pm3d
