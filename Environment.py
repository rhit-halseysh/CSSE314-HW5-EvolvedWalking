import math
import pygame
import pymunk
import pymunk.pygame_util
import neat
import sys
import os

#Inspiration drawn from https://github.com/monokim/PyWalk/tree/master


friction = 0.9
body_friction = 0.5
space = pymunk.Space()
space.gravity = (0.0, 900.0) # -900
generation = 0
lower_x_bound = 200
upper_x_bound = 400


class Walker(object):
    

    def __init__(self) -> None:
        
        self.time_alive = 0
        
        # BODY SET-UP
        moment = 5
        
        # Define the thigh
        thigh_size = (20, 40)
        self.thigh_shape = pymunk.Poly.create_box(None, thigh_size)
        thigh_moment = pymunk.moment_for_poly(moment, self.thigh_shape.get_vertices())
        self.thigh_body = pymunk.Body(moment, thigh_moment)

        # Set the thigh position as the base
        self.thigh_body.position = (300, 450)
        self.thigh_shape.body = self.thigh_body
        self.thigh_shape.friction = body_friction

        # Define the top
        top_moment = pymunk.moment_for_circle(moment, 0, 30)
        self.body = pymunk.Body(moment, top_moment)
        self.shape = pymunk.Circle(None, 15)

        # Set the top position directly relative to the thigh part
        self.body.position = (self.thigh_body.position.x, self.thigh_body.position.y + thigh_size[1] / 2 - 50)
        self.shape.body = self.body
        
        # Give top a push to start it off
        self.body.apply_impulse_at_local_point((100, 0))

        # Create a joint to directly connect the thigh to the top
        self.thigh_joint = pymunk.PivotJoint(self.thigh_body, self.body, (0, thigh_size[1] / 2), (0, 0))
        self.thigh_motor = pymunk.SimpleMotor(self.thigh_body, self.body, 0)

        # Define the leg
        leg_size = (10, 50)
        self.leg_shape = pymunk.Poly.create_box(None, leg_size)
        leg_moment = pymunk.moment_for_poly(moment, self.leg_shape.get_vertices())
        self.leg_body = pymunk.Body(moment, leg_moment)

        # Set the leg position directly relative to the thigh
        self.leg_body.position = (self.thigh_body.position.x, self.thigh_body.position.y - thigh_size[1] / 2 - leg_size[1] / 2)
        self.leg_shape.body = self.leg_body
        self.leg_shape.friction = body_friction

        # Create a joint to connect the leg to the thigh
        self.leg_joint = pymunk.PivotJoint(self.leg_body, self.thigh_body, (0, leg_size[1] / 2), (0, -thigh_size[1] / 2))
        self.leg_motor = pymunk.SimpleMotor(self.thigh_body, self.leg_body, 0)

        # Define the foot
        foot_size = (35, 15)
        self.foot_shape = pymunk.Poly.create_box(None, foot_size)
        foot_moment = pymunk.moment_for_poly(moment, self.foot_shape.get_vertices())
        self.foot_body = pymunk.Body(moment, foot_moment)

        # Set the foot position relative to the leg
        self.foot_body.position = (self.leg_body.position.x, self.leg_body.position.y - leg_size[1] / 2 - foot_size[1] / 2)
        self.foot_shape.body = self.foot_body
        self.foot_shape.friction = body_friction
        self.foot_shape.mass = 30

        # Create a joint to connect the foot to the leg
        self.foot_joint = pymunk.PivotJoint(self.leg_body, self.foot_body, (0, -leg_size[1] / 2), (0, foot_size[1] / 2))
        self.foot_motor = pymunk.SimpleMotor(self.leg_body, self.foot_body, 0)

        # Add the joints and shapes to the space
        space.add(self.thigh_shape, self.thigh_body, self.shape, self.body, self.thigh_joint, self.thigh_motor, 
                  self.leg_shape, self.leg_body, self.leg_joint, self.leg_motor, 
                  self.foot_shape, self.foot_body, self.foot_joint, self.foot_motor)

        
        # Deal with body collisions
        
        shape_filter = pymunk.ShapeFilter(group=1)
        self.shape.filter = shape_filter
        self.thigh_shape.filter = shape_filter
        self.leg_shape.filter = shape_filter
        self.foot_shape.filter = shape_filter
        
        self.is_done = False
        self.distance = 0
        
        self.thigh_flag = False
        self.leg_flag = False
        self.foot_flag = False
        
    def get_data(self):
        thigh = ((360 - math.degrees(self.thigh_body.angle)) - (360 - math.degrees(self.body.angle))) / 360.0
        leg = ((360 - math.degrees(self.leg_body.angle)) - (360 - math.degrees(self.body.angle))) / 360.0
        foot = ((360 - math.degrees(self.foot_body.angle)) - (360 - math.degrees(self.body.angle))) / 360.0
        return self.body.angle, thigh, leg, foot
    
    def remove_shapes(self):
        
        space.remove(self.body)
        space.remove(self.shape)
        space.remove(self.thigh_body)
        space.remove(self.thigh_shape)
        space.remove(self.thigh_joint)
        space.remove(self.thigh_motor)
        
        space.remove(self.leg_body)
        space.remove(self.leg_shape)
        space.remove(self.leg_joint)
        space.remove(self.leg_motor)
        
        space.remove(self.foot_body)
        space.remove(self.foot_shape)
        space.remove(self.foot_joint)
        space.remove(self.foot_motor)
    
    def update(self):
        
        self.time_alive += 1
        
        # Thigh
        self.thigh_flag = False
        if (360 - math.degrees(self.thigh_body.angle)) - (360 - math.degrees(self.body.angle)) >= 70 and self.thigh_motor.rate > 0:
            self.thigh_motor.rate = 0
            self.thigh_flag = True
        elif (360 - math.degrees(self.thigh_body.angle)) - (360 - math.degrees(self.body.angle)) <= -70 and self.thigh_motor.rate < 0:
            self.thigh_motor.rate = 0
            self.thigh_flag = True

        # Leg
        self.leg_flag = False
        if (360 - math.degrees(self.leg_body.angle)) - (360 - math.degrees(self.thigh_body.angle)) >= 90 and self.leg_motor.rate > 0:
            self.leg_motor.rate = 0
            self.leg_flag = True
        elif (360 - math.degrees(self.leg_body.angle)) - (360 - math.degrees(self.thigh_body.angle)) <= 0 and self.leg_motor.rate < 0:
            self.leg_motor.rate = 0
            self.leg_flag = True

        # Foot
        self.foot_flag = False
        if (360 - math.degrees(self.foot_body.angle)) - (360 - math.degrees(self.thigh_body.angle)) >= 30 and self.foot_motor.rate > 0:
            self.foot_motor.rate = 0
            self.foot_flag = True
        elif (360 - math.degrees(self.foot_body.angle)) - (360 - math.degrees(self.thigh_body.angle)) <= -45 and self.foot_motor.rate < 0:
            self.foot_motor.rate = 0
            self.foot_flag = True

        #TODO: Change these constants
        if (self.time_alive > 500 and lower_x_bound <= self.body.position.x <= upper_x_bound) or self.body.position.y > 550 or self.body.position.x > 800:
        #(self.time_alive > 500 and lower_x_bound <= self.body.position.x <= upper_x_bound) or 
            self.is_done = True
            self.remove_shapes()
            #space.remove(self.get_shapes())
        
    
