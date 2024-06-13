#version 130

in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D tex;
uniform float time;

void main() {
    vec2 uv = texcoord;
    
    // Basic pixel sorting effect
    vec2 offset = vec2(sin(time + uv.y * 10.0) * 0.05, cos(time + uv.x * 10.0) * 0.05);
    vec4 color = texture(tex, uv + offset);
    
    // Simulate compression artifacts
    float compression = mod(time, 2.0) < 1.0 ? 0.1 : 0.05;
    color.r = floor(color.r / compression) * compression;
    color.g = floor(color.g / compression) * compression;
    color.b = floor(color.b / compression) * compression;
    
    // Advanced datamoshing effects
    // Displace pixels by sampling from a previous frame based on motion
    vec2 motion = vec2(sin(time + uv.y * 20.0) * 0.1, cos(time + uv.x * 20.0) * 0.1);
    vec4 motionColor = texture(tex, uv + motion);
    
    // Recycling pixels on screen rather than clearing each frame
    vec4 recycledColor = mix(color, motionColor, 0.5);
    
    // Quantizing motion vectors into blocks for a pixelated effect
    float blockSize = 0.01;
    vec2 blockUV = floor(uv / blockSize) * blockSize;
    vec4 blockColor = texture(tex, blockUV);
    
    // Adding noise to create more distortion
    float noise = (sin(dot(uv, vec2(12.9898, 78.233)) * 43758.5453) - 0.5) * 0.1;
    recycledColor.rgb += noise;
    
    fragColor = mix(recycledColor, blockColor, 0.5);
}