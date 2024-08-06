# SPDX-FileCopyrightText: Copyright (c) 2022-2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

list(APPEND CMAKE_MESSAGE_CONTEXT "tests")

find_package(pybind11 REQUIRED)

include(GoogleTest)

# Cuda Test
add_executable(test_cuda
  test_cuda.cu
)

target_link_libraries(test_cuda
  PRIVATE
    GTest::gtest
    GTest::gtest_main
)

gtest_discover_tests(test_cuda)

set_target_properties(test_cuda
  PROPERTIES
    INSTALL_RPATH "$ORIGIN/.."
    CUDA_STANDARD 17
    CUDA_STANDARD_REQUIRED ON
)

# Morpheus Test Utilities
add_library(
  morpheus_test_utilities
    test_utils/common.cpp
    test_utils/tensor_utils.cpp
)

target_link_libraries(
  morpheus_test_utilities
  PUBLIC
    GTest::gtest
    morpheus
)

# Ensure that the python executable is defined for the tests
target_compile_definitions(morpheus_test_utilities
  PRIVATE
    PYTHON_EXECUTABLE="${PYTHON_EXECUTABLE}"
)

# Morpheus Tests
function(add_morpheus_test)
  set(options)
  set(oneValueArgs NAME)
  set(multiValueArgs FILES)
  cmake_parse_arguments(
    MORPHEUS_TEST "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN}
  )

  add_executable(test_${MORPHEUS_TEST_NAME}
    ${MORPHEUS_TEST_FILES}
  )

  target_link_libraries(test_${MORPHEUS_TEST_NAME}
    PRIVATE
      GTest::gtest_main
      morpheus_test_utilities
      pybind11::embed
      TritonClient::httpclient_static
  )

  gtest_discover_tests(test_${MORPHEUS_TEST_NAME})

  set_target_properties(test_${MORPHEUS_TEST_NAME}
    PROPERTIES
      INSTALL_RPATH "$ORIGIN/.."
      CUDA_STANDARD 17
      CUDA_STANDARD_REQUIRED ON
  )
endfunction()

add_morpheus_test(
  NAME llm
  FILES
    llm/test_llm_context.cpp
    llm/test_llm_engine.cpp
    llm/test_llm_node.cpp
    llm/test_llm_node_runner.cpp
    llm/test_llm_task.cpp
    llm/test_llm_task_handler_runner.cpp
    llm/test_utils.cpp
)

list(POP_BACK CMAKE_MESSAGE_CONTEXT)
