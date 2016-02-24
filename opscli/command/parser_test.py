# -*- coding: utf-8 -*-

import parser


data = u"hello test  ☃😋😌😍 😎😏😙 foo  'longer' 'example' 'multi \\' space'"
result = parser.parse(data)

expected = [
  'hello', 'test', u'☃😋😌😍', u'😎😏😙', 'foo', 'longer',
  'example', 'multi \' space']

print all(a == b for a, b in zip(result.result, expected))
