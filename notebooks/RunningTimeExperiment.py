from typing import List, Dict, Tuple, Optional, Any, Callable
from datetime import datetime
from collections import defaultdict
import sys

# common imports
from random import Random  # pylint: disable=unused-import
from math import log, sqrt  # pylint: disable=unused-import,no-name-in-module
from functools import partial  # pylint: disable=unused-import

import plotly.graph_objects as go  # type: ignore
from plotly.colors import qualitative  # type: ignore

from IPython.display import display, Image  # type: ignore


def show_figure(fig, image_path: Optional[str] = None):
    """Show a Plotly figure."""

    if image_path is None:
        fig.show()
    else:
        fig.write_image(image_path)
        display(Image(image_path))


class RunningTimeExperiment:
    """Manages running time experiments."""

    def __init__(self):
        self.instances: List[Tuple[int, Any]] = []
        self.algorithms: List[Tuple[str, Callable[[Any], Any]]] = []
        self.result: Dict[str, Dict[int, List[float]]] = defaultdict(lambda: defaultdict(list))

    def add_instance(self, input_size: int, instance: Any):
        """Adds one problem instance."""
        self.instances += [(input_size, instance)]

    def add_algorithm(self, name: str, func: Callable[[Any], Any]):
        """Adds one algorithm implementation."""
        self.algorithms += [(name, func)]

    def validate(self) -> None:
        """Makes sure that all algorithms output the same solution."""
        assert self.instances and self.algorithms

        sys.stdout.write('Validating algorithms...')
        inst = self.instances[0][1]  # use the first instance
        expected = self.algorithms[0][1](inst)
        assert all(f(inst) == expected for _,
                   f in self.algorithms[1:]), 'Algorithm is not correct'

        print('ok')

    def run(self, num_iterations=3):
        """Runs experiments."""

        self.result.clear()

        for alg, f in self.algorithms:
            sys.stdout.write(f'Running measurment (algorithm={alg}): ')

            for n, inst in self.instances:
                sys.stdout.write(f'|n={n}:')
                for _ in range(num_iterations):
                    start = datetime.now()
                    f(inst)
                    elapsed = datetime.now() - start
                    self.result[alg][n] += [elapsed.total_seconds()]
                    sys.stdout.write('.')
            print('|')

    def create_figure(
        self,
        title: str,
        width=800,
        height=800,
        xscale='log',
        yscale='log',
    ) -> None:
        """Creates a Plotly figure based on the experiment results."""

        fig = go.Figure()

        for i, (alg, _) in enumerate(self.algorithms):
            colors = qualitative.Plotly[i], qualitative.Plotly[(
                i + 5) % len(qualitative.Plotly)]

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
