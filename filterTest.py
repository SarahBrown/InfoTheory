from math import exp
import numpy as np
import time
import argparse
import scipy.stats
import random
from graphics import *
from filterBot import *
from filterGraphics import *
from Particle import *

# map variables
width = 123
height = 82
num_particles = 5000
map_lines = [(0,0,123,0),(123,0,123,82),(0,82,123,82),(0,0,0,82),(59,0,59,15),
         (59,15,64,15),(64,0,64,15),(59,41,59,82),(59,41,64,41),(64,41,64,82)]

drawn_things = list()

test_fake_data = False

# finds ultrasonic measurement for generated particles based on theta, x, and y
def find_ultrasonic_r(par_x, par_y, par_th):
    best_rval = 9999

    for x1,y1,x2,y2 in map_lines:
        if x1 == x2:
           cos_val = np.cos(par_th)

           if (cos_val == 0):
               continue
           r = (x1-par_x)/cos_val
           y_test = par_y + r*np.sin(par_th)

           if (r > 0 and y1 < y2 and y1 <= y_test and y_test <= y2): # checks bounds of map
               if (r < best_rval):
                   best_rval = r
                   continue

        else:
            sin_val = np.sin(par_th)

            if (sin_val == 0):
               continue

            r = (y1-par_y)/sin_val
            x_test = par_x + r*np.cos(par_th)

            if (r > 0 and x1 < x2 and x1 <= x_test and x_test <= x2): # checks bounds of map
               if (r < best_rval):
                   best_rval = r
                   continue

    return best_rval

# creates an uniformly distributed starting particle set
def create_uniform_particle_list(width_map, height_map, num_particles):
    particles = list()

    for i in range(num_particles):
        x = np.random.uniform(0, width_map)
        y = np.random.uniform(0, height_map)
        theta = np.random.uniform(0, 2*np.pi)
        weight = 1/num_particles
        particles.append(Particle(pos_x=x, pos_y=y, theta=theta, weight=weight))

    return particles

# function to recalc weights based on ultrasonic distance measurement
def recalc_weights(particles, ultrasonic):
    weight_total = 0
    weights = list()

    for par in particles:
        par_x = par.pos_x
        par_y = par.pos_y
        par_th = par.theta

        r = find_ultrasonic_r(par_x, par_y, par_th)
        par.r = r
        distance = np.abs(r-ultrasonic)
        
        # gaussian kernal to get a prob around the difference in measurements
        
        error = np.abs(ultrasonic-r)
        sigma2 = 0.9**2
        weight = exp((-error**2)/(2*sigma2))

        par.weight = weight
        weight_total += weight
    
    if weight_total == 0: # makes sure no divide by 0
        weight_total = 1e-8

    for par in particles:
        par.weight /= weight_total
        weights.append(par.weight)
    return weights

def predict(particles, rad_rot):
    for par in particles:
        par.theta += rad_rot + np.random.normal(0, rad_rot*.1) # adds random 10% error to movement

        while par.theta > 2*np.pi:
            par.theta = par.theta - 2*np.pi

        while par.theta < 0:
            par.theta = par.theta + 2*np.pi

def resample(particles, weights):
    num_par = len(particles)
    new_particles = random.choices(particles, weights, k=num_par)

    to_return = list()

    for par in new_particles:
        x = np.random.normal(par.pos_x, 2)
        y = np.random.normal(par.pos_y, 2)
        while (x < 0 or x > width or y < 0 or y > height):
            x = np.random.normal(par.pos_x, 2)
            y = np.random.normal(par.pos_y, 2)
        
        theta = np.random.normal(par.theta, 0.3)
        to_return.append(Particle(pos_x=x, pos_y=y, theta=theta, weight=1/num_par))

    return to_return

# init graphics window and add map to it
win = GraphWin("PartBot",1024,768, autoflush = False)
win.setCoords(-10,-10,133,92)
draw_map_lines(win, map_lines)

if not test_fake_data:
    soc = connect()

# create starting uniform particles list
particles = create_uniform_particle_list(width, height, num_particles)
draw_particles(win, particles, drawn_things)

loop_thru_steps = True

while(loop_thru_steps):
    # take a reading
    if not test_fake_data:
        ultrasonic = read_sensor(soc, b'p')
    else:
        ultrasonic = 8 # fake ultrasonic to test parts
    ultrasonic = ultrasonic + 7 # adds 7 cms to reading to hit center of bot

    # update weights
    weights = recalc_weights(particles, ultrasonic)

    # using simplified model of movement in circle with 8cm radius with bot modeled as a point
    # predict step by updating movement
    rotate_ticks = 1 # rotate the robot to the right a number of ticks
    for i in range(rotate_ticks):
        if not test_fake_data:
            soc.sendall(b'd')
            time.sleep(0.5)

    rad_rot = (np.pi/30)*rotate_ticks
    predict(particles, rad_rot)


    #resample
    particles = resample(particles, weights)
    clear_particles(win, drawn_things)
    draw_particles(win, particles, drawn_things)
    update()

win.getMouse()
win.close()