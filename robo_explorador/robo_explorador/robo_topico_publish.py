"""Questao 3 - No do robo que publica dados ambientais simulados.

Publica no topico /monitoramento valores aleatorios entre 1 e 100
para o nivel de oxigenio e a temperatura, a cada 1 segundo.
"""

import random

import rclpy
from rclpy.node import Node

from robo_interfaces.msg import Monitoramento


class RoboTopicoPublisher(Node):
    def __init__(self):
        super().__init__('robo_topico_publisher')
        self._publisher = self.create_publisher(
            Monitoramento, 'monitoramento', 10)
        self._timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('Robo iniciado: publicando em /monitoramento')

    def timer_callback(self):
        msg = Monitoramento()
        msg.nivel_oxigenio = random.uniform(1.0, 100.0)
        msg.temperatura = random.uniform(1.0, 100.0)
        self._publisher.publish(msg)
        self.get_logger().info(
            f'Publicando -> oxigenio: {msg.nivel_oxigenio:.2f}, '
            f'temperatura: {msg.temperatura:.2f}')


def main(args=None):
    rclpy.init(args=args)
    no = RoboTopicoPublisher()
    rclpy.spin(no)
    no.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
