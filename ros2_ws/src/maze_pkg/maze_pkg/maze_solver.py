import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

VEL_ANGULAR = 0.5       # Velocidad angular máxima (rad/s)
VEL_LINEAL = 0.4        # Velocidad lineal máxima (m/s)
GRADOS_BUSQUEDA = 20    # Ángulo en grados para buscar obstáculos (frente y derecha)
UMBRAL_FRENTE = 1.2     # Distancia mínima para considerar que hay una pared al frente (m)
UMBRAL_DERECHA = 1.2    # Distancia mínima para considerar que hay una pared a la derecha (m)

class MazeSolverNode(Node):

    def __init__(self):
        super().__init__('maze_solver')
        
        # Publicador para cmd_vel y suscriptor para el LiDAR
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, rclpy.qos.qos_profile_sensor_data
        )

        # Variables de estado del entorno inicializadas a False
        self.pared_derecha = False
        self.pared_frente = False

        self.rangos = []

    def scan_callback(self, msg: LaserScan):
        self.rangos = list(msg.ranges)
        if not self.rangos:
            return
            
        self.actualizar_estados()
        self.procesar_movimiento()

    def obtener_distancia_media(self, angulo_central, apertura):
        
        n_rayos = len(self.rangos)
        
        if n_rayos == 0:
            return float('inf')

        grados_por_rayo = 360.0 / n_rayos 
        rayos_validos = []
        
        for i in range(-apertura, apertura + 1):
            # Calculamos el índice asegurando que dé la vuelta al array (359 maximo)
            indice = int((angulo_central + i) / grados_por_rayo) % n_rayos
            dist = self.rangos[indice]
            
            # Filtramos valores basura del sensor
            if not math.isinf(dist) and not math.isnan(dist) and dist > 0.05:
                rayos_validos.append(dist)
        
        # Devolvemos la media del sector
        if rayos_validos:
            return sum(rayos_validos) / len(rayos_validos)
        else:
            return float('inf')

    def obtener_distancia_minima(self, angulo_central, apertura):
        
        n_rayos = len(self.rangos)
        
        if n_rayos == 0:
            return float('inf')

        grados_por_rayo = 360.0 / n_rayos 
        rayos_validos = []
        
        for i in range(-apertura, apertura + 1):
            # Calculamos el índice asegurando que dé la vuelta al array (359 maximo)
            indice = int((angulo_central + i) / grados_por_rayo) % n_rayos
            dist = self.rangos[indice]
            
            # Filtramos valores basura del sensor
            if not math.isinf(dist) and not math.isnan(dist) and dist > 0.05:
                rayos_validos.append(dist)
        
        # Devolvemos el minimo (el punto más cercano del sector)
        if rayos_validos:
            return min(rayos_validos)
        else:
            return float('inf')

    def actualizar_estados(self):

        # El frente usa la función de mínima distancia
        dist_frente = self.obtener_distancia_minima(0, GRADOS_BUSQUEDA)
        
        # La derecha usa la función de mínima distancia
        dist_derecha = self.obtener_distancia_minima(360 - int(GRADOS_BUSQUEDA * 1.5), GRADOS_BUSQUEDA)

        # Actualizamos las variables de estado
        self.pared_frente = (dist_frente < UMBRAL_FRENTE)
        self.pared_derecha = (dist_derecha < UMBRAL_DERECHA)

    def procesar_movimiento(self):
        
        cmd = Twist()

        # --- MÁQUINA DE ESTADOS ---

        # 1. Tener pared a la derecha y sin pared al frente
        if self.pared_derecha and not self.pared_frente:
            self.get_logger().info('ESTADO 1: Avanzando recto')
            cmd.linear.x = VEL_LINEAL
            cmd.angular.z = 0.0

        # 2. Tener pared derecha y pared al frente
        elif self.pared_derecha and self.pared_frente:
            self.get_logger().info('ESTADO 2: Girando izquierda')
            cmd.linear.x = 0.0
            cmd.angular.z = VEL_ANGULAR

        # 3. Tener pared al frente y no tener pared derecha
        elif self.pared_frente and not self.pared_derecha:
            self.get_logger().info('ESTADO 3 (Antiguo 4): Girando derecha')
            cmd.linear.x = 0.0
            cmd.angular.z = -VEL_ANGULAR
            
        # 4. No tener pared al frente ni a la derecha
        else:
            self.get_logger().info('ESTADO 4: Avanzando recto (Estado por defecto)')
            cmd.linear.x = VEL_LINEAL
            cmd.angular.z = -VEL_ANGULAR

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    nodo = MazeSolverNode()
    
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        nodo.get_logger().info('Nodo detenido por el usuario (Ctrl+C).')
    finally:
        nodo.cmd_pub.publish(Twist())
        nodo.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()