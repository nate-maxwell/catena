#version 330 core

in vec3 v_world_position;
in vec2 v_texcoord;
in mat3 v_tbn;

out vec4 out_color;

uniform sampler2D u_albedo_map;
uniform sampler2D u_metallic_map;
uniform sampler2D u_roughness_map;
uniform sampler2D u_normal_map;
uniform sampler2D u_ao_map;
uniform sampler2D u_height_map;

uniform vec3 u_camera_position;
uniform vec3 u_light_direction;
uniform vec3 u_light_color;
uniform vec3 u_ambient_color;

uniform float u_height_scale;

const float PI = 3.14159265359;

float distribution_ggx(vec3 normal, vec3 halfway, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float n_dot_h = max(dot(normal, halfway), 0.0);
    float n_dot_h2 = n_dot_h * n_dot_h;
    float denom = n_dot_h2 * (a2 - 1.0) + 1.0;
    denom = PI * denom * denom;
    return a2 / max(denom, 0.0000001);
}

float geometry_schlick_ggx(float n_dot_v, float roughness) {
    float r = roughness + 1.0;
    float k = (r * r) / 8.0;
    return n_dot_v / max(n_dot_v * (1.0 - k) + k, 0.0000001);
}

float geometry_smith(vec3 normal, vec3 view, vec3 light, float roughness) {
    float n_dot_v = max(dot(normal, view), 0.0);
    float n_dot_l = max(dot(normal, light), 0.0);

    return geometry_schlick_ggx(n_dot_v, roughness)
        * geometry_schlick_ggx(n_dot_l, roughness);
}

vec3 fresnel_schlick(float cos_theta, vec3 f0) {
    return f0 + (1.0 - f0) * pow(clamp(1.0 - cos_theta, 0.0, 1.0), 5.0);
}

vec3 safe_normalize(vec3 value, vec3 fallback) {
    float length_squared = dot(value, value);

    if (
        length_squared < 0.000001 ||
        value.x != value.x ||
        value.y != value.y ||
        value.z != value.z
    ) {
        return fallback;
    }

    return value * inversesqrt(length_squared);
}

void main() {
    vec2 texcoord = v_texcoord;

    vec3 albedo = texture(u_albedo_map, texcoord).rgb;
    float roughness = clamp(texture(u_roughness_map, texcoord).r, 0.04, 1.0);
    float metallic = clamp(texture(u_metallic_map, texcoord).r, 0.0, 1.0);
    float ambient_occlusion = clamp(texture(u_ao_map, texcoord).r, 0.0, 1.0);

    vec3 geometric_normal = safe_normalize(v_tbn[2], vec3(0.0, 0.0, 1.0));

    vec3 tangent_normal = texture(u_normal_map, texcoord).rgb * 2.0 - 1.0;
    tangent_normal = safe_normalize(tangent_normal, vec3(0.0, 0.0, 1.0));

    vec3 normal = safe_normalize(v_tbn * tangent_normal, geometric_normal);

    vec3 view = safe_normalize(
        u_camera_position - v_world_position,
        vec3(0.0, 0.0, 1.0)
    );
    vec3 light = safe_normalize(-u_light_direction, vec3(0.0, 1.0, 0.0));
    vec3 halfway = safe_normalize(view + light, normal);

    vec3 f0 = mix(vec3(0.04), albedo, metallic);

    float ndf = distribution_ggx(normal, halfway, roughness);
    float geometry = geometry_smith(normal, view, light, roughness);
    vec3 fresnel = fresnel_schlick(max(dot(halfway, view), 0.0), f0);

    vec3 numerator = ndf * geometry * fresnel;
    float denominator =
        4.0
        * max(dot(normal, view), 0.0)
        * max(dot(normal, light), 0.0)
        + 0.0001;
    vec3 specular = numerator / denominator;

    vec3 k_diffuse = (vec3(1.0) - fresnel) * (1.0 - metallic);
    float n_dot_l = max(dot(normal, light), 0.0);

    vec3 radiance = u_light_color * n_dot_l;
    vec3 direct_light = (k_diffuse * albedo / PI + specular) * radiance;

    vec3 ambient = u_ambient_color * albedo * ambient_occlusion;

    vec3 final_color = ambient + direct_light;

    final_color = max(final_color, vec3(0.0));
    final_color = final_color / (final_color + vec3(1.0));
    final_color = pow(final_color, vec3(1.0 / 2.2));

    out_color = vec4(final_color, 1.0);
}
