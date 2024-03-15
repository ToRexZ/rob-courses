#include <gazebo/gazebo.hh>

// All gazebo plugins must be in a gazebo namespace
namespace gazebo 
{
    // Each plugin must inherit from a plugin type, in this case it is WorldPlugin
    class WorldPluginTutorial : public WorldPlugin
    {
    public: WorldPluginTutorial() : WorldPlugin()
        {
            printf("Hello World!\n");
        }

    public: void Load(physics::WorldPtr _world, sdf::ElementPtr _sdf)
        {
        }
    };

    GZ_REGISTER_WORLD_PLUGIN(WorldPluginTutorial)
} // namespace gazebo
