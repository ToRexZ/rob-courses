#include <functional>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3>
#include <thread>
#include "ros/ros.h"
#include "ros/callback_queue.h"
#include "ros/subscribe_options.h"
#include "std_msgs/Float.h"
#include "geometry_msgs/Twist.h"
#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>


namespace gazebo
{
    class MoveObject : ModelPlugin{
        public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
        {
            // Store the pointer to the model
            this->model = _parent;

            this->updateConnection = event::Events::ConnectWorldUpdateBegin(
                std::bind(&MoveObject::OnUpdate, this);
            )

            this->prev_secs = ros::Time::now().toSec();

            // Topic name
            std::string plannar_pos_topicName = "/cmd_vel"
        }

        // Pointer to the object
        private: physics::ModelPtr model;

        // Pointer to the object connection
        private: event::ConncectionPtr updateConnection;

        private: double prev_secs;
    }
} // namespace gazebo
