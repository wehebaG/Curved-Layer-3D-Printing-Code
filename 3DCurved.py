"""
Matthew Guile
Wichita  State  University Curved Layer Fused Deposition Toolpath Generation
"""

# Import libraries import math
import numpy as np
import matplotlib.pyplot as plt from mpl_toolkits import mplot3d import datetime

# Input  printing  parameters
printSize   =   75	#   Square   footprint   part   (mm)
nozzleDiameter  =  0.4	#  Diameter  of  printer  nozzle
layerHeight  =  0.2	# Layer  height  for  printed  part
extruderTemp = 215	# Extruder   temperature   (C)
bedTemp = 60	# Bed temperature (C)
print_speed = 3600	# Print speed (mm/min)
filamentDiameter  =  1.75	# Diamter  of  filament
flowModifier  =  1.05	# Percentage  of  flow  modifier
retractionLength   =   4	#   Retraction   distance   (mm)
retractionSpeed   =   2400	# Retraction speed (mm/min)
surfaceLayers  =  5	# Number  of  shells  or  surface  layers

# Initialize  variables
span   =   int(printSize/nozzleDiameter)+1	#  Interim  value  for  x-y-z  array
z_arr =  np.zeros((span,span))	# Initialize  array  for  surface  values

# Function that generates z value given x and y values def surf_func(i,j):
maxTheta = math.pi	# Max  theta  for  surface  equation
amplitude  =  7.5	# Amplitude  of  surface  equation
z_offset  =  1.0	# Offset  in  Z  direction

# Offset for first layer height z_offset += layerHeight

x =  maxTheta  *  (i/span) y  =  maxTheta  *  (j/span)
 

# Here is the surface equation!
#return amplitude*(math.sin(x)**(3/2))*(math.sin(y)**(3/2))+z_offset return amplitude*(math.sin(y)**2)+z_offset

# Function that generates surface plot def surf_plot(plot_span):
#   Generate    surface    plot x_arr = np.arange(plot_span) y_arr = np.arange(plot_span)
x_arr, y_arr = np.meshgrid(x_arr, y_arr) fig = plt.figure()
ax     =     plt.axes(projection=’3d’)

ax.plot_surface(x_arr, y_arr, z_arr,cmap=’viridis’, edgecolor=’none’) ax.set_zlim(0, 25)
ax.set_title(’Surface plot’) plt.show()

# Function that calculates the extrusion value for G01 command def calc_extrusion(x, y, i_diff, j_diff, h):
# Initialize  variables
z_diff  =  0	# Z value difference from previous pt
res  =  0	# Resultant  vector  from  each  pt
area_road  =  0	#   Cross-sectional   area   of   road
volume_out = 0	# Volume to extrude for G01 path
e_instant   =   0	# Instant E value for G01 path

z_diff = z_arr[x][y] - z_arr[x+i_diff][y+j_diff] +  h res = math.sqrt((nozzleDiameter**2) + (z_diff**2))

area_road = ((nozzleDiameter - layerHeight)*layerHeight) \
+ (math.pi*(layerHeight/2)**2) volume_out = area_road*res

e_instant =  (volume_out  /  (math.pi  *  (filamentDiameter/2)**2))  \
* flowModifier
return e_instant


# Function that generates the curved  layer  g-code def gen_gcode(tot_layers):
#  Initialize  variables
 
e_count = 0	# Initialize absolute E value (mm)
z_hop_height  =  15	# Z height  for  safe  travel  moves # Note: Offset is for a delta stlye build plate
x_offset   =   -printSize/2	#   X   offset   on   buildplate
y_offset   =   -printSize/2	#   Y   offset   on   buildplate

# Determines maximum z height of part for  clearance max = np.amax(z_arr)
z_hop = max + z_hop_height

# Create  a  blank  g-code  file
file_out  =  open("CL-Part.gcode",  "w+")

# Get date and time to stamp on outputted g-code e = datetime.datetime.now()


# Write  start-up  g-code
file_out.write("Matthew Guile - Curved Layer Fused Deposition \n"
+e.strftime("%B %d, %Y %H:%M:%S")+ "\n" \ ";Set up \n" \
"M104 S" +str(extruderTemp)+ " ;Set extruder temp \n" \ "M105 ;Get extruder temperature \n" \
"M109 S" +str(extruderTemp)+ " ;Wait for temp \n" \ "M82	;absolute extrusion mode \n" \
"G28	;Home \n" \
"G92 E0  ;Reset  extruder  position  \n  \n")

# Iterate g-code for each layer for layer in range(tot_layers):

# Alternate between left/right and up/down rastering if layer % 2 == 0:

# On even numbered layers, raster up/down for i in range(span):

# If starting from the bottom and traveling up if i % 2 == 0:
for j in range(1,span): x_diff = 0
y_diff =  -1

h = z_compensation(i, j, x_diff, y_diff)
 
x = (i *  nozzleDiameter)  +  x_offset y = (j * nozzleDiameter) + y_offset
#z = z_arr[i][j]  +  h  +  (layerHeight  *  layer) z = z_arr[i][j] + (layerHeight * layer)
e_count += calc_extrusion(i, j, x_diff, y_diff, h)

gCommand = print_gcode(x, y, z, e_count, print_speed) file_out.write(gCommand)

