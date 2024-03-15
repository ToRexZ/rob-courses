#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/development/hand_rl_ws/src/hand_prosthesis_rl_control_pkgs/thirdparty/point_cloud_ros"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/development/hand_rl_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/development/hand_rl_ws/install/lib/python3/dist-packages:/development/hand_rl_ws/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/development/hand_rl_ws/build" \
    "/usr/bin/python3" \
    "/development/hand_rl_ws/src/hand_prosthesis_rl_control_pkgs/thirdparty/point_cloud_ros/setup.py" \
     \
    build --build-base "/development/hand_rl_ws/build/hand_prosthesis_rl_control_pkgs/thirdparty/point_cloud_ros" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/development/hand_rl_ws/install" --install-scripts="/development/hand_rl_ws/install/bin"
