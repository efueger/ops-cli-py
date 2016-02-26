# -*- coding: utf-8 -*-

from opscli.command import parse


data = u"hello test  ☃😋😌😍 😎😏😙 foo  'longer' 'example' 'multi \\' space'"
result = parse.parse(data)

expected = [
  'hello', 'test', u'☃😋😌😍', u'😎😏😙', 'foo', 'longer',
  'example', 'multi \' space']

print all(a == b for a, b in zip(result.commands[0], expected))


data = u"test "
print parse.parse(data).success # == False

data = u" test"
print parse.parse(data).success # == False

data = u"test|"
print parse.parse(data).success # == False

tests = ['cmd1  |cmd2 | cmd3', 'cmd1|cmd2|cmd3', 'cmd1 arg | cmd2', 'cmd1 arg|cmd2']
for data in tests:
    result = parse.parse(data)
    if result.error:
        print data, result.error
    expected = [x.strip().split(' ') for x in data.split('|')]
    if not result.error:
        print data, str(result.commands) == str(expected)
