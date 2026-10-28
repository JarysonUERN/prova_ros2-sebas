"""Questao 11 - Cliente da acao /deslocamento com cancelamento.

Solicita o deslocamento do robo, cancela a acao apos 5 segundos e
apresenta a distancia percorrida ate o momento do cancelamento.
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from robo_interfaces.action import Deslocamento


class RoboAcaoClienteCancela(Node):
    def __init__(self):
        super().__init__('robo_acao_cliente_cancela')
        self._cliente = ActionClient(self, Deslocamento, 'deslocamento')
        self._goal_handle = None
        self._timer_cancelamento = None

    def enviar_meta(self, latitude, longitude, vel_lat, vel_lon):
        meta = Deslocamento.Goal()
        meta.latitude = latitude
        meta.longitude = longitude
        meta.velocidade_latitudinal = vel_lat
        meta.velocidade_longitudinal = vel_lon

        self.get_logger().info('Aguardando o servidor de acao...')
        self._cliente.wait_for_server()

        self.get_logger().info(
            f'Enviando meta: destino ({latitude}, {longitude}) com '
            f'velocidades ({vel_lat}, {vel_lon}) u/s')
        futuro_meta = self._cliente.send_goal_async(
            meta, feedback_callback=self.feedback_callback)
        futuro_meta.add_done_callback(self.resposta_meta_callback)

    def resposta_meta_callback(self, futuro):
        self._goal_handle = futuro.result()
        if not self._goal_handle.accepted:
            self.get_logger().info('Meta rejeitada pelo robo!')
            rclpy.shutdown()
            return
        self.get_logger().info(
            'Meta aceita. A acao sera cancelada apos 5 segundos...')
        # Dispara o cancelamento uma unica vez, 5 s depois
        self._timer_cancelamento = self.create_timer(5.0, self.cancelar_meta)

    def cancelar_meta(self):
        self._timer_cancelamento.cancel()
        self.get_logger().info('Enviando pedido de cancelamento...')
        futuro_cancel = self._goal_handle.cancel_goal_async()
        futuro_cancel.add_done_callback(self.cancelamento_callback)

    def cancelamento_callback(self, futuro):
        resposta = futuro.result()
        if len(resposta.goals_canceling) > 0:
            self.get_logger().info('Cancelamento aceito pelo servidor')
        futuro_resultado = self._goal_handle.get_result_async()
        futuro_resultado.add_done_callback(self.resultado_callback)

    def feedback_callback(self, mensagem):
        feedback = mensagem.feedback
        self.get_logger().info(
            f'Feedback -> posicao atual: ({feedback.latitude_atual:.2f}, '
            f'{feedback.longitude_atual:.2f})')

    def resultado_callback(self, futuro):
        resultado = futuro.result().result
        self.get_logger().info(
            f'Acao cancelada! Distancia percorrida ate o cancelamento: '
            f'{resultado.distancia_percorrida:.2f} unidades')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    no = RoboAcaoClienteCancela()
    # Destino (10, 10) com velocidade 1 u/s em cada eixo
    # (levaria ~10 s; o cancelamento ocorre aos 5 s)
    no.enviar_meta(10.0, 10.0, 1.0, 1.0)
    rclpy.spin(no)


if __name__ == '__main__':
    main()
