#let ink      = rgb("#1a1a1a")   // body text
#let soft     = rgb("#6b7280")   // muted labels, page numbers
#let accent   = rgb("#2563eb")   // blue — only on Q labels
#let divider  = rgb("#e5e7eb")   // thin rules
#let surface  = rgb("#f0f1f4")   // code background

#set page(
  paper: "a4",
  footer: context {
    if counter(page).get().first() > 1 {
      line(length: 100%, stroke: 0.4pt + divider)
      align(center, text(size: 8pt, fill: soft)[#counter(page).display("1 / 1", both: true)])
    }
  },
)

#set text(
  font: "Rubik",
  size: 10.5pt,
  fill: ink,
  lang: "es",
  hyphenate: false,
)

#set par(
  leading: 0.60em,
  spacing: 1.25em,
  justify: true,
)

#set heading(numbering: none)

// Separator
#set line(length: 10%, stroke: divider)
#show line: it => align(center)[#block(inset: (top: 5pt, bottom: 5pt))[#it]]

// Enumerations
#show enum: it => block(inset: (left: 1.2em))[#it]

#set list(marker: [*#sym.quote.chevron.r.single*], spacing: 10pt)
#show list: set par(justify: false)
#show list: it => block(inset: (left: 1.2em))[#it]

// Outline
#show outline.entry.where(
  level: 1
): set block(above: 1.2em)

// Links
#show link: underline
#show link: set text(fill: accent)

// H1
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(1em)
  text(size: 22pt, weight: "bold", fill: ink)[#it.body]
  v(6pt, weak: true)
  line(length: 100%, stroke: 0.5pt + divider)
  v(1em,  weak: true)
}

// H2
#show heading.where(level: 2): it => {
  v(1.5em, weak: true)
  text(size: 13pt, weight: "semibold", fill: ink)[#it.body]
  v(0.5em)
}

// Code Block
#show raw.where(block: true): it => {
  v(1.4em, weak: true)
  block(
    fill: surface,
    inset: (x: 14pt, y: 11pt),
    radius: 5pt,
    stroke: divider,
    width: 100%,
  )[
    #text(font: "Maple Mono NF", size: 9pt, fill: ink)[#it]
  ]
  v(1.4em, weak: true)
}

// Inline block
#show raw.where(block: false): content => box(inset: (left: 3pt, right: 3pt))[
  #text(
    font: "Maple Mono NF",
    fill: rgb("#577dd0"),
    weight: "semibold",
    size: 9pt,
  )[
    #highlight(fill: surface, extent: 2.5pt)[#content]
  ]
]

// Q&A unit: small blue label → bold question → thin rule → answer
#let pregunta(num, question, body) = {
  block(width: 100%, above: 1.8em, below: 1.8em)[
    #text(size: 9pt, weight: "semibold", fill: accent)[PREGUNTA #num]
    #v(6pt, weak: true)
    #text(size: 11pt, weight: "semibold", fill: ink)[#question]
    #v(8pt, weak: true)
    #line(length: 100%, stroke: 0.4pt + divider)
    #v(10pt, weak: true)
    #body
  ]
}

// Exercise unit: muted label → bold title → thin rule → content
#let ejercicio(num, title, body) = {
  block(width: 100%, above: 1.8em, below: 1.8em)[
    #text(size: 9pt, weight: "semibold", fill: accent)[EJERCICIO #num]
    #v(6pt, weak: true)
    #text(size: 11pt, weight: "semibold", fill: ink)[#title]
    #v(8pt, weak: true)
    #line(length: 100%, stroke: 0.4pt + divider)
    #v(10pt, weak: true)
    #body
  ]
}

#let campo(label, body) = {
  v(1.5em, weak: true)
  text(size: 9pt, weight: "semibold", fill: soft)[#upper(label)]
  v(1.2em, weak: true)
  body
}

#let captura = block(
  width: 100%,
  height: 5cm,
  fill: surface,
  stroke: 0.6pt + divider,
  radius: 5pt,
)[
  #align(center + horizon)[
    #text(size: 9pt, fill: soft)[Captura de pantalla]
  ]
]

// --- PORTADA
#v(3cm)
#text(size: 28pt, weight: "bold", fill: ink)[Práctica 2]
#v(8pt, weak: true)
#text(size: 16pt, fill: soft)[Trabajando con el Turtlebot 3 en simulación]
#v(15pt)
#text(size: 11pt, fill: soft)[Abel Gandía Ruiz]
#v(8pt, weak: true)
#link("https://github.com/danisty/tar")[https://github.com/danisty/tar]
#v(16pt, weak: true)
#outline()

= Parte 1: Primeros Pasos con el Turtlebot y Odometría

== Preguntas teóricas

Para esta primera parte se lanza el Turtlebot 3 *Waffle* en `Gazebo` y se teleopera con el paquete `turtlebot3_teleop`. Esto nos permite estudiar los mecanismos de comunicación que emplea ROS 2 para controlar al robot.

```bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

#image("/assets/image-1.png")

#pregunta("1", [¿Cuál es el topic en el cual se debe publicar la información para que el robot se mueva?])[
  El topic sobre el que se publica para mover al robot es `/cmd_vel`. Se puede comprobar inspeccionando el nodo de teleoperación:
  ```bash
  ros2 node info /teleop_keyboard
  ```
  ```
  /teleop_keyboard
    Subscribers:

    Publishers:
      /cmd_vel: geometry_msgs/msg/Twist
      ...
    Service Servers:
      ...
    ...
  ```
]

#pregunta("2", [¿Cuál es el tipo de mensaje que se publica?])[
  El tipo de mensaje publicado en `/cmd_vel` es `geometry_msgs/msg/Twist`. Se puede verificar con:
  ```bash
  ros2 topic info /cmd_vel
  ```
  ```
  Type: geometry_msgs/msg/Twist
  Publisher count: 1
  Subscription count: 1
  ```
  El mensaje `Twist` contiene dos vectores de tres componentes cada uno:
  ```bash
  ros2 interface show geometry_msgs/msg/Twist
  ```
  ```
  # This expresses velocity in free space broken into its linear and angular parts.
  Vector3  linear
    float64 x
    float64 y
    float64 z
  Vector3  angular
    float64 x
    float64 y
    float64 z
  ```
  Para el Turtlebot 3, al tratarse de un robot diferencial que se mueve sobre un plano, únicamente se utilizan `linear.x` (velocidad de avance) y `angular.z` (velocidad de giro).
]

#pregunta("3", [¿Qué tipo de movimientos puede realizar el robot? ¿Cuáles son los ejes de movimientos positivos?])[
  El Turtlebot 3 es un robot de *tracción diferencial* con dos ruedas motrices. Esto le permite realizar dos tipos de movimiento:

  + *Movimiento lineal* a lo largo del eje X del robot: `linear.x > 0` avanza hacia adelante, `linear.x < 0` retrocede.

  + *Movimiento rotacional* alrededor del eje Z (vertical): `angular.z > 0` gira en sentido *antihorario* (izquierda), `angular.z < 0` gira en sentido *horario* (derecha).

  No puede desplazarse lateralmente (no tiene movimiento en el eje Y), por tanto, si le mandamos un giro de $-20°$, el robot girará hacia la *derecha*.
]

#pregunta("4", [¿El robot gira sobre su eje siempre? ¿Qué comando de odometría se le está mandando a los motores para que sea así?])[
  Sí, el Turtlebot 3 gira sobre su propio eje cuando se le envía únicamente velocidad angular (`angular.z != 0`) con velocidad lineal nula (`linear.x = 0`). En este caso, ambas ruedas giran a la misma velocidad pero en *sentidos opuestos*, haciendo que el punto medio del eje de las ruedas se mantenga fijo.
]

#pregunta("5", [¿Cuál es la unidad de magnitud de las velocidades lineales y angulares?])[
  Las unidades en ROS 2 siguen el sistema internacional (SI):
  - *Velocidad lineal:* metros por segundo (m/s)
  - *Velocidad angular:* radianes por segundo (rad/s)
]

#pagebreak()

== Ejercicios

#ejercicio("1", [Nodo `movimiento.py` con 4 modos de movimiento y nodo `dibuja_mov.py` para visualización de trayectorias])[

  Se ha creado el paquete `p3_pkg` con las dependencias necesarias (`rclpy`, `geometry_msgs`, `nav_msgs`). Dentro de este paquete se implementan dos nodos: `movimiento.py` para ejecutar las trayectorias y `dibuja_mov.py` para registrarlas y dibujarlas.

  Cada modo de movimiento define una cola de pasos `('forward', distancia)` o `('rotate', grados)`. El callback de odometría (`/odom`) compara la posición/ángulo actual con el origen del paso y, cuando se alcanza la tolerancia, pasa al siguiente paso.

  El nodo soporta dos modos de control, seleccionables con el flag `--pid`:
  - *Sin PID (por defecto):* velocidad constante; útil para observar el _drift_ odométrico en los ejercicios 1-2.
  - *Con PID (`--pid`):* controlador PID sobre la rotación y corrección de _heading_ en avance; detallado en el ejercicio 4.

  #campo("Modo 0: Movimiento lineal de 2 metros")[
    ```python
    if movement_type == 0:
        self.steps.append(('forward', 2.0))
    ```
    El robot avanza 2 metros en línea recta midiendo la distancia recorrida a través de la odometría.

    #pregunta("6", [¿Cómo puedo comprobar que el robot haya avanzado esta distancia?])[
      Se puede comprobar suscribiéndose al topic `/odom` de tipo `nav_msgs/msg/Odometry`. Este topic publica la posición estimada del robot. Comparando `pose.pose.position.x` antes y después del movimiento se puede calcular la distancia recorrida con:
      ```bash
      ros2 topic echo /odom
      ```
    ]

    #align(center)[
      #image("/assets/image-10.png")
    ]
  ]

  #campo("Modo 1: Triángulo equilátero de 3m de lado")[
    ```python
    elif movement_type == 1:
        for _ in range(3):
            self.steps.append(('forward', 3))
            self.steps.append(('rotate', -120))
    ```
    El robot avanza 3 metros y gira $-120°$ (horario) tres veces. El ángulo exterior de un triángulo equilátero es $(360°) / 3 = 120°$, con signo negativo para girar a la derecha.

    #image("/assets/image-11.png")
  ]

  #campo("Modo 2: Cuadrado de 1m de lado")[
    ```python
    elif movement_type == 2:
        for _ in range(4):
            self.steps.append(('forward', 1))
            self.steps.append(('rotate', -90))
    ```
    El robot avanza 1 metro y gira $-90°$ cuatro veces, dibujando un cuadrado.

    #image("/assets/image-12.png")
  ]

  #campo("Modo 3: Figura de infinito (bowtie)")[
    ```python
    elif movement_type == 3:
        self.steps.append(('forward', 0.5))
        self.steps.append(('rotate', -120))
        self.steps.append(('forward', 1))
        self.steps.append(('rotate', 120))
        self.steps.append(('forward', 0.5))
        self.steps.append(('rotate', 120))
        self.steps.append(('forward', 1))
        self.steps.append(('rotate', -120))
    ```
    La figura de infinito se construye como dos triángulos simétricos (un _bowtie_). El robot avanza 0.5m, gira para trazar el primer triángulo, vuelve al centro y traza el segundo triángulo en espejo.

    #image("/assets/image-13.png")
  ]

  #campo("Ejecución")[
    *Terminal 1:* Lanzar Gazebo con el Turtlebot 3
    ```bash
    export TURTLEBOT3_MODEL=waffle
    ros2 launch turtlebot3_gazebo empty_world.launch.py
    ```

    *Terminal 2:* Lanzar RViz2 para visualizar la trayectoria en tiempo real
    ```bash
    rviz2
    ```
    Se configura el _display_ *Odometry* sobre el topic `/odom` con `Keep` elevado ($>1000$) para acumular la traza, y se establece el _Fixed Frame_ a `odom`. Opcionalmente se añade el _display_ *RobotModel* para visualizar el robot.

    *Terminal 3:* Ejecutar el movimiento deseado
    ```bash
    ros2 run p3_pkg movimiento <modo>  # 0, 1, 2 o 3
    ```
  ]
]

#pagebreak()

#ejercicio("2", [Ejecutar 10 veces el cuadrado, triángulo e infinito y analizar la acumulación de error])[
  Se ejecutan los modos 1, 2 y 3 del nodo `movimiento.py` diez veces consecutivas sin resetear la simulación entre ejecuciones. RViz2 acumula la traza de odometría, permitiendo visualizar el _drift_ progresivo.

  #campo("Resultados")[
    Al repetir cada trayectoria 10 veces, se observa que el robot *no vuelve exactamente a la posición original* en cada iteración. El error se acumula progresivamente, haciendo que la trayectoria se desplace respecto al punto de inicio.

    #grid(
      columns: (1fr, 1fr, 1fr),
      align: center + horizon,
      gutter: 8pt,
      image("/assets/image-6.png"),
      image("/assets/image-7.png"),
      image("/assets/image-8.png"),
    )
  ]

  #pregunta("", [¿El robot acaba en la posición original? ¿A qué puede deberse esto?])[
    No, el robot *no vuelve exactamente* a la posición inicial tras cada repetición. El error se acumula con cada iteración, desplazando progresivamente el punto de retorno.

    Este problema se conoce como *drift odométrico* y es un problema fundamental de la odometría basada en ruedas (_dead reckoning_). Es la razón por la que los robots reales emplean sensores adicionales (LiDAR, cámaras, IMU) para corregir su estimación de posición.
  ]
]

#pagebreak()

#ejercicio("3", [Nodo `aparcamiento.py` para estacionar el Turtlebot 3 en un espacio delimitado])[
  Se ha implementado el nodo `aparcamiento.py` dentro del paquete `p3_pkg`.

  #campo("Entorno de simulación")[
    Para lanzar el entorno de aparcamiento:
    ```bash
    export TURTLEBOT3_MODEL=waffle
    ros2 launch p3_pkg parking_tb3.launch.py
    ```
    El mundo `parking.world` define un espacio de aparcamiento con las siguientes coordenadas:
    - Pared izquierda: $x approx 1.0$
    - Pared derecha: $x approx 2.0$
    - Pared trasera: $y approx -1.95$
    - Entrada abierta: $y approx -1.0$
    - Centro del hueco: $x approx 1.5$

    El robot arranca en $(0, 0)$ mirando hacia $+X$.
  ]

  #campo("Estrategia de aparcamiento")[
    Se realiza una maniobra de *aparcamiento en marcha atrás* (_reverse bay parking_) en tres pasos:

    + *Avanzar 1.5m:* el robot se desplaza en línea recta hacia $+X$ hasta alinearse con el centro del hueco ($x approx 1.5$).

    + *Girar $90°$:* rotación antihoraria para orientar el robot hacia $+Y$, quedando de espaldas a la entrada del espacio.

    + *Marcha atrás 1.4m:* el robot entra marcha atrás en el hueco hasta quedar centrado.

    ```python
    def run(self):
        self.steps.append(('forward', 1.5))
        self.steps.append(('rotate', 90))
        self.steps.append(('reverse', 1.4))
    ```
  ]

  #campo("Código")[
    ```python
    class AparcamientoNode(Node):
        def __init__(self):
            super().__init__('aparcamiento_node')
            self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
            self.create_subscription(Odometry, 'odom', self._odom_cb, 10)
            self.steps = deque()
            # ... (estado interno: posición, ángulo, acción actual)

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
                math.cos(self.theta - self.origin_theta))
            remaining = self.target - angle
            if abs(remaining) < ANGULAR_TOLERANCE:
                self._stop()
                self._next()
            else:
                w = min(ANGLE_SPEED, max(0.05, abs(remaining) * 1.5))
                msg = Twist()
                msg.angular.z = w if remaining > 0 else -w
                self.pub.publish(msg)
    ```
  ]

  #campo("Ejecución")[
    ```bash
    ros2 run p3_pkg aparcamiento
    ```

    #image("/assets/image-9.png")
  ]
]

#pagebreak()

#ejercicio("4", [Corrección de errores de odometría mediante un controlador PID])[
  Como se ha observado en los Ejercicios 1 y 2, el robot no ejecuta las trayectorias de forma perfecta. Para corregir estos errores se ha implementado un *controlador PID* (_Proportional-Integral-Derivative_) dentro del nodo `movimiento.py`, activable mediante el flag `--pid`.

  ```bash
  ros2 run p3_pkg movimiento 2 --pid       # cuadrado con PID
  ros2 run p3_pkg movimiento 2 10 --pid    # cuadrado 10 veces con PID
  ```

  Se implementan dos controladores PID independientes:

  *1. PID de rotación*: controla los giros puros (`angular.z`):
  ```python
  KP_ROT = 0.5    # Proporcional: corrección suave
  KI_ROT = 0.01   # Integral: compensa errores constantes
  KD_ROT = 0.05   # Derivativo: amortigua oscilaciones
  ```

  *2. PID de corrección de heading*: mantiene la línea recta durante el avance:
  ```python
  KP_HDG = 1.0    # Proporcional: corrección moderada
  KI_HDG = 0.0    # Integral: desactivado (no hay sesgo constante)
  KD_HDG = 0.1    # Derivativo: suaviza las correcciones
  ```

  Los valores se han ajustado a partir de implementaciones de referencia para el Turtlebot 3.

  Al iniciar cada avance, se memoriza el _heading_ actual como objetivo (`target_theta`). Si durante el avance el robot se desvía, el PID aplica una corrección en `angular.z` para reconducirlo.

  #campo("Implementación del PID")[
    ```python
    def _pid(self, error, kp, ki, kd):
        now = self.get_clock().now().nanoseconds / 1e9
        dt = now - self._prev_time if self._prev_time else 0.0
        self._prev_time = now

        self._integral += error * dt
        self._integral = max(-1.0, min(1.0, self._integral))  # anti-windup

        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        return kp * error + ki * self._integral + kd * derivative
    ```
    El mecanismo de *anti-windup* limita la integral entre $[-1, 1]$ para evitar que se acumule un valor excesivo cuando el error persiste.
  ]

  #campo("Tolerancia angular")[
    Con PID activo, la tolerancia angular se reduce a $0.002$ rad ($approx 0.11°$), frente a los $0.02$ rad ($approx 1.15°$) del modo sin PID. Esto es posible porque el PID desacelera suavemente al aproximarse al ángulo objetivo, mientras que el control a lazo abierto necesita una tolerancia mayor para evitar sobrepasos.
  ]

  #campo("Resultado")[
    Con el controlador PID, las trayectorias más precisas:
    - Los giros se completan con un error inferior a $0.002$ radianes ($approx 0.11°$)
    - Los avances mantienen el _heading_ con correcciones en tiempo real
    - Las velocidades se modulan proporcionalmente a la distancia restante, evitando sobrepasos

    #image("/assets/image-15.png")
  ]
]

#pagebreak()

#ejercicio("5", [Repetir los ejercicios con el Turtlebot 3 Burger y comparar resultados])[
  Se repiten los ejercicios 1-4 empleando el modelo `Burger` en lugar del `Waffle`:
  ```bash
  export TURTLEBOT3_MODEL=burger
  ```

  #image("/assets/image-16.png")

  #pregunta("", [¿Observas diferencias en la precisión de los movimientos entre Burger y Waffle? ¿Cuál robot acumula más error? ¿En qué tipo de movimiento se nota más la diferencia?])[
    Sí, hay diferencias aunque no son enormes. Al ejecutar 10 repeticiones del cuadrado con PID activado se obtiene:

    #table(
      columns: (1fr, 1fr, 1fr),
      table.header([*Métrica*], [*Waffle*], [*Burger*]),
      [Posición final], [($-0.02$, $-0.01$)], [($-0.02$, $-0.02$)],
      [Heading final], [$2.23°$], [$2.73°$],
      [Drift angular/iter], [$\~0.22°$], [$\~0.27°$],
    )

    Burger acumula algo más de error, sobre todo angular (un $\~23%$ más de drift por iteración). Donde más se nota es en los *giros*: como tiene las ruedas más juntas ($0.160$ m vs $0.288$ m), cualquier pequeña diferencia de velocidad entre ruedas se traduce en un desvío angular mayor.
  ]

  #pregunta("", [¿Burger realiza giros más amplios o más cerrados que Waffle?])[
    Burger hace giros *más cerrados*. Al tener las ruedas más juntas ($0.160$ m vs $0.288$ m en Waffle), el radio de giro es más pequeño.
  ]

  #pregunta("", [Al implementar controladores para corregir errores de trayectoria: ¿Los mismos parámetros PID funcionan igual para ambos robots?])[
    Sí, los mismos parámetros PID (`KP_ROT=0.5`, `KI_ROT=0.01`, `KD_ROT=0.05`) funcionan bien para los dos robots. Ninguno se vuelve inestable ni oscila, y ambos completan las 10 repeticiones del cuadrado sin problemas. Eso sí, Burger acumula algo más de drift angular ($\~0.27°$/iter vs $\~0.22°$/iter en Waffle), así que el PID no llega a compensar del todo el error extra que introduce su menor separación de ruedas. Para que Burger igualase a Waffle habría que subir un poco las ganancias, sobre todo la proporcional, para que corrija más agresivamente esas pequeñas desviaciones.
  ]

  #pregunta("", [Durante la tarea de aparcamiento: ¿Cuál robot realiza la maniobra con menos correcciones?])[
    Waffle aparca con menos correcciones. Al ser más pesado y tener la base más ancha ($0.266 times 0.266$ m), sus trayectorias son más estables y no se desvía tanto. Burger es bastante más compacto ($0.140 times 0.140$ m), así que le sobra espacio dentro del hueco, pero necesita más ajustes correciones.
  ]

  #pregunta("", [Inspecciona las propiedades URDF de ambos robots: ¿Cómo afectan las diferencias a la precisión y estabilidad?])[
    Las propiedades URDF se encuentran en el paquete `turtlebot3_gazebo/urdf/`. Las principales diferencias son:

    #table(
      columns: (1fr, 1fr, 1fr),
      table.header([*Propiedad*], [*Burger*], [*Waffle*]),
      [Radio de rueda], [$0.033$ m], [$0.033$ m],
      [Separación de ruedas], [$0.160$ m], [$0.288$ m],
      [Masa base], [$0.826$ kg], [$1.373$ kg],
      [Caja de colisión], [$0.140 times 0.140$ m], [$0.266 times 0.266$ m],
      [Ruedas caster], [1 trasera], [2 traseras],
      [Sensor LiDAR], [LDS-01 (360°)], [LDS-01 (360°)],
      [Cámara], [No], [Intel RealSense R200],
    )

    Lo que más afecta es la *separación de ruedas*: Waffle tiene la base casi el doble de ancha ($0.288$ vs $0.160$ m), lo que le da más estabilidad en línea recta. En un robot diferencial, el error angular de la odometría depende de $Delta v \/ L$ (siendo $L$ la separación entre ruedas), así que con la misma imprecisión en las ruedas, Burger acumula más error angular.

    La *masa* también se nota: Waffle pesa más ($1.373$ kg base vs $0.826$ kg), tiene más inercia y eso hace que sus movimientos sean más suaves y predecibles. Burger es más ágil, pero también más sensible a cualquier perturbación.
  ]
]

#pagebreak()

= Parte 2: Resolución de un Laberinto

En esta segunda parte de la práctica se utiliza el Turtlebot 3 equipado con un sensor LiDAR para resolver un laberinto de manera autónoma. Para ello se crea un nuevo paquete de ROS llamado `maze_pkg`, incluyendo todas las dependencias necesarias. Este paquete contendrá los nodos y scripts requeridos para la navegación del robot dentro del laberinto, empleando técnicas de percepción y control basadas en los datos del LiDAR.

Para comenzar, se lanza en un mundo vacío por un lado el Turtlebot 2 y por otro el Turtlebot 3, y se contesta a las siguientes preguntas para cada robot:

== Preguntas teóricas

#pregunta("12", [¿Cuál es el topic asociado al LiDAR? ¿Cuál es la tipología de los mensajes?])[

  El topic asiciado al LIDAR es `/scan` y el tipo de mensaje publicado es `sensor_msgs/msg/LaserScan`. Se puede verificar con:
  ```bash
  ros2 topic info /scan
  ```
  Lo cual nos devuelve:
  ```
  Type: sensor_msgs/msg/LaserScan
  Publisher count: 1
  Subscription count: 0
  ```
  Si mostramos información sobre el tipo de mensaje con el siguiente comando:
  ```bash
  ros2 interface show sensor_msgs/msg/LaserScan
  ```
  Obtenermos todos los campos que componen el mensaje:
  ```bash
    # Single scan from a planar laser range-finder
    #
    # If you have another ranging device with different behavior (e.g. a sonar
    # array), please find or create a different message, since applications
    # will make fairly laser-specific assumptions about this data

    std_msgs/Header header
        builtin_interfaces/Time stamp
            int32 sec
            uint32 nanosec
        string frame_id
    float32 angle_min
    float32 angle_max
    float32 angle_increment
    float32 time_increment
    float32 scan_time
    float32 range_min
    float32 range_max
    float32[] ranges
    float32[] intensities
  ```

]

#pregunta("13", [¿Cuál es el rango de distancias que puede medir el LiDAR? ¿Cuál es el rango angular de escaneo que tiene el LiDAR? ¿Cuál es el origen de referencia del LiDAR?])[
  Para poder comprobar los rangos de distancia y ángulo del LiDAR, así como su origen de referencia, se puede "escuchar" uno de los mensajes publicados en el topic `/scan` con el siguiente comando:
  ```bash
  ros2 topic echo /scan --once
  ```
  Entre la información publicada en el mensaje, se pueden encontrar los siguientes campos relevantes:
  - range_min: 0.11999999731779099
  - range_max: 3.5
  - angle_min: 0.0
  - angle_max: 6.28000020980835
  - frame_id: "base_scan"

  Con esta información se puede concluir que el LIDAR puede medir distancias desde aproximadamente 0.12 metros hasta 3.5 metros, con un rango angular completo de 360° (de 0 a $2\pi$ radianes). El origen de referencia del LiDAR es el frame `base_scan`, lo que nos indica que el centro de coordenada de la infromació devuelta por el LIDAR es la propia posición del sensor.

]

== Ejercicios

#ejercicio("1", [Nodo `res_maze.py` para resolver el laberinto con el Turtlebot 3])[

  Se ha implementado el nodo para resolver el primer laberinto (`maze_1.world`) utlizando la información del LIDAR para detectar las paredes del laberinto. Para ellos hemos usado el algortimo de seguimiento de pared derecha, que consiste en mantener la pared a la derecha del robot mientras se avanza. El robot gira a la derecha si no hay pared a su derecha, avanza recto mientras haya pared a su derecha, y gira derecha o izquierda si detecta un obstáculo frontal.

  Para resolverlo se han definido los cuatro estados siguientes:

  + *Avanzar recto:* El robot avanza manteniendo la pared a su derecha, corrigiendo su trayectoria si se aleja demasiado de ella.
  + *Girar a la izquierda:* El robot gira a la izquierda para evitar un obstáculo frontal, hasta que la vía quede despejada.
  + *Girar a la derecha para evitar un obstáculo:* El robot gira a la derecha en caso de enconctrar un obstáculo frontal.
  + *Girar a la derecha y avanzar:* El robot gira a la derecha mientras avanza, hasta tener una pared a su derecha.

  Además, se ha definido un estado extra a los cuatro típicos, para conseguir que el robot comience, debido a que en la posición inicial no se encuentra ninguna pared por lo que no se cumplía ninguna de las condiciones anteriores. En este estado inicial, el robot avanza recto hasta encontrar una pared, momento en el que comienza a aplicar el algoritmo de seguimiento de pared derecha.

  Para lograr obtener la infomación del LiDAR se ha creado un callback que se suscribe al topic correspondiente, y que procesa los datos de escaneo para determinar la presencia de paredes en las direcciones frontal y derecha. En función de esta información, el nodo decide qué acción tomar en cada momento. Para detectar un muro, se usa un angulo de "visión" y se calcula la distancia mínima a un obstáculo dentro de ese rango angular, durante las pruebas también se pobró a usar la media de las distancias dentro del rango, pero se observó que el mínimo era más efectivo para evitar colisiones.

  También se han definido unos umbrales de distancia para considerar que hay una pared, quedando establecidos finalmente en:

  ```python
  UMBRAL_FRENTE = 0.5      # Distancia mínima para considerar que hay una pared al frente (m)
  UMBRAL_DERECHA = 0.5     # Distancia mínima para considerar que hay una pared a la derecha (m)
  ```

  Como resultado, el robot es capaz de resolver el laberinto siguiendo la pared derecha, se puede comprobar en el siguiente #link("https://youtu.be/azQwjBAmv10")[video de la ejecución] del nodo o lanzando el entorno en Gazebo y ejecutando el nodo:

  - Primera terminal: Lanzar el entorno de Gazebo con el laberinto
  ```bash
  ros2 launch maze_pkg maze_1.launch.py
  ```

  - Segunda terminal: Ejecutar el nodo de resolución del laberinto
  ```bash
  ros2 run maze_pkg maze_solver_node
  ```
]

#pagebreak()

#ejercicio("2", [Ejecutar el algoritmo en el segundo laberinto (`maze_2.world`) y analizar su comportamiento])[
  En la carpeta `worlds` existe un segundo mapa con un modelo de laberinto distinto llamado `maze_2.world`. Se lanza este nuevo entorno en Gazebo y se ejecuta el algoritmo de resolución del Ejercicio 1:
  ```bash
  ros2 launch maze_pkg maze_2.launch.py
  ```

  #campo("Resultado")[
    #image("/assets/image-17.png")
  ]

  #pregunta("14", [¿Qué problemática observas en este tipo de escenarios?])[
    El problema principal de `maze_2` es que hay paredes internas que no están conectadas con las paredes exteriores del laberinto (las que tienen la salida). Esto hace que el algoritmo de seguimiento se quede dando vueltas indefinidamente alrededor de una "isla" interior sin llegar nunca a la salida, ya que la pared que sigue no lleva a ningún lado.
  ]

  #pregunta("15", [¿Es el robot capaz de resolver este laberinto? Si no es así, justifica tu respuesta. ¿Qué información crees que necesita el robot para poder llegar a resolverlo?])[
    Con un simple wall-following, no. Si el robot empieza siguiendo una pared que forma parte de una isla desconectada, se queda en bucle sin alcanzar la salida. En el siguiente #link("https://youtu.be/0M17mQbGifk?t=0")[video (0:00)] se puede observar exactamente este comportamiento con el Waffle.

    Para resolverlo necesitaría información adicional, como un mapa del laberinto (por ejemplo mediante SLAM) o algún mecanismo de memoria que le permita detectar que está repitiendo el mismo recorrido y cambiar de estrategia.
  ]

  Para mejorar el comportamiento ante ese bucle, se ha combinado el seguimiento de pared derecha con el algoritmo de *Pledge*: se integra la rotación neta del robot (mediante odometría) y, cuando el contador de giros vuelve a cero en un punto donde puede avanzar hacia el exterior de la "isla", se abandona el *wall following* y se busca de nuevo una pared a seguir. La lógica actual está en `ros2_ws/src/maze_pkg/maze_pkg/res_maze.py` (nodo `maze_solver`).

  #campo("Acumulación de rotación (`/odom`)")[
    El callback de odometría obtiene el _yaw_ a partir del cuaternión, calcula el incremento angular entre lecturas corrigiendo el salto $plus.minus 180°$, y acumula el giro en `rotacion_acumulada`, que es la magnitud que usa Pledge para saber si el robot ha completado un ciclo de vueltas respecto a la orientación de referencia:

    ```python
    if self.angulo_previo is None:
        self.angulo_previo = grados
        return

    delta = grados - self.angulo_previo
    if delta > 180.0:
        delta -= 360.0
    elif delta < -180.0:
        delta += 360.0

    self.rotacion_acumulada += delta
    self.angulo_previo = grados
    ```
  ]

  #campo("Máquina de estados Pledge + pared derecha")[
    `estado_pledge == 0` avanza en línea recta hasta detectar pared a la derecha; entonces pasa a `estado_pledge == 1` y aplica la misma lógica de cuatro casos que el seguimiento de pared (avanzar, girar izquierda, girar derecha, o combinar giro y avance). La novedad es la condición de escape: en estado 1, si la rotación acumulada está cerca de cero y no hay obstáculo frontal, se vuelve al estado 0 y se intenta "salir" recto, rompiendo el circuito alrededor de la isla:

    ```python
    if self.estado_pledge == 0:
        if self.pared_derecha:
            self.estado_pledge = 1
            self.rotacion_acumulada = 0.0
        else:
            cmd.linear.x = VEL_LINEAL
            cmd.angular.z = 0.0
    elif self.estado_pledge == 1:
        if abs(self.rotacion_acumulada) < TOLERANCIA_GRADOS and not self.pared_frente:
            self.estado_pledge = 0
            self.rotacion_acumulada = 0.0
            cmd.linear.x = VEL_LINEAL
            cmd.angular.z = 0.0
        else:
            if self.pared_derecha and not self.pared_frente:
                cmd.linear.x = VEL_LINEAL
                cmd.angular.z = 0.0
            elif self.pared_derecha and self.pared_frente:
                cmd.linear.x = 0.0
                cmd.angular.z = VEL_ANGULAR
            elif self.pared_frente and not self.pared_derecha:
                cmd.linear.x = 0.0
                cmd.angular.z = -VEL_ANGULAR
            else:
                cmd.linear.x = VEL_LINEAL / 4.0
                cmd.angular.z = -VEL_ANGULAR
    ```
  ]

  Con Pledge, el Turtlebot 3 Waffle consigue completar el laberinto `maze_2`, como se puede comprobar en el mismo #link("https://youtu.be/0M17mQbGifk?t=95")[video (1:35)].
]

#pagebreak()

#ejercicio("3", [Repetir los Ejercicios 1 y 2 con el Turtlebot 3 Burger])[
  Se repiten los ejercicios anteriores empleando el modelo `Burger`:
  ```bash
  export TURTLEBOT3_MODEL=burger
  ```

  #pregunta("16", [¿Qué diferencias observas respecto al otro modelo? Detalla claramente las diferencias que observes.])[
    Al ejecutar el Burger en el primer laberinto (#link("https://www.youtube.com/watch?v=yInB-Bq9tng")[video maze\_1]) y en el segundo con Pledge (#link("https://youtu.be/0M17mQbGifk?t=227")[video maze\_2, 3:47]), se observan las siguientes diferencias respecto al Waffle:

    - *Tamaño y maniobrabilidad:* Burger es significativamente más pequeño ($0.140 times 0.140$ m frente a $0.266 times 0.266$ m), lo que le permite pasar por pasillos estrechos con más holgura. Sin embargo, su menor separación de ruedas ($0.160$ m vs $0.288$ m) hace que sus giros sean menos estables y más propensos a desviaciones.

    - *Velocidad de respuesta:* Al tener menos masa ($0.826$ kg vs $1.373$ kg), Burger reacciona más rápidamente a los comandos de velocidad, pero también es más sensible a las correcciones, lo que puede provocar un comportamiento ligeramente más nervioso al seguir las paredes.

    - *Drift en los giros:* Como ya se observó en la Parte 1, Burger acumula más error angular por iteración. En el contexto del laberinto esto se traduce en que ocasionalmente se acerca demasiado a las paredes o tarda un poco más en estabilizar su trayectoria tras un giro.

    - *Velocidad de resolución:* A pesar de su menor estabilidad, Burger termina los laberintos en menos tiempo. Su menor masa e inercia hacen que alcance la velocidad de consigna más rápido tras cada giro, y su tamaño compacto le permite tomar las curvas sin necesitar tanto margen de maniobra, reduciendo el tiempo total de recorrido.

    - *Resolución con Pledge:* Ambos modelos consiguen resolver `maze_2` con el algoritmo de Pledge, pero Burger necesita más correcciones durante el seguimiento de pared debido a su menor estabilidad. El algoritmo funciona correctamente con los mismos parámetros para ambos robots.
  ]
]

#pagebreak()

#ejercicio("4", [Generación de un laberinto personalizado y resolución con ambos modelos])[
  Se genera un nuevo laberinto personalizado (`maze_3.world`) y se prueban ambos modelos del Turtlebot 3 para resolverlo.

  #campo("Generación del laberinto")[
    Para crear el laberinto se ha desarrollado un script en Python (`custom_maze_world_gen.py`) que genera directamente un fichero `.world` compatible con Gazebo. El script utiliza un algoritmo de *Depth-First Search* para generar un laberinto perfecto (sin ciclos) sobre una rejilla de $15 times 15$ celdas, con celdas de $1.2$ m de lado. Después, elimina aleatoriamente un $15%$ de las paredes internas (`ISLAND_FACTOR`) para crear islas y pasillos de anchura variable, haciendo que el laberinto requiera el algoritmo de Pledge para ser resuelto. Todas las paredes se agrupan en un único `<link>` SDF para optimizar el rendimiento de Gazebo.

    ```python
    WIDTH = 15          # Celdas en X
    HEIGHT = 15         # Celdas en Y
    CELL_SIZE = 1.2     # Tamaño de celda (m)
    WALL_THICKNESS = 0.15
    WALL_HEIGHT = 1.0
    ISLAND_FACTOR = 0.15  # Probabilidad de eliminar una pared para crear islas
    ```

    El robot se posiciona en el centro del laberinto y la salida se abre en la pared superior central. Para generar el mundo basta con ejecutar:
    ```bash
    python3 custom_maze_world_gen.py
    ```
    Esto produce el fichero `maze_3.world` listo para ser lanzado en Gazebo.
  ]

  #campo("Diseño del laberinto")[
    #image("/assets/image-18.png")
  ]

  #campo("Resultado")[
    El modelo Burger resuelve el laberinto generado utilizando el algoritmo de Pledge, como se puede ver en el siguiente #link("https://youtu.be/Ysx-LqwLCmk")[video]. El Waffle también lo completa sin problemas gracias a su mayor estabilidad, aunque el laberinto está dimensionado para que ambos modelos puedan recorrerlo cómodamente dado el tamaño de celda de $1.2$ m.
  ]
]