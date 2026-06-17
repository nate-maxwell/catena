#version 410 core

layout(triangles, equal_spacing, ccw) in;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform mat3 u_normal_matrix;
uniform sampler2D u_height_map;
uniform float u_displacement_scale;

in vec3 v_eval_position[];
in vec3 v_eval_normal[];
in vec2 v_eval_texcoord[];
in vec3 v_eval_tangent[];

out vec3 v_world_position;
out vec2 v_texcoord;
out mat3 v_tbn;

vec3 interpolate3(vec3 a, vec3 b, vec3 c) {
    return gl_TessCoord.x * a + gl_TessCoord.y * b + gl_TessCoord.z * c;
}

vec2 interpolate2(vec2 a, vec2 b, vec2 c) {
    return gl_TessCoord.x * a + gl_TessCoord.y * b + gl_TessCoord.z * c;
}

void main() {
    vec3 position = interpolate3(v_eval_position[0], v_eval_position[1], v_eval_position[2]);
    vec3 normal = normalize(interpolate3(v_eval_normal[0], v_eval_normal[1], v_eval_normal[2]));
    vec2 texcoord = interpolate2(v_eval_texcoord[0], v_eval_texcoord[1], v_eval_texcoord[2]);
    vec3 tangent = normalize(interpolate3(v_eval_tangent[0], v_eval_tangent[1], v_eval_tangent[2]));

    float height = texture(u_height_map, texcoord).r;
    vec3 displaced_position = position + normal * (height * u_displacement_scale);

    vec3 world_normal = normalize(u_normal_matrix * normal);
    vec3 world_tangent = normalize(u_normal_matrix * tangent);
    world_tangent = normalize(world_tangent - dot(world_tangent, world_normal) * world_normal);
    vec3 world_bitangent = cross(world_normal, world_tangent);
    v_tbn = mat3(world_tangent, world_bitangent, world_normal);

    vec4 world_position = u_model * vec4(displaced_position, 1.0);
    v_world_position = world_position.xyz;
    v_texcoord = texcoord;

    gl_Position = u_projection * u_view * world_position;
}
