from graphics import *
from Particle import *
import numpy as np

width = 123
height = 82

def draw_particles(win, particles, drawn_things):
    for par in particles:
        par_x = par.pos_x
        par_y = par.pos_y
        par_th = par.theta
        par_w = par.weight

        # particles
        if (par_w * len(particles) == 1): # uniform sample so all same size particle
            c = Circle(Point(par_x, par_y), 1)

        else:
            c = Circle(Point(par_x, par_y), par_w*5) # multiples by 5 to show new weight distribution
        
        if (par_x < 0 or par_x > width or par_y < 0 or par_y > height):
            continue

        c.draw(win)
        drawn_things.append(c)

        # lines indicating theta direction
        theta_line = Line(Point(par_x,par_y), Point((par_x + 2*np.cos(par_th)), (par_y + 2*np.sin(par_th))))
        theta_line.draw(win)
        drawn_things.append(theta_line)

def clear_particles(win, drawn_things):
    for drawn in drawn_things:
        drawn.undraw()

    drawn_things.clear()

def draw_map_lines(win, map_lines):
    for x1,y1,x2,y2 in map_lines:
        l = Line(Point(x1,y1),Point(x2,y2))
        l.setWidth(3)
        l.draw(win)