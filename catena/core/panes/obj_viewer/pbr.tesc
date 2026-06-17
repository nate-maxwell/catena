#version 410 core

layout(vertices = 3) out;

const float TESSELLATION_LEVEL = 8.0;

in vec3 v_control_position[];
in vec3 v_control_normal[];
in vec2 v_control_texcoord[];
in vec3 v_control_tangent[];

out vec3 v_eval_position[];
out vec3 v_eval_normal[];
out vec2 v_eval_texcoord[];
out vec3 v_eval_tangent[];

void main() {
    v_eval_position[gl_InvocationID] = v_control_position[gl_InvocationID];
    v_eval_normal[gl_InvocationID] = v_control_normal[gl_InvocationID];
    v_eval_texcoord[gl_InvocationID] = v_control_texcoord[gl_InvocationID];
    v_eval_tangent[gl_InvocationID] = v_control_tangent[gl_InvocationID];

    if (gl_InvocationID == 0) {
        gl_TessLevelInner[0] = TESSELLATION_LEVEL;
        gl_TessLevelOuter[0] = TESSELLATION_LEVEL;
        gl_TessLevelOuter[1] = TESSELLATION_LEVEL;
        gl_TessLevelOuter[2] = TESSELLATION_LEVEL;
    }
}
