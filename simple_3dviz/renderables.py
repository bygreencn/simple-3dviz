"""Renderables represent objects that can be rendered in a scene."""

import numpy as np


from .programs import uniform_value


class Renderable(object):
    """Represent something that can be rendered."""
    def init(self, ctx):
        """Initialize the renderable with the moderngl context."""
        raise NotImplementedError()

    def update_uniforms(self, uniforms):
        """Update any uniforms that are provided from somewhere else.
        
        The object is free to update its own programs' uniform values as well.
        Also since the program can be shared, the uniforms might be updated
        from another object.

        Arguments
        ---------
            uniforms: list of tuples
        """
        pass

    def render(self):
        """Render whatever this represents."""
        raise NotImplementedError()


class Circle(Renderable):
    def __init__(self, position=(0., 0.), radius=0.5, color=(0, 0, 0)):
        self._vertices = np.array([[-1,  1],
                                   [ 1,  1],
                                   [ 1, -1],
                                   [ 1, -1],
                                   [-1, -1],
                                   [-1,  1]], dtype="float32")
        self._radius = radius
        self._position = position
        self._color = color

        self._prog = None
        self._vao = None

        self.position = uniform_value(self, "_prog", "_position")
        self.radius = uniform_value(self, "_prog", "_radius")
        self.color = uniform_value(self, "_prog", "_color")

    def init(self, ctx):
        self._prog = ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_vert;
                out vec2 v_vert;

                void main() {
                    v_vert = in_vert;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
                """,
            fragment_shader="""
                #version 330

                uniform float radius;
                uniform vec2 position;
                uniform vec3 color;
                in vec2 v_vert;
                out vec4 f_color;

                void main() {
                    float d = distance(v_vert, position);
                    float e = clamp(0.05*radius, 0.05, 0.1);
                    if (d < radius+e) {
                        float s = 1-smoothstep(radius-e, radius+e, d)/(radius+e);
                        f_color = vec4(color, s);
                    } else {
                        discard;
                    }
                }
                """
        )
        self._prog["radius"].value = self._radius
        self._prog["position"].value = self._position
        self._prog["color"].value = self._color
        vbo = ctx.buffer(self._vertices.tobytes())
        self._vao = ctx.simple_vertex_array(self._prog, vbo, "in_vert")

    def render(self):
        self._vao.render()