# If starting from the top and traveling down else:
for j in range(span-2, -1, -1):
x_diff  =  0
y_diff  =  1
h = z_compensation(i,  j, x_diff, y_diff) x = (i * nozzleDiameter) + x_offset
y = (j * nozzleDiameter) + y_offset
#z = z_arr[i][j]  +  h  +  (layerHeight  *  layer) z = z_arr[i][j] + h + (layerHeight * layer)
e_count += calc_extrusion(i, j, x_diff, y_diff, h)

gCommand = print_gcode(x, y, z, e_count, print_speed) file_out.write(gCommand)
# Finish this  layer  and  prepare  for  next  layer # Retract filament
file_out.write("G01 E"  +  str(e_count  - retractionLength)  \
+ " F"  +  str(retractionSpeed)) # Move in  z  to  avoid  collision file_out.write("G01 Z" + str(z_hop) \
+ " F"  +  str(print_speed)  +  "\n") # Move to starting point of next layer file_out.write("G01 X" + str(x_offset) \
+  "  Y"  +  str(y_offset)  \
+ " F"  +  str(print_speed)  +  "\n") # Un-retract filament
file_out.write("G01   E"   +   str(e_count   +   retractionLength)   \
+ "  F"  +  str(retractionSpeed))

# Alternate between left/right and up/down rastering else:
 
#  If  starting  from  the  right  and  traveling  left for j in range(span):

# Check if even or odd row to create raster pattern if j % 2 == 0:
for i in range(1,span): x_diff = -1
y_diff =  0
h = z_compensation(i,  j, x_diff, y_diff) x = (i * nozzleDiameter) + x_offset
y = (j * nozzleDiameter) + y_offset
#z = z_arr[i][j]  +  h  +  (layerHeight  *  layer) z = z_arr[i][j] + (layerHeight * layer)
e_count += calc_extrusion(i, j, x_diff, y_diff, h)

gCommand = print_gcode(x, y, z, e_count, print_speed) file_out.write(gCommand)

# If starting from the left and traveling right else:
for i in range(span-2, -1, -1):
x_diff  =  1
y_diff  =  0
h = z_compensation(i,  j, x_diff, y_diff) x = (i * nozzleDiameter) + x_offset
y = (j * nozzleDiameter) + y_offset
#z = z_arr[i][j]  +  h  +  (layerHeight  *  layer) z = z_arr[i][j] + (layerHeight * layer)
e_count += calc_extrusion(i, j, x_diff, y_diff, h)

gCommand = print_gcode(x, y, z, e_count, print_speed) file_out.write(gCommand)
# Finish this  layer  and  prepare  for  next  layer # Retract filament
file_out.write("G01 E"  +  str(e_count  - retractionLength)  \
+ " F"  +  str(retractionSpeed)) # Move in  z  to  avoid  collision file_out.write("G01 Z" + str(z_hop) \
+ "  F"  +  str(print_speed)  +  "\n")
 
# Move to starting point of next layer file_out.write("G01   X"   +   str(x_offset)   \
+  "  Y"  +  str(y_offset)  \
+ " F"  +  str(print_speed)  +  "\n") # Un-retract filament
file_out.write("G01   E"   +   str(e_count   +   retractionLength)   \
+ "  F"  +  str(retractionSpeed))

file_out.close()

# Function that compensates for the nozzle being too high/low. # B/c the printer is a three-axis machine, the nozzle is not
# normal and will scrape if the printing angle is too high def z_compensation(i, j, i_diff, j_diff):
nozzleWidth = 1.8	# Out diameter of the nozzle z_diff  =  0	# Initialize to zero
theta = 0	# Initialize to  zero z_diff =  z_arr[i][j]  -  z_arr[i+i_diff][j+j_diff] theta = math.asin(z_diff/nozzleWidth)
if theta>=0:
return (((layerHeight  /  2)/  math.cos(theta))  \
+((nozzleWidth / 2)*math.tan(theta))) * 0.5
else:
return ((nozzleWidth/4)*math.tan(theta)) * 0.5


# Function that print the G01 commands def print_gcode(x, y, z, e, f):
return ("G01  X"  +  str(x)  +  \
"  Y"  +  str(y)  +  \
"  Z"  +  str(z)  +  \
"  E"  +  str(e)  +  \
" F" + str(f) +  "\n")

# Function that outputs a point  cloud  to  later  be  used  to  design  supports def print_coordinates():
file_out = open("coordinates.asc", "w+") for i in range (0, span):
for j in range(0, span):
file_out.write(str(i*nozzleDiameter)   +   "   "   \
 
+ str(j*nozzleDiameter)  +  "  "  \
+  str(z_arr[i][j])  +  "\n")
file_out.close()

##############################################################################  #	CURVED LAYER FUSED DEPOSITON MODELING	#
#	TOOLPATH GENERATION	# ##############################################################################

# Populate array with z values for i in range(span):
for j in range(span):
z_arr[i][j]  =  surf_func(i,j)  +  layerHeight

# Plot the surface that is to be printed surf_plot(span)

# Create the corresponding G-Code gen_gcode(surfaceLayers)

# Output the point cloud that is later to be used to create core structure #print_coordinates()
