$(function()
{
    var Particle = function(x, y, radius){
        this.x = x;
        this.y = y;
        this.prev_x = x;
        this.prev_y = y;
        this.acc_x = 0;
        this.acc_y = 0;
        this.radius = radius;
    }

    Particle.prototype = {
        accelerate: function(delta)
        {
            this.x += this.acc_x * Math.pow(delta,2);
            this.y += this.acc_y * Math.pow(delta,2);
            this.acc_x = 0;
            this.acc_y = 0;
        },
        equilibrium: function(delta)
        {
            var x = this.x*2 - this.prev_x;
            var y = this.y*2 - this.prev_y;
            this.prev_x = this.x;
            this.prev_y = this.y;
            this.x = x;
            this.y = y;
        },
        draw: function(ctx)
        {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2, false);
            ctx.fill();
        },
    }

    var Simulation = function(ctx)
    {
        var particles = this.particles = [];
        var width = ctx.canvas.width;
        var height = ctx.canvas.height;
        var damping = 0.98;
        var interval;

        while(particles.length < 60)
        {
            var particle = new Particle(
                Math.random() * (ctx.canvas.width-50) + 25,
                Math.random() * (ctx.canvas.height-50) + 25,
                Math.random() * 20 + 5
            );
            var collides = false;
            for(var i=0, l=particles.length; i<l; i++)
            {
                var other = particles[i];
                var x = other.x - particle.x;
                var y = other.y - particle.y;
                var length = Math.sqrt(x*x+y*y);
                if(length < other.radius + particle.radius)
                {
                    collides = true;
                    break;
                }
            }
            if(!collides)
            {
                particles.push(particle);
            }
        }
        
        var collide = function(preserve_impulse)
        {
            for(var i=0, l=particles.length; i<l; i++)
            {
                var particle1 = particles[i];
                for(var j=i+1; j<l; j++){
                    var particle2 = particles[j];
                    var x = particle1.x - particle2.x;
                    var y = particle1.y - particle2.y;
                    var slength = x*x+y*y;
                    var length = Math.sqrt(slength);
                    var target = particle1.radius + particle2.radius;

                    if(length < target)
                    {
                        var v1x = particle1.x - particle1.prev_x;
                        var v1y = particle1.y - particle1.prev_y;
                        var v2x = particle2.x - particle2.prev_x;
                        var v2y = particle2.y - particle2.prev_y;

                        var factor = (length-target)/length;
                        particle1.x -= x*factor*0.5;
                        particle1.y -= y*factor*0.5;
                        particle2.x += x*factor*0.5;
                        particle2.y += y*factor*0.5;

                        if(preserve_impulse)
                        {
                            var f1 = (damping*(x*v1x+y*v1y))/slength;
                            var f2 = (damping*(x*v2x+y*v2y))/slength;

                            v1x += f2*x-f1*x;
                            v2x += f1*x-f2*x;
                            v1y += f2*y-f1*y;
                            v2y += f1*y-f2*y;

                            particle1.prev_x = particle1.x - v1x;
                            particle1.prev_y = particle1.y - v1y;
                            particle2.prev_x = particle2.x - v2x;
                            particle2.prev_y = particle2.y - v2y;
                        }
                    }
                }
            }
        }

        var border_collide_preserve_impulse = function()
        {
            for(var i=0, l=particles.length; i<l; i++)
            {
                var particle = particles[i];
                var radius = particle.radius;
                var x = particle.x;
                var y = particle.y;

                if(x-radius < 0)
                {
                    var vx = (particle.prev_x - particle.x)*damping;
                    particle.x = radius;
                    particle.prev_x = particle.x - vx;
                }
                else if(x + radius > width){
                    var vx = (particle.prev_x - particle.x)*damping;
                    particle.x = width-radius;
                    particle.prev_x = particle.x - vx;
                }
                if(y-radius < 0)
                {
                    var vy = (particle.prev_y - particle.y)*damping;
                    particle.y = radius;
                    particle.prev_y = particle.y - vy;
                }
                else if(y + radius > height)
                {
                    var vy = (particle.prev_y - particle.y)*damping;
                    particle.y = height-radius;
                    particle.prev_y = particle.y - vy;
                }
            }
        }
        
        var border_collide = function()
        {
            for(var i=0, l=particles.length; i<l; i++)
            {
                var particle = particles[i];
                var radius = particle.radius;
                var x = particle.x;
                var y = particle.y;

                if(x-radius < 0)
                {
                    particle.x = radius;
                }
                else if(x + radius > width)
                {
                    particle.x = width-radius;
                }
                if(y-radius < 0)
                {
                    particle.y = radius;
                }
                else if(y + radius > height)
                {
                    particle.y = height-radius;
                }
            }
        }

        var draw = function()
        {
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillStyle = 'rgba(21, 214, 140, 1.0)';
            for(var i=0, l=particles.length; i<l; i++){
                particles[i].draw(ctx);
            }
        }

        var gravity = function()
        {
            for(var i=0, l=particles.length; i<l; i++)
            {
                particles[i].acc_y += 0.35;
            }
        }

        var accelerate = function(delta)
        {
            for(var i=0, l=particles.length; i<l; i++)
            {
                particles[i].accelerate(delta);
            }
        }
        
        var equilibrium = function(delta)
        {
            for(var i=0; i<particles.length; i++)
            {
                particles[i].equilibrium(delta);
            }
        }

        var step = function()
        {
            var steps = 2;
            var delta = 1/steps;
            for(var i=0; i<steps; i++)
            {
                gravity();
                accelerate(delta);
                collide(false);
                border_collide();
                equilibrium(delta);
                collide(true);
                border_collide_preserve_impulse();
            }
            draw();
        }

        this.start = function()
        {
            interval = setInterval(function()
            {
                step();
            }, 30);
        }

        this.stop = function()
        {
            if(interval)
            {
                clearInterval(interval);
                interval = null;
            }
        }

        draw();
    }
    var canvas = $('#canv')
        .click(function(event)
        {
            var offset = $(this).offset();
            var x = event.pageX - offset.left;
            var y = event.pageY - offset.top;
            simulation.particles.push(new Particle(
                x,
                y,
                Math.random() * 20 + 5
            ));
        })
        .hover()[0];

    $(document).ready(function() 
    {
        simulation.start();
    });

    var ctx = canvas.getContext('2d');
    var simulation = new Simulation(ctx);
});