if("$ENV{ROS_DISTRO}" STREQUAL "foxy" OR "$ENV{ROS_DISTRO}" STREQUAL "galactic" OR "$ENV{ROS_DISTRO}" STREQUAL "humble" OR "$ENV{ROS_DISTRO}" STREQUAL "iron")
  message(STATUS "Using BehaviorTree.CPP V3")
  set(BT_LIB_NAME behaviortree_cpp_v3)
  set(BT_TARGET ${behaviortree_cpp_v3_TARGETS})
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBTV3")
else()
  message(STATUS "Using BehaviorTree.CPP V4")
  set(BT_LIB_NAME behaviortree_cpp)
  set(BT_TARGET behaviortree_cpp::behaviortree_cpp)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBTV4")
endif()

include_directories(.)

add_subdirectory(action)

# Test register
ament_add_gtest(test_register
  test_register.cpp
)
target_link_libraries(test_register
  ${BT_TARGET}
  rclcpp::rclcpp
)