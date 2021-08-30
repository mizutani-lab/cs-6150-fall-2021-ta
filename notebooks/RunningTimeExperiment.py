from typing import List, Tuple, Optional, Union, Any, Callable
from random import Random
from datetime import datetime
from math import log, sqrt
from functools import partial
from collections import defaultdict
import sys

import plotly.graph_objects as go
from plotly.colors import qualitative

from IPython.display import display, HTML, Markdown, Image


def show_figure(fig, image_path: Optional[str] = None):
    if image_path is None:
        fig.show()
    else:
        fig.write_image(image_path)
        display(Image(image_path))


class RunningTimeExperiment:
    def __init__(self):
        self.instances: List[Tuple[int, Any]] = []
        self.algorithms: List[Tuple[str, Callable[[Any], Any]]] = []
        self.result: Dict[str, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))

    def add_instance(self, input_size: float, instance: Any):
        self.instances += [(input_size, instance)]

    def add_algorithm(self, name: str, func: Callable[[Any], Any]):
        self.algorithms += [(name, func)]

    def validate(self) -> bool:
        """Make sure that all algorithms output the same solution."""
        assert self.instances and self.algorithms

        sys.stdout.write('Validating algorithms...')
        inst = self.instances[0][1]  # use the first instance
        expected = self.algorithms[0][1](inst)
        assert all(f(inst) == expected for _, f in self.algorithms[1:]), 'Algorithm is not correct'
        
        print('ok')
    
    def run(self, num_iterations=3):
        self.result.clear()

        for alg, f in self.algorithms:
            sys.stdout.write(f'Running measurment (algorithm={alg}): ')

            for n, inst in self.instances:
                sys.stdout.write(f'|n={n}:')
                for iteration in range(3):
                    start = datetime.now()
                    f(inst)
                    elapsed = datetime.now() - start
                    self.result[alg][n] += [elapsed.total_seconds()]
                    sys.stdout.write('.')
            print('|')
    
    def create_figure(self,
        title: str,
        width=800,
        height=800,
        xscale='log',
        yscale='log',
    ) -> None:
        fig = go.Figure()

        for i, (alg, _) in enumerate(self.algorithms):
            colors = qualitative.Plotly[i], qualitative.Plotly[(i + 5) % len(qualitative.Plotly)]

            xs, ys, axs, ays = [], [], [], []

            for n, _ in self.instances:
                runtime = self.result[alg][n]
                xs += [n] * len(runtime)
                ys += runtime
                axs += [n]
                ays += [sum(runtime) / len(runtime)]  # take average

            # add violin trace
            fig.add_trace(go.Violin(
                x=xs,
                y=ys,
                name=alg,
                box_visible=True,
                meanline_visible=True,
                showlegend=False,
                line=dict(color=colors[0], width=1),
                fillcolor=colors[1],
                opacity=0.7,
            ))

            # add line trace
            fig.add_trace(go.Scatter(
                x=axs,
                y=ays,
                mode='lines',
                name=alg,
                line=dict(color=colors[0])
            ))

        fig.update_xaxes(title='Input size: n' + (' [log scale]' if xscale == 'log' else ''), type=xscale)
        fig.update_yaxes(title='Running time (sec)' + (' [log scale]' if yscale == 'log' else ''), type=yscale)
        fig.update_layout(dict(title=title, showlegend=True, width=width, height=height))
        return fig