project("opscli" NONE)

enable_testing()
cmake_minimum_required(VERSION 2.8)

function(test module)
  add_test(
    NAME ${module}
    COMMAND coverage run --source=${CMAKE_CURRENT_SOURCE_DIR}
      -p ${CMAKE_CURRENT_SOURCE_DIR}/${module}_test.py
    WORKING_DIRECTORY ${PROJECT_BINARY_DIR})
  set_tests_properties(${module}
    PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}")
endfunction(test)

add_subdirectory(opscli)
