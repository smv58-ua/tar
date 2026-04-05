import math
import rclpy
import rclpy.qos
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

VEL_ANGULAR = 0.5       # Velocidad angular máxima (rad/s)
VEL_LINEAL = 0.4        # Velocidad lineal máxima (m/s)
GRADOS_BUSQUEDA = 20    # Ángulo en grados para buscar obstáculos (frente y derecha)
UMBRAL_FRENTE = 0.5     # Distancia mínima para considerar que hay una pared al frente (m)
UMBRAL_DERECHA = 0.5    # Distancia mínima para considerar que hay una pared a la derecha (m)
TOLERANCIA_GRADOS = 15.0 # Márgen de error para considerar una rotación como cero

class MazeSolverNode(Node):

    def __init__(self):
        super().__init__('maze_solver')
        
        # Publicador para cmd_vel y suscriptor para el LiDAR
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, rclpy.qos.qos_profile_sensor_data
        )
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        

        # Variables de estado del entorno inicializadas a False
        self.pared_derecha = False
        self.pared_frente = False

        # variables de inicialización de pledge
        self.grados_rotacion = 0.0
        self.estado_pledge = 0 # 0: Buscando norte, 1: hugging wall
        self.rotacion_acumulada = 0.0 
        self.angulo_previo = None 

        self.rangos = []

    def scan_callback(self, msg: LaserScan):
        self.rangos = list(msg.ranges)
        if not self.rangos:
            return
            
        self.actualizar_estados()
        self.procesar_movimiento()

    def odom_callback(self, msg: Odometry):
        # Obtener el quaternion del odm msg
        q = msg.pose.pose.orientation

        # Formula para convertir y extraer el "yaw" (nuestra rotación que interesa)
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        
        yaw_radians = math.atan2(siny_cosp, cosy_cosp)
        grados = math.degrees(yaw_radians)

        if grados < 0:
            grados += 360.0

        self.grados_rotacion = grados

        # Si leemos el sensor por primera vez, guardamos el ángulo y terminamos
        if self.angulo_previo is None:
            self.angulo_previo = grados
            return
        
        # Calculamos cuánto ha girado el robot desde la última lectura
        delta = grados - self.angulo_previo

        # Corregimos el salto de la brújula
        if delta > 180.0:
            delta -= 360.0
        elif delta < -180.0:
            delta += 360.0
        
        # Sumamos 
        self.rotacion_acumulada += delta

        # actualizamos el ángulo previo
        self.angulo_previo = grados

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

        # Loggear  las variables de pledge
        self.get_logger().info(
                f'Estado Pledge: {self.estado_pledge}, Rotacion Acumulada: {self.rotacion_acumulada:.2f} grados'
        )
        # --- MÁQUINA DE ESTADOS ---

        if self.estado_pledge == 0:
            # ESTADO 0: Buscando la pared (Norte)
            if self.pared_derecha:
                self.get_logger().info('Encontramos la pared, cambiamos a Estado 1 (Abrazmos pared)')
                self.estado_pledge = 1
                # Reseteamos
                self.rotacion_acumulada = 0.0
            else:
                cmd.linear.x = VEL_LINEAL
                cmd.angular.z = 0.0
        elif self.estado_pledge == 1:
            # ESTADO 1: Abrazando la pared

            # Condicion de escape - Si regresamos a cero (misma orientación) y no hay pared al frente
            if abs(self.rotacion_acumulada) < TOLERANCIA_GRADOS and not self.pared_frente:
                self.get_logger().info('Regresamos a cero, cambiamos a Estado 0 (Buscando Norte)')
                self.estado_pledge = 0
                self.rotacion_acumulada = 0.0
                # avanzamos
                cmd.linear.x = VEL_LINEAL
                cmd.angular.z = 0.0
            else:
                # Lógica abrazando la pared por la derecha
                
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
                    self.get_logger().info('ESTADO 3: Girando derecha')
                    cmd.linear.x = 0.0
                    cmd.angular.z = -VEL_ANGULAR
                    
                # 4. No tener pared al frente ni a la derecha
                else:
                    self.get_logger().info('ESTADO 4: Girando derecha y avanzando')
                    cmd.linear.x = VEL_LINEAL / 4.0
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