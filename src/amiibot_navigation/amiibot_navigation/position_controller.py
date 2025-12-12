import time
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.duration import Duration

def main():
    # 1. Inicializar ROS 2
    rclpy.init()

    # 2. Instanciar el Navegador (La API mágica)
    navigator = BasicNavigator()

    # 3. Esperar a que Nav2 esté completamente activo
    # (Esto verifica que amcl, bt_navigator, planner, controller, etc. estén listos)
    print("Esperando a que Nav2 esté listo...")
    navigator.waitUntilNav2Active()

    # --- Opcional: Establecer la posición inicial si no se ha hecho ---
    # Si ya lo hiciste en Rviz o tienes un buen mapa guardado, puedes saltar esto.
    # initial_pose = PoseStamped()
    # initial_pose.header.frame_id = 'map'
    # initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    # initial_pose.pose.position.x = 0.0
    # initial_pose.pose.position.y = 0.0
    # initial_pose.pose.orientation.z = 0.0
    # initial_pose.pose.orientation.w = 1.0
    # navigator.setInitialPose(initial_pose)

    # 4. Definir la meta (Goal)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    
    # Coordenadas X e Y en metros (según tu mapa)
    goal_pose.pose.position.x = -0.35
    goal_pose.pose.position.y = 0.0
    
    # Orientación (cuaterniones). w=1.0 significa mirando hacia "adelante" (0 grados)
    goal_pose.pose.orientation.z = 0.0
    goal_pose.pose.orientation.w = 1.0

    # 5. Enviar la meta
    print(f"Yendo a ({goal_pose.pose.position.x}, {goal_pose.pose.position.y})...")
    navigator.goToPose(goal_pose)

    # 6. Bucle de monitoreo mientras el robot se mueve
    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            # Puedes imprimir cuánto tiempo falta o la distancia restante
            print(f'Distancia restante: {feedback.distance_remaining:.2f} m', end='\r')
            
            # Aquí podrías poner lógica extra:
            # "Si lleva mucho tiempo (> 100s), cancelar": navigator.cancelTask()

    # 7. Evaluar el resultado final
    result = navigator.getResult()
    
    if result == TaskResult.SUCCEEDED:
        print("\n¡Meta alcanzada con éxito!")
    elif result == TaskResult.CANCELED:
        print("\nLa meta fue cancelada.")
    elif result == TaskResult.FAILED:
        print("\nFalló la navegación (¿obstáculo?, ¿camino bloqueado?)")

    # Cerrar
    #navigator.lifecycleShutdown()
    exit(0)

if __name__ == '__main__':
    main()