#version 410 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec2 in_texcoord;
layout(location = 3) in vec3 in_tangent;

out vec3 v_control_position;
out vec3 v_control_normal;
out vec2 v_control_texcoord;
out vec3 v_control_tangent;

void main() {
    v_control_position = in_position;
    v_control_normal = in_normal;
    v_control_texcoord = in_texcoord;
    v_control_tangent = in_tangent;
}
