"""Questao 4 - Estacao base que le os dados do topico /monitoramento.

Saida: "Safe" se a temperatura estiver entre 10 e 40 graus e o nivel
de oxigenio for maior que 80; "Not Safe" caso contrario.
"""

import rclpy
from rclpy.node import Node

from robo_interfaces.msg import Monitoramento


class RoboTopicoSubscriber(Node):
    def __init__(self):
        super().__init__('robo_topico_subscriber')
        self._subscription = self.create_subscription(
            Monitoramento, 'monitoramento', self.listener_callback, 10)
        self.get_logger().info('Estacao base ouvindo /monitoramento')

    def listener_callback(self, msg):
        if 10.0 <= msg.temperatura <= 40.0 and msg.nivel_oxigenio > 80.0:
            status = 'Safe'
        else:
            status = 'Not Safe'
        self.get_logger().info(
            f'Oxigenio: {msg.nivel_oxigenio:.2f} | '
            f'Temperatura: {msg.temperatura:.2f} -> {status}')


def main(args=None):
    rclpy.init(args=args)
    no = RoboTopicoSubscriber()
    rclpy.spin(no)
    no.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
