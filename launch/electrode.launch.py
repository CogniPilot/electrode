from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution, NotSubstitution, AndSubstitution, OrSubstitution
from launch.actions import DeclareLaunchArgument, Shutdown, LogInfo, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import LaunchConfigurationEquals, IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


ARGUMENTS = [

    # launch arguments
    DeclareLaunchArgument('sim',
        default_value=['false'],
        description='use with simulation'
    ),

    DeclareLaunchArgument('rviz2',
        default_value='true',
        choices=['true', 'false'],
        description='use rviz2 for gui.'
    ),

    DeclareLaunchArgument('joy',
        default_value='true',
        choices=['true', 'false'],
        description='use joystick'
    ),

    DeclareLaunchArgument('controller',
        default_value='f310',
        choices=['f310', 'ps4'],
        description='which controller you are using'
    ),

    DeclareLaunchArgument('log_level',
        default_value=['warn'],
        description='Logging level'
    ),

    DeclareLaunchArgument('vehicle',
        default_value=['b3rb'],
        description='vehicle'
    ),
]

def generate_launch_description():

    joy = Node(
        package='joy',
        output='log',
        executable='joy_node',
        condition=IfCondition(LaunchConfiguration('joy')),
        arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
        parameters=[
            {'use_sim_time': LaunchConfiguration('sim')},
            {'coalesce_interval_ms': 50},
            {'autorepeat_rate': 20.0},
            {'deadzone': 0.02},
            ],
        on_exit=Shutdown()
    )

    joy_to_input = Node(
       condition=IfCondition(LaunchConfiguration('joy')),
       name='joy_to_input',
       package='electrode',
       output='screen',
       executable=['joy_to_input_', LaunchConfiguration('controller'), '.py'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz2')),
        arguments=[
            '-d', [PathJoinSubstitution([FindPackageShare('electrode'), 'config',
            LaunchConfiguration('vehicle')]), '.rviz'], '--ros-args', '--log-level',
            LaunchConfiguration('log_level')],
        parameters=[{'use_sim_time': LaunchConfiguration('sim')}],
        on_exit=Shutdown(),
    )


    return LaunchDescription(ARGUMENTS + [
        joy,
        joy_to_input,
        rviz_node,
    ])
