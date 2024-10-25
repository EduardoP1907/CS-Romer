import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import asarray as ar
from scipy import exp

class ColormapManager:
    """
    Clase para gestionar colormaps disponibles.
    """
    def __init__(self):
        self.cmaps = [
            "magma", "inferno", "inferno_r", "plasma", "viridis",
            "bone", "afmhot", "gist_heat", "CMRmap", "gnuplot",
            "Blues_r", "Purples_r", "ocean", "hot", "seismic_r", "ocean_r"
        ]

    def get_colormaps(self):
        return self.cmaps


class DataConfig:
    """
    Clase para configurar los ejes de los datos con el encabezado.
    """
    def __init__(self, data, header, units="degrees"):
        self.data = data
        self.header = header
        self.units = units
        self.u_factor = self._set_units_factor()

    def _set_units_factor(self):
        """
        Configura el factor de conversión basado en las unidades proporcionadas.
        """
        if self.units == "arcmin":
            return 60.0
        elif self.units == "arcsec":
            return 3600.0
        elif self.units == "rad":
            return np.pi / 180.0
        return 1.0

    def config_axes(self):
        """
        Configura los ejes x e y basados en los datos y el encabezado.
        """
        x = self.data.shape[0]
        y = self.data.shape[1]
        dx = self.header["cdelt1"] * self.u_factor
        dy = self.header["cdelt2"] * self.u_factor
        x = ar(range(x)) * dx
        y = ar(range(y)) * dy
        x1 = (self.header["crpix1"] - 1.0) * np.abs(dx)
        y1 = (self.header["crpix2"] - 1.0) * dy
        x = np.arange(x1, -x1 - dx, -dx)
        y = np.arange(-y1, y1 + dy, dy)
        return [x, y, x1, y1]


class ColorBarManager:
    """
    Clase para manejar la creación y configuración de barras de color.
    """
    def __init__(self, mappable, title="", location="right"):
        self.mappable = mappable
        self.title = title
        self.location = location

    def create_colorbar(self):
        """
        Crea una barra de color para la imagen proporcionada.
        """
        last_axes = plt.gca()
        ax = self.mappable.axes
        fig = ax.figure
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(self.location, size="5%", pad=0.05)
        cbar = fig.colorbar(self.mappable, cax=cax, extend="both")
        cbar.set_label(self.title)
        plt.sca(last_axes)
        return cbar


class AnimationCreator:
    """
    Clase para crear animaciones con los datos proporcionados.
    """
    def __init__(self, header, cube, cube_axis, xlabel="", ylabel="", cblabel="", title="", cmap="Spectral", title_pad=0.0, vmin=None, vmax=None):
        self.header = header
        self.cube = cube
        self.cube_axis = cube_axis
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.cblabel = cblabel
        self.title = title
        self.cmap = cmap  # El colormap ahora es un argumento configurable.
        self.title_pad = title_pad
        self.vmin = vmin
        self.vmax = vmax

        if self.vmin is None or self.vmax is None:
            self.vmax = np.amax(np.amax(cube, axis=0))
            self.vmin = np.amin(np.amin(cube, axis=0))

    def create_animation(self, output_video="dynamic_images.mp4", fps=30, interval=50, repeat=False):
        """
        Crea una animación y la guarda como un archivo de video.
        """
        fig, ax = plt.subplots()
        data_config = DataConfig(self.cube[0], self.header)
        axes = data_config.config_axes()

        cv0 = self.cube[0]
        im = ax.imshow(
            cv0,
            origin="lower",
            aspect="equal",
            cmap=self.cmap,  # Usando el colormap seleccionado
            extent=[axes[2], -axes[2], -axes[3], axes[3]],
        )
        ax.set_title(self.title, pad=self.title_pad)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        # Gestión de la barra de color
        colorbar_mgr = ColorBarManager(im, self.cblabel)
        cb = colorbar_mgr.create_colorbar()
        cb.locator = ticker.MaxNLocator(nbins=3)
        cb.update_ticks()

        def animate(i):
            arr = self.cube[i]
            phi_i = self.cube_axis[i]
            # vmax     = np.max(arr)
            # vmin     = np.min(arr)
            ax.set_title(f"Faraday Depth Spectrum at {phi_i:.4f} rad/m^2")
            # time_text.set_text("Phi: {0}".format(phi_i))
            im.set_data(arr)
            im.set_clim(self.vmin, self.vmax)

        ani = animation.FuncAnimation(
            fig,
            animate,
            frames=len(self.cube),
            interval=interval,
            repeat=repeat,
            blit=False,
            repeat_delay=1000,
        )
        ani.save(output_video)

colormap_manager = ColormapManager()
header = {"cdelt1": 0.5, "cdelt2": 0.5, "crpix1": 50, "crpix2": 50}
cube = np.random.rand(100, 50, 50)
cube_axis = np.linspace(-10, 10, 100)

animation_creator = AnimationCreator(
    header, cube, cube_axis, "X-axis", "Y-axis", "Color Bar", 
    "Sample Animation", cmap=colormap_manager.get_colormaps()[3]  # Usando "plasma"
)
animation_creator.create_animation()
