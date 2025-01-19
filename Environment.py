import math
import pygame
import pymunk
import pymunk.pygame_util
import neat
import sys
import os


friction = 0.9
body_friction = 0.5
space = pymunk.Space()
space.gravity = (0.0, 900.0) # -900
generation = 0


class Walker(object):

    def __init__(self) -> None:
        
        # BODY SET-UP
        moment = 5
        
        # Top
        
        top_moment = pymunk.moment_for_circle(moment, 0, 30)
        self.body = pymunk.Body(moment, top_moment)
        self.shape = pymunk.Circle(None, 15)
        self.body.position = (100, 500)
        self.shape.body = self.body
        
        # Thigh
        
        thigh_size = (20, 40)
        self.thigh_shape = pymunk.Poly.create_box(None, thigh_size)
        thigh_moment = pymunk.moment_for_poly(moment, self.thigh_shape.get_vertices())
        self.thigh_body = pymunk.Body(moment, thigh_moment)
        self.thigh_body.position = (self.body.position.x-20, self.body.position.y-40)
        self.thigh_shape.body = self.thigh_body
        self.thigh_shape.friction = body_friction
        self.thigh_joint = pymunk.PivotJoint(self.thigh_body, self.body, (0, thigh_size[1] / 2), (-20, -50))
        self.thigh_motor = pymunk.SimpleMotor(self.body, self.thigh_body, 0)
        
        # Leg
        
        leg_size = (10, 50)
        self.leg_shape = pymunk.Poly.create_box(None, leg_size)
        leg_moment = pymunk.moment_for_poly(moment, self.leg_shape.get_vertices())
        self.leg_body = pymunk.Body(moment, leg_moment)
        self.leg_body.position = (self.thigh_body.position.x, self.thigh_body.position.y - 100)
        self.leg_shape.body = self.leg_body
        self.leg_shape.friction = body_friction
        self.leg_joint = pymunk.PivotJoint(self.leg_body, self.thigh_body, (0, leg_size[1] / 2), (0, -thigh_size[1] / 2))
        self.leg_motor = pymunk.SimpleMotor(self.thigh_body, self.leg_body, 0)
        
        # Foot
        
        foot_size = (35, 15)
        self.foot_shape = pymunk.Poly.create_box(None, foot_size)
        foot_moment = pymunk.moment_for_poly(moment, self.foot_shape.get_vertices())
        self.foot_body = pymunk.Body(moment, foot_moment)
        self.foot_body.position = (self.leg_body.position.x + foot_size[0]/2, self.leg_body.position.y + (foot_size[1]/2 + leg_size[1]/2))
        self.foot_shape.body = self.foot_body
        self.foot_shape.friction = body_friction
        self.foot_shape.mass = 30
        self.foot_joint = pymunk.PivotJoint(self.leg_body, self.foot_body, (-5, -leg_size[1] / 2), (-foot_size[0]/2 + 10, foot_size[1]/2))
        self.foot_motor = pymunk.SimpleMotor(self.leg_body, self.foot_body, 0)
        
        # Add components to Space
        
        space.add(self.body, self.shape)
        space.add(self.thigh_body, self.thigh_shape, self.thigh_joint, self.thigh_motor)
        space.add(self.leg_body, self.leg_shape, self.leg_joint, self.leg_motor)
        space.add(self.foot_body, self.foot_shape, self.foot_joint, self.foot_motor)
        
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
    
    def get_shapes(self):
        body = self.body, self.shape
        thigh = self.thigh_body, self.thigh_shape, self.thigh_joint, self.thigh_motor
        leg = self.leg_body, self.leg_shape, self.leg_joint, self.leg_motor
        foot = self.foot_body, self.foot_shape, self.foot_joint, self.foot_motor

        return body, thigh, leg, foot
    
    def set_color(self, color, rest_color = (0, 0, 255), shoe_color = (50, 50, 50)):
        self.shape.color = color
        self.thigh_shape.color = rest_color
        self.leg_shape.color = rest_color
        self.foot_shape.color = shoe_color
    
    def update(self):
        
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

        #self.body.position.y <= 100 or
        #TODO: Change these constants
        if (self.body.position.x > 800 and self.body.position.y <= 800):
            self.is_done = True
            space.remove(self.get_shapes())

    def _process_events(self) -> None:
        """
        Handle game and events like keyboard input. Call once per frame only.
        :return: None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pygame.image.save(self._screen, "bouncing_balls.png")

    def _clear_screen(self) -> None:
        """
        Clears the screen.
        :return: None
        """
        self._screen.fill(pygame.Color("white"))

    def _draw_objects(self) -> None:
        """
        Draw the objects.
        :return: None
        """
        space.debug_draw(self._draw_options)
        
    
def add_static_scenery():

        static_body = space.static_body
        static_lines = [
            pymunk.Segment(static_body, (0, 600 - 100), (1000, 600 - 100), 10.0),
        ]
        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
        space.add(*static_lines)
        
def run_walker(genomes, config):

        # Physics
        # Time step
        dt = 1.0 / 50.0
        # Number of physics steps per screen frame
        physics_steps_per_frame = 1
        #font = pygame.font.SysFont("Arial", 30)

        # pygame
        pygame.init()
        screen = pygame.display.set_mode((1000, 800))
        clock = pygame.time.Clock()
        draw_options = pymunk.pygame_util.DrawOptions(screen)

        # Floor
        add_static_scenery()

        # Execution control 
        running = True

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

            # check
            max = 0
            at = 0
            remain_walker = 0
            for i, walker in enumerate(walkers):
                if not walker.is_done:
                    remain_walker += 1
                    walker.update()
                  #  walker.set_color((240, 240, 240), (240, 240, 240), (240, 240, 240))
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

          #  walkers[at].set_color((255, 0, 0))
            walker_position = walkers[at].body.position
            ruler -= (speed_up+1)

            tick += 1
            if tick == 600:
               # land.surface_velocity = (-100 * speed_up, 0)
                speed_up += 1
                tick = 0

            space.step(dt)
            screen.fill((255, 255, 255))
           # screen.blit(foundry, (0, screen_height - 300))
            space.debug_draw(draw_options)
            #walkers[at].draw_face(screen)

            #text = font.render("Generation : " + str(generation), True, (0, 0, 0))
           # text_rect = text.get_rect()
           # text_rect.center = (1000/2, 100)
            #screen.blit(text, text_rect)

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