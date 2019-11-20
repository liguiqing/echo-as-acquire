import unittest
from unittest import TestCase

from local_http_server import emit_message_buffer
from local_http_server import EmitMessage

class TestLocalHttpServer(TestCase):

    def test_class_emit_message_init(self):
        self.assertTrue(True)
        emit_message1 = EmitMessage(data={'test':True})
        self.assertEquals('keep_alive',emit_message1.on)
        self.assertTrue(emit_message1.data['test'])

    def test_emit_message_buffer(self):
        self.assertIsNotNone(emit_message_buffer)
        emit_message_buffer.over()
        self.assertEquals(1,emit_message_buffer.size())
        em = EmitMessage(on='over', data={'success':True})
        self.assertEquals(em,emit_message_buffer.get())
        em = EmitMessage(on='test', data={'success':True})
        emit_message_buffer.put('test',data={'success':True})
        self.assertEquals(em,emit_message_buffer.get())