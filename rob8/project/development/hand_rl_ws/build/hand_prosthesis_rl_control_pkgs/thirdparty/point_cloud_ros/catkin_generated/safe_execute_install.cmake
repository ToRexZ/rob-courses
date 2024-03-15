execute_process(COMMAND "/development/hand_rl_ws/build/hand_prosthesis_rl_control_pkgs/thirdparty/point_cloud_ros/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/development/hand_rl_ws/build/hand_prosthesis_rl_control_pkgs/thirdparty/point_cloud_ros/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
