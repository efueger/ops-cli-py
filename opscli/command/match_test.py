import match

#print grammar.match('test', 'foo') # == True
#print grammar.match('test', 'foo', 'bar') # == False

#print grammar.match('127.0.0.1')
#print grammar.match('127.0.0.1', 'advertised-routes')
#print grammar.match('127.0.0.1', 'paths', '[A-Z]+')
#print grammar.match('127.0.0.1', 'paths', '.*')
#print grammar.match('127.0.0.1', 'policy')
#print grammar.match('127.0.0.1', 'policy', 'detail')
#print grammar.match('127.0.0.1', 'received')                   # == False
#print grammar.match('127.0.0.1', 'received', 'prefix-filter')  # == True
