import kivy
kivy.require('1.1.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger

import math

def clamp(min_val, max_val, value):
    return max(min_val, min(max_val, value))

def clamp_iter(min_val, max_val, iter):
    return [clamp(min_val, max_val, val) for val in iter]

class PongPaddle(Widget):
    score = NumericProperty(0)
    velocity = NumericProperty(0)
    target_pos = NumericProperty(-1)

    # Larger this is, slower bat gets
    speed = NumericProperty(4)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y-self.center_y)/(self.height/2)
            bounced = Vector(-1*vx, vy)
            vel = bounced * 1.05
            max_velocity = self.width
            ball.velocity = clamp_iter(-max_velocity, max_velocity, (vel.x, vel.y + offset))

    def update(self):
        if abs(self.center_y - self.target_pos) <= self.speed:
            self.stop()
        if self.target_pos == -1 or self.speed == 0:
            return
        self.velocity = (self.target_pos - self.center_y)  / self.speed
        self.pos = Vector(0, self.velocity) + self.pos

    def start_move_to(self, target):
        self.target_pos = clamp(self.height / 2, self.get_root_window().height - self.height / 2, target)

    def stop(self):
        self.target_pos = -1
    def handle_input(self, x, y):
        if y == self.center_y:
            self.stop()
        else:
            self.start_move_to(y)

    def handle_touch(self, touch):
        self.handle_input(touch.x, touch.y)

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def update(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self, vel=(4,0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, *args):
        self.ball.update()
        self.player1.update()
        self.player2.update()

        #bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        #bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        #went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4,0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4,0))


    def on_touch_move(self, touch):
        if touch.x < self.width/2:
            self.player1.handle_touch(touch)
        if touch.x > self.width/2:
            self.player2.handle_touch(touch)

    def on_touch_up(self, touch):
        if touch.x < self.width / 2:
            self.player1.velocity = 0
        if touch.x > self.width  / 2:
            self.player2.velocity = 0

    def on_touch_down(self, touch):
        self.on_touch_move(touch)


Factory.register("PongBall", PongBall)
Factory.register("PongPaddle", PongPaddle)
Factory.register("PongGame", PongGame)


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game



if __name__ == '__main__':
    PongApp().run()
