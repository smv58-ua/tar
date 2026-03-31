#!/usr/bin/env python3
"""
aparcamiento.py — Nodo ROS 2 que aparca el Turtlebot 3 en el espacio
definido en el mundo parking.world.

Layout del parking (coordenadas mundo):
  - Pared izquierda:  x ≈ 1.0
  - Pared derecha:    x ≈ 2.0
  - Pared trasera:    y ≈ -1.95
  - Entrada abierta:  y ≈ -1.0
  - Centro del hueco:  x ≈ 1.5

El robot arranca en (0, 0) mirando hacia +X.
Estrategia: avanzar hasta alinearse con el centro del hueco,
girar 90° (mirar hacia +Y, de espaldas al hueco) y entrar marcha atrás.

Uso:
    ros2 run p3_pkg aparcamiento
"""

import math
from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

SPEED = 0.15
ANGLE_SPEED = 0.3
LINEAR_TOLERANCE = 0.01
ANGULAR_TOLERANCE = 0.008


def quaternion_to_yaw(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class AparcamientoNode(Node):

    def __init__(self):
        super().__init__('aparcamiento_node')

        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(Odometry, 'odom', self._odom_cb, 10)

        self.x = None
        self.y = None
        self.theta = None
        self.angular_vel = 0.0

        self.origin_x = 0.0
        self.origin_y = 0.0
        self.origin_theta = 0.0

        self.action = None   # 'forward' | 'rotate'
        self.target = 0.0

        self.steps = deque()

    # ── Odometry callback ────────────────────────────────────────────────

    def _odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.theta = quaternion_to_yaw(
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        )
        self.angular_vel = msg.twist.twist.angular.z

        if self.action == 'forward' or self.action == 'reverse':
            self._forward_ctrl()
        elif self.action == 'rotate':
            self._rotate_ctrl()

    # ── Controllers ──────────────────────────────────────────────────────

    def _forward_ctrl(self):
        dist = math.hypot(self.x - self.origin_x, self.y - self.origin_y)
        remaining = self.target - dist
        if remaining < LINEAR_TOLERANCE:
            self._stop()
            self._next()
        else:
            speed = min(SPEED, max(0.05, remaining * 1.5))
            if self.action == 'reverse':
                speed = -speed
            msg = Twist()
            msg.linear.x = speed
            self.pub.publish(msg)

    def _rotate_ctrl(self):
        angle = math.atan2(
            math.sin(self.theta - self.origin_theta),
            math.cos(self.theta - self.origin_theta),
        )
        remaining = self.target - angle
        if abs(remaining) < ANGULAR_TOLERANCE:
            self._stop()
            self._next()
        else:
            w = min(ANGLE_SPEED, max(0.05, abs(remaining) * 1.5))
            msg = Twist()
            msg.angular.z = w if remaining > 0 else -w
            self.pub.publish(msg)

    def _stop(self):
        self.pub.publish(Twist())

    # ── Step sequencer ───────────────────────────────────────────────────

    def _next(self):
        if self.x is not None:
            self.get_logger().info(
                f'Pos: x={self.x:.2f}, y={self.y:.2f}, '
                f'theta={math.degrees(self.theta):.1f}°'
            )

        if not self.steps:
            self.get_logger().info('Aparcamiento completado.')
            raise SystemExit(0)

        self.action, value = self.steps.popleft()

        if self.action in ('forward', 'reverse'):
            self.origin_x = self.x
            self.origin_y = self.y
            self.target = value
        elif self.action == 'rotate':
            self.origin_theta = self.theta
            self.target = math.radians(value)

    # ── Main sequence ────────────────────────────────────────────────────

    def run(self):
        # Maniobra de aparcamiento en marcha atrás:
        # 1. Avanzar 1.5m (alinearse con el centro del hueco en X)
        # 2. Girar 90° (mirar hacia +Y, de espaldas al hueco)
        # 3. Marcha atrás 1.4m (entrar de culo en el hueco)
        self.steps.append(('forward', 1.5))
        self.steps.append(('rotate', 90))
        self.steps.append(('reverse', 1.4))

        self.get_logger().info('Esperando odometría...')
        while self.x is None:
            rclpy.spin_once(self, timeout_sec=0.1)

        # Corregir orientación inicial si no está alineado con X+
        correction = -math.degrees(self.theta)
        if abs(correction) > math.degrees(ANGULAR_TOLERANCE):
            self.steps.appendleft(('rotate', correction))

        self._next()


def main(args=None):
    rclpy.init(args=args)
    node = AparcamientoNode()
    node.run()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