def add_scenery():
    
    shape = pymunk.Poly.create_box(None, (800, 10))
    shape.friction = 0.5
    shape.elasticity = 1.0
    moment = pymunk.moment_for_poly(1, shape.get_vertices())
    body = pymunk.Body(9999, moment, body_type=pymunk.Body.KINEMATIC)
    body.position = (600, 500)
    shape.body = body
    space.add(body, shape)

    return shape
        
def run_walker(genomes, config):

        # Physics
        # Time step
        dt = 1.0 / 50.0
        # Number of physics steps per screen frame

        # pygame
        pygame.init()
        screen = pygame.display.set_mode((1000, 800))
        clock = pygame.time.Clock()
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        
        font = pygame.font.SysFont("DejaVu Sans", 50)

        # Floor
        floor = add_scenery()
        floor.surface_velocity = (-25, 0)

        ruler = 0
        nets = []
        walkers = []

        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            walkers.append(Walker())
            g.fitness = 0
            
        global generation
        generation += 1
        tick = 0
        speed_up = 1

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    cursor_position = pygame.mouse.get_pos()
                    print(f"Cursor position: {cursor_position}")

            for i, walker in enumerate(walkers):
                output = nets[i].activate(walker.get_data())
                speed = 3
                for i, out in enumerate(output):
                    if out > 0.9:
                        if i == 0 and walker.thigh_flag == False:
                            walker.thigh_motor.rate = speed
                        elif i == 1 and walker.thigh_flag == False:
                            walker.thigh_motor.rate = -speed
                        elif i == 2 and walker.leg_flag == False:
                            walker.leg_motor.rate = speed
                        elif i == 3 and walker.leg_flag == False:
                            walker.leg_motor.rate = -speed
                        elif i == 4 and walker.foot_flag == False:
                            walker.foot_motor.rate = speed
                        elif i == 5 and walker.foot_flag == False:
                            walker.foot_motor.rate = -speed

            max = 0
            at = 0
            remain_walker = 0
            for i, walker in enumerate(walkers):
                if not walker.is_done:
                    remain_walker += 1
                    walker.update()
                    genomes[i][1].fitness += 0.1
                    distance = walker.body.position.x
                    if distance > walker.distance:
                        genomes[i][1].fitness += 0.1
                    walker.distance = distance
                    if walker.body.position.x > max:
                        max = walker.body.position.x
                        at = i


            if remain_walker == 0:
                break

            ruler -= (speed_up+1)

            tick += 1
            if tick == 600:
                floor.surface_velocity = (-15 * speed_up, 0)
                speed_up += 1
                tick = 0

            space.step(dt)
            screen.fill((255, 255, 255))
            space.debug_draw(draw_options)

            text = font.render("Generation : " + str(generation), True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (1000/2, 100)
            screen.blit(text, text_rect)

            for i in range(ruler, 1700, 100):
                pygame.draw.line(screen, (0, 0, 0), (i, 100 - 300), (i, 800 - 290))

            if ruler < 450:
                ruler = 550

            for i, walker in enumerate(walkers):
                if not walker.is_done:
                    walker.thigh_motor.rate = 0
                    walker.leg_motor.rate = 0
                    walker.foot_motor.rate = 0


            pygame.display.flip()
            clock.tick(60)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    generation = 0
    winner = p.run(run_walker, 1000)

def main():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)


if __name__ == "__main__":
    main()