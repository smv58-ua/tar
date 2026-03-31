#!/bin/bash
set -e

# Initialize rosdep (skip if already initialized)
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update || true

# Build the ROS 2 workspace
source /opt/ros/humble/setup.bash
cd /workspace
rosdep install -i --from-path src --rosdistro humble -y --skip-keys "battery_interfaces"
colcon build

# Add sourcing to bashrc (if not already present)
if ! grep -q "source /opt/ros/humble/setup.bash" ~/.bashrc; then
  cat >> ~/.bashrc << 'EOF'

# ROS 2 Humble environment
source /opt/ros/humble/setup.bash
source /workspace/install/local_setup.bash
export LIBGL_ALWAYS_SOFTWARE=1
EOF
fi
