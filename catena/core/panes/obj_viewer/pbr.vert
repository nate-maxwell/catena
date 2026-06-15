#version 330 core

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec2 in_texcoord;
layout(location = 3) in vec3 in_tangent;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform mat3 u_normal_matrix;

out vec3 v_world_position;
out vec2 v_texcoord;
out mat3 v_tbn;

void main() {
    vec4 world_position = u_model * vec4(in_position, 1.0);
    v_world_position = world_position.xyz;
    v_texcoord = in_texcoord;

    vec3 normal = normalize(u_normal_matrix * in_normal);
    vec3 tangent = normalize(u_normal_matrix * in_tangent);
    tangent = normalize(tangent - dot(tangent, normal) * normal);
    vec3 bitangent = cross(normal, tangent);
    v_tbn = mat3(tangent, bitangent, normal);

    gl_Position = u_projection * u_view * world_position;
}
