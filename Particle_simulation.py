import pygame
import random
import numpy as np
import operator
from itertools import combinations

class Particle:
    def __init__(self):
        self.mass = 10
        self.radius = random.randint(10, 50) 
        self.width, self.height = 700, 500
        self.pos = np.array((self.width/2, self.height/2))
        self.v = np.array((0.0, 0.0)) 
        self.acc = np.array((0.0, 0.0))
        self.bounce = 0.95
    
class Simulation:
    def __init__(self):
        self.screen = None
        self.dim = self.width, self.height = 700, 500
        self.fps = 120
        self.dt = 0.08
        self.drag = 0.1
        self.ball_list = []
        self.tol = 5
    
    def update(self, ball, dt):
        new_pos = np.array((ball.pos[0] + ball.v[0]*dt + ball.acc[0]*(dt*dt*0.5), ball.pos[1] + ball.v[1]*dt + ball.acc[1]*(dt*dt*0.5)))
        new_acc = np.array((self.apply_forces(ball))) # only needed if acceleration is not constant
        new_v = np.array((ball.v[0] + (ball.acc[0]+new_acc[0])*(dt*0.5), ball.v[1] + (ball.acc[1]+new_acc[1])*(dt*0.5)))
        ball.pos = new_pos;
        ball.v = new_v;
        ball.acc = new_acc;
   
    def apply_forces(self, ball):
        grav_acc = [0.0, 9.81]
        drag_force = [0.5 * self.drag * (ball.v[0] * abs(ball.v[0])), 0.5 * self.drag * (ball.v[1] * abs(ball.v[1]))]  #D = 0.5 * (rho * C * Area * vel^2)
        drag_acc = [drag_force[0] / ball.mass, drag_force[1] / ball.mass] # a = F/m

        return (-drag_acc[0]),(grav_acc[1] - drag_acc[1])
        
    def make_ball(self):
        ball = Particle()

        return ball

    def init(self):
        pygame.init()
        pygame.display.set_caption("Bouncing Ball")

        self.screen = pygame.display.set_mode(self.dim)
        self.isRunning = True
        self.screen.fill((255,255,255))

        self.clock = pygame.time.Clock()

        self.ball_list = []
        ball = self.make_ball()
        self.ball_list.append(ball)

        for ball in self.ball_list:
            ball.pos[0] += ball.v[0]
            ball.pos[1] += ball.v[1]

    def event(self, event):
        if event.type == pygame.QUIT:
            self.isRunning = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            ball = self.make_ball()
            ball.pos[0] = pos[0]
            ball.pos[1] = pos[1]
            self.ball_list.append(ball)
    
    def collision(self):
        pairs = combinations(range(len(self.ball_list)), 2)

        for i,j in pairs:
            part1 = self.ball_list[i]
            part2 = self.ball_list[j]
            distance = list(map(operator.sub, self.ball_list[i].pos, self.ball_list[j].pos))

            if np.hypot(*distance) < self.ball_list[i].radius + self.ball_list[j].radius:
                distance = part1.pos - part2.pos
                rad = part1.radius + part2.radius
                slength = (part1.pos[0] - part2.pos[0])**2 + (part1.pos[1] - part2.pos[1])**2
                length = np.hypot(*distance)
                factor = (length-rad)/length;
                x = part1.pos[0] - part2.pos[0]
                y = part1.pos[1] - part2.pos[1]

                part1.pos[0] -= x*factor*0.5
                part1.pos[1] -= y*factor*0.5
                part2.pos[0] += x*factor*0.5
                part2.pos[1] += y*factor*0.5

                u1 = (part1.bounce*(x*part1.v[0]+y*part1.v[1]))/slength
                u2 = (part2.bounce*(x*part2.v[0]+y*part2.v[1]))/slength
                part1.v[0] = u2*x-u1*x
                part1.v[1] = u1*x-u2*x
                part2.v[0] = u2*y-u1*y
                part2.v[1] = u1*y-u2*y

    def check_boundaries(self, ball):
        if ball.pos[0] + ball.radius > self.width:
            ball.v[0] *= -ball.bounce
            ball.pos[0] = self.width - ball.radius
                
        if ball.pos[0] < ball.radius:
            ball.v[0] *= -ball.bounce
            ball.pos[0] = ball.radius
                
        if ball.pos[1] + ball.radius > self.height:
            self.friction = True
            ball.v[1] *= -ball.bounce
            ball.pos[1] = self.height - ball.radius

        elif ball.pos[1] < ball.radius:
            ball.v[1] *= -ball.bounce
            ball.pos[1] = ball.radius

    def loop(self):
        self.collision()

        for ball in self.ball_list:
            self.check_boundaries(ball)
            self.update(ball, self.dt)

    def draw(self):
        self.screen.fill((255,255,255))

        for ball in self.ball_list:
            pygame.draw.circle(self.screen, (0,0,100), [ball.pos[0], ball.pos[1]], ball.radius)

        pygame.display.update()

    def execute(self):
        if self.init() == False:
            self.isRunning = False

        while self.isRunning:
            for event in pygame.event.get():
                self.event(event)

            self.loop()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()

if __name__ == "__main__":
    np.seterr(over='raise')
    p = Simulation()
    p.execute()