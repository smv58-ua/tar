#!/usr/bin/env python3
"""
dibuja_mov.py — Nodo ROS 2 que suscribe a /odom y registra la trayectoria
del Turtlebot 3 para representarla gráficamente con matplotlib.

Uso:
    ros2 run p3_pkg dibuja_mov

Pulsa Ctrl+C para finalizar la captura y generar la gráfica.
La imagen se guarda automáticamente como 'trayectoria.png'.
"""

import math
import signal
import sys

import matplotlib
matplotlib.use('Agg')   # backend sin pantalla (útil en contenedor sin GUI)
import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class DibujaMovNode(Node):
    """Suscribe a /odom y almacena la posición (x, y) del robot."""

    def __init__(self):
        super().__init__('dibuja_mov')

        # Listas de coordenadas registradas
        self._xs: list[float] = []
        self._ys: list[float] = []

        self._sub = self.create_subscription(
            Odometry,
            '/odom',
            self._odom_callback,
            10,
        )
        self.get_logger().info(
            'dibuja_mov activo — suscrito a /odom.\n'
            'Ejecuta el nodo movimiento y pulsa Ctrl+C aquí para guardar la gráfica.'
        )

    # ── Callback ──────────────────────────────────────────────────────────────

    def _odom_callback(self, msg: Odometry) -> None:
        """Almacena la posición del robot cada vez que llega un mensaje de odometría."""
        self._xs.append(msg.pose.pose.position.x)
        self._ys.append(msg.pose.pose.position.y)

    # ── Representación gráfica ────────────────────────────────────────────────

    def plot_trajectory(self, filename: str = 'trayectoria.png') -> None:
        """Dibuja y guarda la trayectoria registrada."""
        if not self._xs:
            self.get_logger().warn('No se recibieron datos de odometría; gráfica no generada.')
            return

        fig, ax = plt.subplots(figsize=(8, 8))

        # Traza de la trayectoria
        ax.plot(self._xs, self._ys, 'b-', linewidth=1.5, label='Trayectoria')

        # Marcadores de inicio y fin
        ax.plot(self._xs[0],  self._ys[0],  'go', markersize=12,
                label=f'Inicio ({self._xs[0]:.2f}, {self._ys[0]:.2f})')
        ax.plot(self._xs[-1], self._ys[-1], 'rs', markersize=12,
                label=f'Fin   ({self._xs[-1]:.2f}, {self._ys[-1]:.2f})')

        # Distancia entre inicio y fin (error de cierre)
        dx = self._xs[-1] - self._xs[0]
        dy = self._ys[-1] - self._ys[0]
        closure_error = math.hypot(dx, dy)

        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_title(
            f'Trayectoria del Turtlebot 3\n'
            f'Puntos registrados: {len(self._xs)} · '
            f'Error de cierre: {closure_error:.4f} m',
            fontsize=13,
        )
        ax.legend(fontsize=11)
        plt.tight_layout()

        fig.savefig(filename, dpi=150)
        self.get_logger().info(f'Gráfica guardada como "{filename}"')

        # Intentar mostrar en pantalla (sólo si hay entorno gráfico)
        try:
            matplotlib.use('TkAgg')
            plt.show()
        except Exception:
            pass


# ─── Main ─────────────────────────────────────────────────────────────────────

def main(args=None) -> None:
    rclpy.init(args=args)
    node = DibujaMovNode()

    def _shutdown_handler(sig, frame):
        """Maneja Ctrl+C: genera la gráfica y cierra limpiamente."""
        print()  # salto de línea tras ^C
        node.plot_trajectory()
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown_handler)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.plot_trajectory()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
