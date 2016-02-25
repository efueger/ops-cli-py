
project("opscli-command" NONE)

enable_testing()
cmake_minimum_required(VERSION 2.8)

function(test module)
  add_test(
    NAME ${module} COMMAND python ${module}_test.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
endfunction(test)

test("command")
test("context")
test("match")
test("parse")
test("token")
