import sys
import math
import time

from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty

SPEED = 0.15
ANGLE_SPEED = 0.3

LINEAR_TOLERANCE = 0.01
ANGULAR_TOLERANCE = 0.02
ANGULAR_TOLERANCE_PID = 0.002  # ~0.11 degrees
SETTLE_VELOCITY = 0.005  # rad/s — robot considered stopped below this

SEQUENCES = {0, 1, 2, 3}

# ── PID gains ────────────────────────────────────────────────────────────────
# Rotation PID (controls angular.z while turning in place)
KP_ROT = 0.5
KI_ROT = 0.01
KD_ROT = 0.05

# Heading correction PID (keeps straight line while driving forward)
KP_HDG = 1.0
KI_HDG = 0.0
KD_HDG = 0.1


def normalize_angle(a):
    """Normaliza un ángulo al rango (-π, π]."""
    return math.atan2(math.sin(a), math.cos(a))


def quaternion_to_euler(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class MovementNode(Node):

    def __init__(self, pid_enabled=False):

        super().__init__('movement_node')

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.reset_client = self.create_client(Empty, '/reset_simulation')

        self.x = None
        self.y = None
        self.theta = None
        self.angular_vel = 0.0

        self.origin_x = None
        self.origin_y = None

        # Incremental rotation tracking
        self.last_theta = None
        self.turn_accumulated = 0.0

        self.type = None
        self.value = None

        self.steps = deque()

        # PID
        self.pid_enabled = pid_enabled
        self.target_theta = None
        self._prev_error = 0.0
        self._integral = 0.0
        self._prev_time = None

    # ------------ Callback ------------

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.angular_vel = msg.twist.twist.angular.z

        self.theta = quaternion_to_euler(
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w
        )

        if self.type == 'settle':
            self.settle_controller()

        elif self.type == 'forward':
            self.forward_movement_controller()

        elif self.type == 'rotate':
            self.rotate_movement_controller()

    # ------------ PID helper ------------

    def _pid(self, error, kp, ki, kd):
        """Calcula la salida PID dado un error."""
        now = time.monotonic()
        if self._prev_time is None:
            dt = 0.0
        else:
            dt = now - self._prev_time
        self._prev_time = now

        self._integral += error * dt
        self._integral = max(-1.0, min(1.0, self._integral))

        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        return kp * error + ki * self._integral + kd * derivative

    def _reset_pid(self):
        self._prev_error = 0.0
        self._integral = 0.0
        self._prev_time = None

    # ------------ Movement controllers ------------

    def settle_controller(self):
        """Wait for robot to physically stop before starting next step."""
        self.stop_robot()
        if abs(self.angular_vel) < SETTLE_VELOCITY:
            self.type = self._pending_type
            self.value = self._pending_value
            self._start_step()

    def forward_movement_controller(self):

        if self.x is None or self.y is None:
            return

        distance_traveled = math.hypot(self.x - self.origin_x, self.y - self.origin_y)
        remaining = self.value - distance_traveled

        if remaining < LINEAR_TOLERANCE:
            self.stop_robot()
            self.next_step()
            return

        msg = Twist()

        if self.pid_enabled:
            msg.linear.x = min(SPEED, max(0.05, remaining * 1.5))
            heading_error = normalize_angle(self.target_theta - self.theta)
            angular_correction = self._pid(heading_error, KP_HDG, KI_HDG, KD_HDG)
            msg.angular.z = max(-ANGLE_SPEED, min(ANGLE_SPEED, angular_correction))
        else:
            msg.linear.x = SPEED
            msg.angular.z = 0.0

        self.publisher.publish(msg)

    def rotate_movement_controller(self):

        if self.theta is None or self.last_theta is None:
            return

        delta = normalize_angle(self.theta - self.last_theta)
        self.turn_accumulated += delta
        self.last_theta = self.theta

        remaining = self.value - self.turn_accumulated

        ang_tol = ANGULAR_TOLERANCE_PID if self.pid_enabled else ANGULAR_TOLERANCE

        if abs(remaining) < ang_tol:
            self.stop_robot()
            self.next_step()
            return

        msg = Twist()

        if self.pid_enabled:
            output = self._pid(remaining, KP_ROT, KI_ROT, KD_ROT)
            msg.angular.z = max(-ANGLE_SPEED, min(ANGLE_SPEED, output))
        else:
            msg.angular.z = ANGLE_SPEED if remaining > 0 else -ANGLE_SPEED

        self.publisher.publish(msg)

    def stop_robot(self):
        self.publisher.publish(Twist())

    # ----------- Movement sequence management ------------

    def next_step(self):

        if self.x is not None and self.y is not None and self.theta is not None:
            self.get_logger().info(f'Initial/Final step position: x={self.x:.2f}, y={self.y:.2f}, theta={math.degrees(self.theta):.2f} degrees')

        if len(self.steps) == 0:
            return

        self.steps.popleft()

        if len(self.steps) == 0:
            self.get_logger().info('All steps completed.')
            self.stop_robot()
            rclpy.shutdown()
            return

        step = self.steps[0]
        next_type, next_value = step

        # If transitioning from rotate to forward, settle first
        if self.type == 'rotate' and next_type == 'forward':
            self._pending_type = next_type
            self._pending_value = next_value
            self.type = 'settle'
            return

        self.type, self.value = next_type, next_value
        self._start_step()

    def _start_step(self):
        if self.type == 'forward':
            self.origin_x = self.x
            self.origin_y = self.y

            if self.pid_enabled:
                self.target_theta = self.theta
                self._reset_pid()

            msg = Twist()
            msg.linear.x = SPEED
            self.publisher.publish(msg)

        elif self.type == 'rotate':
            self.last_theta = self.theta
            self.turn_accumulated = 0.0
            self.value = math.radians(self.value)

            if self.pid_enabled:
                self._reset_pid()

            msg = Twist()
            msg.angular.z = ANGLE_SPEED if self.value > 0 else -ANGLE_SPEED
            self.publisher.publish(msg)

    def _reset_pose(self):
        """Reset Gazebo simulation so the robot starts at (0, 0, 0)."""
        self.stop_robot()
        if not self.reset_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().warn('/reset_simulation not available, skipping reset')
            return False
        future = self.reset_client.call_async(Empty.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        # Clear cached odom so we wait for fresh values after reset
        self.x = None
        self.y = None
        self.theta = None
        self.get_logger().info('Simulation reset: pose set to origin')
        return True

    def init(self):

        if len(self.steps) == 0:
            self.get_logger().info('No steps to execute.')
            rclpy.shutdown()
            return

        step = self.steps[0]
        self.type, self.value = step

        self._start_step()

    def run(self, movement_type, repeats=1):

        for _ in range(repeats):
            if movement_type == 0:

                self.steps.append(('forward', 2.0))

            elif movement_type == 1:
                for _ in range(3):
                    self.steps.append(('forward', 3))
                    self.steps.append(('rotate', -120))

            elif movement_type == 2:
                for _ in range(4):
                    self.steps.append(('forward', 1))
                    self.steps.append(('rotate', -90))

            elif movement_type == 3:
                self.steps.append(('forward', 0.5))
                self.steps.append(('rotate', -120))
                self.steps.append(('forward', 1))
                self.steps.append(('rotate', 120))
                self.steps.append(('forward', 0.5))
                self.steps.append(('rotate', 120))
                self.steps.append(('forward', 1))
                self.steps.append(('rotate', -120))

        self._reset_pose()

        self.get_logger().info('Esperando primer mensaje de odometría...')
        while self.x is None or self.y is None or self.theta is None:
            rclpy.spin_once(self, timeout_sec=0.1)

        # Correct any residual heading after reset
        ang_tol = ANGULAR_TOLERANCE_PID if self.pid_enabled else ANGULAR_TOLERANCE
        initial_correction = -math.degrees(self.theta)
        if abs(initial_correction) > math.degrees(ang_tol):
            self.steps.appendleft(("rotate", initial_correction))

        self.init()

def main(args=None):

    rclpy.init(args=args)

    if len(sys.argv) < 2:
        print('Uso: ros2 run p3_pkg movimiento <modo> [repeats] [--pid]')
        rclpy.shutdown()
        return

    pid_enabled = '--pid' in sys.argv
    argv_filtered = [a for a in sys.argv[1:] if a != '--pid']

    try:
        mode = int(argv_filtered[0])
    except (ValueError, IndexError):
        print(f'Error: modo no válido.')
        rclpy.shutdown()
        return

    if mode not in SEQUENCES:
        print(f'Error: Modo "{mode}" no reconocido.')
        rclpy.shutdown()
        return

    repeats = 1
    if len(argv_filtered) >= 2:
        try:
            repeats = int(argv_filtered[1])
        except ValueError:
            pass

    node = MovementNode(pid_enabled=pid_enabled)
    if pid_enabled:
        node.get_logger().info('PID control enabled')
    node.run(mode, repeats)

    rclpy.spin(node)

if __name__ == '__main__':
    main()
