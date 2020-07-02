import math
import random
import time

import pyglet
from pyglet.window import key

WIDTH, HEIGTH = 800, 600
N_BALL = 100

red_ball_image = pyglet.image.load("red_ball.png")
red_ball_image.anchor_x = red_ball_image.width // 2
red_ball_image.anchor_y = red_ball_image.height // 2

blue_ball_image = pyglet.image.load("blue_ball.png")
blue_ball_image.anchor_x = blue_ball_image.width // 2
blue_ball_image.anchor_y = blue_ball_image.height // 2


class RandomBall(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x_speed = random.choice([-0.5, 0.5])
        self.y_speed = random.choice([-0.5, 0.5])

        self.time_change = random.uniform(0.0, 1.0)
        # self.time_change = random.lognormvariate(1, 1)
        self.update_time = 0
        self.current_time = 0
        self.collision_count = 0
        self.decay = 0.4

    def update(self, dt, other_ball):
        self.wall_collision()
        self.process_random_move(dt)

        self.process_collisions(other_ball)
        self.x += self.x_speed
        self.y += self.y_speed

    def process_random_move(self, dt):
        self.current_time += dt
        random_move = (self.current_time - self.update_time) > self.time_change
        self.update_time = (
            self.current_time if random_move else self.update_time
        )
        if random_move:
            self.random_speed()
            self.scale = random.choices(
                [1, 0.25, 1.50, 2], weights=[1000, 3, 5, 3]
            )[0]

    def wall_collision(self):
        # Hitting right side
        if ((self.x + (self.width / 2)) >= WIDTH) or (
            (self.x - (self.width / 2)) <= 0
        ):
            self.x_speed *= -1 * self.decay
            self.x += self.x_speed * (1 / self.decay)
        # Hitting top of screen
        if ((self.y + (self.height / 2)) >= HEIGTH) or (
            (self.y - (self.height / 2)) <= 0
        ):
            self.y_speed *= -1 * self.decay
            self.y += self.y_speed * (1 / self.decay)

    def random_speed(self):
        self.x_speed += random.normalvariate(0, 0.1)
        self.y_speed += random.normalvariate(0, 0.1)

    @staticmethod
    def distance(point1, point2):
        return math.sqrt(
            ((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2)
        )

    def ball_collide(self, other_ball):
        # Hitting from left
        min_distance = (self.width / 2) + (other_ball.width / 2)
        return min_distance >= self.distance(self.position, other_ball.position)

    def process_collisions(self, other_ball):
        if self.ball_collide(other_ball):
            self.collision_count += 1
            self.x_speed = (-1 * self.x_speed) + other_ball.x_speed
            self.y_speed = (-1 * self.y_speed) + other_ball.y_speed
            self.x += self.x_speed
            self.y += self.y_speed


class ColliderBall(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.x_speed = 0
        self.y_speed = 0

    def update(self):
        self.x += self.x_speed
        self.y += self.y_speed


class Window(pyglet.window.Window):
    def __init__(self, random_balls=100, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.batch = pyglet.graphics.Batch()

        self.random_balls = random_balls
        self.ball_sprites = []
        self.fill_ball_list()

        self.collider_ball = ColliderBall(
            img=blue_ball_image, x=100, y=100, batch=self.batch
        )

        self.set_exclusive_mouse(True)
        pyglet.clock.schedule_interval(self.update, 1 / 120)

    def fill_ball_list(self):
        for i in range(self.random_balls):
            x, y = (
                random.normalvariate(self.width // 2, 50),
                random.normalvariate(self.height // 2, 50),
            )
            self.ball_sprites.append(
                RandomBall(red_ball_image, x, y, batch=self.batch)
            )

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, dt):
        self.collider_ball.update()
        for b in self.ball_sprites:
            b.update(dt=dt, other_ball=self.collider_ball)
        self.collider_ball.x_speed = 0
        self.collider_ball.y_speed = 0

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            for b in self.ball_sprites:
                b.x_speed = 0
                b.y_speed = 0
        if symbol == key.ESCAPE:
            self.close()

    def on_mouse_motion(self, x, y, dx, dy):
        self.collider_ball.x_speed = dx
        self.collider_ball.y_speed = dy


if __name__ == "__main__":
    window = Window(
        random_balls=N_BALL,
        width=WIDTH,
        height=HEIGTH,
        caption="Collider Ball!",
    )
    pyglet.app.run()
