#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D tex;
uniform float time;

void main()
{
    vec2 uv = TexCoords;
    vec4 color = texture(tex, uv);

    // Pixel sorting effect
    float threshold = 0.5;
    if (color.r > threshold)
    {
        uv.y += sin(uv.x * 10.0 + time) * 0.1;
    }
    else
    {
        uv.x += cos(uv.y * 10.0 + time) * 0.1;
    }

    // Compression artifacts simulation
    float block_size = 8.0;
    vec2 block_uv = floor(uv * block_size) / block_size;
    vec4 block_color = texture(tex, block_uv);

    // Blend the original color with the blocky color to simulate compression artifacts
    color = mix(color, block_color, 0.5);

    // Apply the final color
    FragColor = color;
}