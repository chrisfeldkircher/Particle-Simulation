import pygame
import pygame.gfxdraw
import random
import numpy as np
import operator
from itertools import combinations

class Particle:
    def __init__(self, func):
        self.mass = 10
        self.radius = 10 
        self.width, self.height = 700, 500
        #self.pos = np.array((random.randrange(self.radius, self.width - self.radius), random.randrange(self.radius, self.height - self.radius)))
        self.pos = np.array((self.width/2, self.height/2))
        #self._v = np.array(((random.randint(-4, 4), (random.randint(-4, 4)))))
        self._v = np.array((0.0, 0.0)) 
        self.acc = np.array((0.0, 0.0))
        self.bounce = 0.95
        self.func = func
        self.coll = True
    
    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, value):
        self.func()
        self._v = value
    
class Simulation:
    def __init__(self):
        self.screen = None
        self.dim = self.width, self.height = 700, 500
        self.dt = 0.05
        #self.Area = np.pi * self.radius**2
        #self.rho = 1.225 #density of air
        #self.C = 0.47 # drag coeff sphere
        #self.drag = 0.5 * (self.rho * self.C * self.Area * self.v[1]**2) #A = Cross-sectional Area, rho = density, C = drag coefficient
        self.drag = 0.2
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
        #print("Velocity_x: {}\n Velocity_y: {}\n".format(ball.v[0], ball.v[1])) 
        drag_force = [0.5 * self.drag * (ball.v[0] * abs(ball.v[0])), 0.5 * self.drag * (ball.v[1] * abs(ball.v[1]))]  #D = 0.5 * (rho * C * Area * vel^2)
        drag_acc = [drag_force[0] / ball.mass, drag_force[1] / ball.mass] # a = F/m
        return (grav_acc[0] - drag_acc[0]),(grav_acc[1] - drag_acc[1])

    def make_ball(self, func):
        ball = Particle(func)
        #ball.pos[0] = random.randrange(ball.radius, self.width - ball.radius) + ball.v[0]
        #ball.pos[1] = random.randrange(ball.radius, self.height - ball.radius) + ball.v[1]
        ball.pos = np.array((self.width/2, self.height/2))
 
        return ball

    def energy(self):
        e_kin = 0
        e_pot = 0
        #print(self.ball_list[0].v)
        """
        for i in range(len(self.ball_list)):
            e_kin += 1/2 * self.ball_list[i].mass * np.linalg.norm(self.ball_list[i].v)**2
            e_pot += self.ball_list[i].mass * 9.81 * (self.height - self.ball_list[i].pos[1] - self.ball_list[i].radius)
        print("{}xBalls = Energy: {}".format(len(self.ball_list),e_kin))
        """
        
        #pass

    def init(self):
        pygame.init()
        pygame.display.set_caption("Bouncing Ball")

        self.screen = pygame.display.set_mode(self.dim)
        self.isRunning = True
        self.screen.fill((255,255,255))

        self.clock = pygame.time.Clock()

        self.ball_list = []
        ball = self.make_ball(self.energy)
        self.ball_list.append(ball)

        for ball in self.ball_list:
            ball.pos[0] += ball.v[0]
            ball.pos[1] += ball.v[1]

    def event(self, event):
        if event.type == pygame.QUIT:
            self.isRunning = False
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            ball = self.make_ball(self.energy)
            ball.pos[0] = pos[0]
            ball.pos[1] = pos[1]
            self.ball_list.append(ball)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ball = self.make_ball(self.energy)
                self.ball_list.append(ball)
    
    def collsion(self, part1, part2):
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

        if  part1.coll and part2.coll:
            u1 = (part1.bounce*(x*part1.v[0]+y*part1.v[1]))/slength
            u2 = (part2.bounce*(x*part2.v[0]+y*part2.v[1]))/slength
            part1.v[0] = u2*x-u1*x
            part1.v[1] = u1*x-u2*x
            part2.v[0] = u2*y-u1*y
            part2.v[1] = u1*y-u2*y

        """
        diff1 = list(map(operator.sub, part1.v, part2.v))
        diff12 = list(map(operator.sub, part1.pos, part2.pos))
        term1 = -2*part1.mass/M
        term12 = np.dot(diff1, diff12)/np.linalg.norm(diff12)**2
        term13 = [term12 * i for i in diff12]
        term14 = [term1*term12 * i for i in term13]

        diff2 = list(map(operator.sub, part2.v, part1.v))
        diff22 = list(map(operator.sub, part2.pos, part1.pos))
        term2 = -2*part2.mass/M
        term22 = np.dot(diff2, diff22)/np.linalg.norm(diff22)**2
        term23 = [term22 * i for i in diff22]
        term24 = [term2*term22 * i for i in term23]

        t1 = list(map(operator.sub, part1.v, term14))
        u1 = [part1.bounce * i for i in t1] 
        t2 = list(map(operator.sub, part2.v, term24))
        u2 = [part2.bounce * i for i in t2]
        
        part1.v = u1
        part2.v = u2
        """

    def check_boundaries(self, ball):
        """
        if ball.pos[1] > self.height - ball.radius or ball.pos[1] < ball.radius:
            ball.v[1] *= -ball.bounce
        if ball.pos[0] > self.width - ball.radius or ball.pos[0] < ball.radius:
            ball.v[0] *= -ball.bounce
        """

        if ball.pos[0] + ball.radius > self.width:
            ball.v[0] *= -ball.bounce
            ball.pos[0] = self.width - ball.radius
                
        if ball.pos[0] < ball.radius:
            ball.v[0] *= -ball.bounce
            ball.pos[0] = ball.radius
                
        if ball.pos[1] + ball.radius > self.height:
            ball.v[1] *= -ball.bounce
            ball.pos[1] = self.height - ball.radius

        elif ball.pos[1] < ball.radius:
            ball.v[1] *= -ball.bounce
            ball.pos[1] = ball.radius

    def loop(self):
        pairs = combinations(range(len(self.ball_list)), 2)
        for i,j in pairs:
            distance = list(map(operator.sub, self.ball_list[i].pos, self.ball_list[j].pos))
            if np.hypot(*distance) < self.ball_list[i].radius + self.ball_list[j].radius: #* unpacks the list items as individual arguments for func call
                self.collsion(self.ball_list[i], self.ball_list[j])

        for ball in self.ball_list:
            self.check_boundaries(ball)
            self.update(ball, self.dt)
            e_pot = ball.mass * 9.81 * (self.height - ball.pos[1] - ball.radius)
            e_kin = 1/2 * ball.mass * np.linalg.norm(ball.v)**2
            if abs(e_kin - e_pot) < self.tol:
                #ball.coll = False
                ball.v[0] = 0
                ball.v[1] = 0
            #ball.pos[0] += ball.v[0]
            #ball.pos[1] += ball.v[1]

    def draw(self):
        self.screen.fill((255,255,255))

        for ball in self.ball_list:
            pygame.draw.circle(self.screen, (0,0,100), [ball.pos[0], ball.pos[1]], ball.radius)
            #pygame.gfxdraw.filled_circle(self.screen, int(ball.pos[0]), int(ball.pos[1]), int(ball.radius), (100,0,100))

        pygame.display.update()

    def execute(self):
        if self.init() == False:
            self.isRunning = False

        while self.isRunning:
            for event in pygame.event.get():
                self.event(event)

            self.loop()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    np.seterr(over='raise')
    p = Simulation()
    p.execute()
