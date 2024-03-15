#include <functional>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Pose3.hh>

namespace gazebo
{
    class ModelPush : public ModelPlugin{
        virtual ~ModelPush(){
            if (this->updateConnection)
                this->updateConnection.reset();
        }
        

        public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/) 
        {
            // Store the pointer to the model
            this->model = _parent;

            // Listen to the update event. This event is broadcast every simulation iteration.
            this->updateConnection = event::Events::ConnectWorldUpdateBegin(
                std::bind(&ModelPush::OnUpdate, this));

            // Get Link of the model
            this->link = this->model->GetLink("link");

            // Check if the link is valid
            if (!this->link)
            { 
                gzerr << "link is invalid" << std::endl;
                return;
            }

        }
        public: void OnUpdate()
        {
            // Get the model's current pose
            ignition::math::Pose3d pose = this->model->WorldPose();

            // Extract the position components
            ignition::math::Vector3d position = pose.Pos();

            // Print the position
            std::cout << "Model position: x=" << position.X() << ", y=" << position.Y() << ", z=" << position.Z() << std::endl;

            // Apply a small linear velocity to the model.
            this->model->SetLinearVel(ignition::math::Vector3d(0, 0, 0.1));

            // this->link->AddForce(ignition::math::Vector3d(0, 0, 100));
        }

        // Pointer to the model
        private: physics::ModelPtr model;

        // Pointer to the link
        physics::LinkPtr link;

        // Pointer to the update event connection
        private: event::ConnectionPtr updateConnection;
    };
    GZ_REGISTER_MODEL_PLUGIN(ModelPush);
} // namespace gazebo
