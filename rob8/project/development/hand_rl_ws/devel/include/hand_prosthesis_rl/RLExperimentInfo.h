// Generated by gencpp from file hand_prosthesis_rl/RLExperimentInfo.msg
// DO NOT EDIT!


#ifndef HAND_PROSTHESIS_RL_MESSAGE_RLEXPERIMENTINFO_H
#define HAND_PROSTHESIS_RL_MESSAGE_RLEXPERIMENTINFO_H


#include <string>
#include <vector>
#include <memory>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace hand_prosthesis_rl
{
template <class ContainerAllocator>
struct RLExperimentInfo_
{
  typedef RLExperimentInfo_<ContainerAllocator> Type;

  RLExperimentInfo_()
    : episode_number(0)
    , episode_reward(0.0)  {
    }
  RLExperimentInfo_(const ContainerAllocator& _alloc)
    : episode_number(0)
    , episode_reward(0.0)  {
  (void)_alloc;
    }



   typedef int32_t _episode_number_type;
  _episode_number_type episode_number;

   typedef float _episode_reward_type;
  _episode_reward_type episode_reward;





  typedef boost::shared_ptr< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> const> ConstPtr;

}; // struct RLExperimentInfo_

typedef ::hand_prosthesis_rl::RLExperimentInfo_<std::allocator<void> > RLExperimentInfo;

typedef boost::shared_ptr< ::hand_prosthesis_rl::RLExperimentInfo > RLExperimentInfoPtr;
typedef boost::shared_ptr< ::hand_prosthesis_rl::RLExperimentInfo const> RLExperimentInfoConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator1> & lhs, const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator2> & rhs)
{
  return lhs.episode_number == rhs.episode_number &&
    lhs.episode_reward == rhs.episode_reward;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator1> & lhs, const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace hand_prosthesis_rl

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
{
  static const char* value()
  {
    return "117729220546455cc216a7df0b6e91d0";
  }

  static const char* value(const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0x117729220546455cULL;
  static const uint64_t static_value2 = 0xc216a7df0b6e91d0ULL;
};

template<class ContainerAllocator>
struct DataType< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
{
  static const char* value()
  {
    return "hand_prosthesis_rl/RLExperimentInfo";
  }

  static const char* value(const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
{
  static const char* value()
  {
    return "int32 episode_number\n"
"float32 episode_reward\n"
;
  }

  static const char* value(const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.episode_number);
      stream.next(m.episode_reward);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct RLExperimentInfo_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::hand_prosthesis_rl::RLExperimentInfo_<ContainerAllocator>& v)
  {
    s << indent << "episode_number: ";
    Printer<int32_t>::stream(s, indent + "  ", v.episode_number);
    s << indent << "episode_reward: ";
    Printer<float>::stream(s, indent + "  ", v.episode_reward);
  }
};

} // namespace message_operations
} // namespace ros

#endif // HAND_PROSTHESIS_RL_MESSAGE_RLEXPERIMENTINFO_H
