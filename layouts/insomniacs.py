#!/usr/bin/python
__version__ = '0.1'

import math

##define heights

moon=1494.45 # mm
bottom_planet=1010.11 #mm
top_duo_planet=2420.13 # mm
second_trio_planet=2692.5 # mm
third_trio_planet=bottom_planet #mm

#scale factor for OPC
scaling=3500.

def cartesian(R,theta):
    x=R*math.sin(math.radians(theta))
    y=R*math.cos(math.radians(theta))
    return x,y

def moon_create(R,theta):
    moon = 1494.45
    x,y=cartesian(R,theta)
    x=x/scaling
    y=y/scaling
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x, y, moon/scaling))
    #lines.append('{"line":[[%.2f, %.2f, %.2f], [%.2f, %.2f, %.2f]]}' % (x,y,height,x,y,0))


def three_planets_create(R,theta,phi):
    bottom_planet = 1010.11
    second_trio_planet = 2692.5
    b=1682.39
    R_1=math.sqrt(R**2 + (b/2)**2 - 2*R*(b/2)*math.cos(math.radians(180-phi)))
    theta_1=math.degrees(math.asin(b*math.sin(math.radians(180-phi))/(2*R_1)))
    theta_1=theta+theta_1
    R_2 = math.sqrt(R**2 + b**2 - 2*R*b*math.cos(math.radians(180 - phi)))
    theta_2 = math.degrees(math.asin(b * math.sin(math.radians(180 - phi)) /R_2))
    theta_2=theta+theta_2
    x,y=cartesian(R,theta)
    x=x/scaling
    y=y/scaling
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x, y, bottom_planet/scaling))
    x,y = cartesian(R_1, theta_1)
    x = x/scaling
    y = y/scaling
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x, y, second_trio_planet/scaling))
    x,y =cartesian(R_2,theta_2)
    x = x/scaling
    y = y/scaling
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x, y, bottom_planet/scaling))

def planet_create(R,theta):
    x,y=cartesian(R,theta)
    bottom_planet = 1010.11 #mm
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x/scaling,y/scaling,bottom_planet/scaling))

def dual_planet_screate(R,theta):
    x,y=cartesian(R,theta)
    bottom_planet = 1010.11  # mm
    top_duo_planet = 2420.13  # mm
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x/scaling,y/scaling,bottom_planet/scaling))
    lines.append('{"point": [%.2f, %.2f, %.2f]}' % (x/scaling,y/scaling,top_duo_planet/scaling))


## place the moons
### lines.append('  {"point": [%.2f, %.2f, %.2f]}' % (x, y, z))

lines = []
moon_create(6000,0)
moon_create(2000,300)
moon_create(6000,300)
moon_create(6000,225)
moon_create(6000,180)
moon_create(2000,140)
moon_create(6000,140)
moon_create(6000,80)
moon_create(2000,35)
moon_create(6000,35)

three_planets_create(4000,0,-60)
three_planets_create(4000,225,60)
three_planets_create(4000,140,-60)

##solo planets
planet_create(4000,180)
planet_create(4000,35)

## binary planet systems
dual_planet_screate(4000,300)
dual_planet_screate(4000,80)


print '[\n' + ',\n'.join(lines) + '\n]'
