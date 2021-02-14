import matplotlib.pyplot as plt
from mpld3 import fig_to_html, plugins
fig, ax = plt.subplots()
lines = ax.plot_date(range(10), range(10))
plugins.clear(fig)
plugins.connect(fig, plugins.Reset(), plugins.MousePosition())
with open('index.html', 'w') as f:
    f.write(fig_to_html(fig))