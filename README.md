# Setzer

Simple yet full-featured LaTeX editor for the GNU/Linux desktop, written in Python with Gtk.

Website: <a href="https://www.cvfosammmm.org/setzer/">https://www.cvfosammmm.org/setzer/</a>

<a href="https://flathub.org/apps/details/org.cvfosammmm.Setzer"><img src="https://www.cvfosammmm.org/setzer/images/flathub-badge-en.svg" width="150" height="50"></a>

![Screenshot](https://github.com/cvfosammmm/Setzer/raw/master/data/screenshot.png)

Setzer is a LaTeX editor written in Python with Gtk. I'm happy if you give it a try and provide feedback via the issue tracker here on GitHub, be it about design, code architecture, bugs, feature requests, ... I try to respond to issues immediately.

## Installing Setzer

### Flatpak

Install with: `flatpak install flathub org.cvfosammmm.Setzer`

### AUR

Git version available <a href="https://aur.archlinux.org/packages/setzer-git/">here</a>.

### Manual

I develop Setzer on Debian and that's what I tested it with. On Debian derivatives (like Ubuntu) it should probably work the same. On distributions other than Debian and Debian derivatives it should work more or less the same. If you want to run Setzer from source on another distribution and don't know how please open an issue here on GitHub. I will then try to provide instructions for your system.

1. Install prerequisite packages:<br />
Debian: `libgtk-3-dev libgtksourceview-3.0-dev libpoppler-glib-dev libgspell-1-dev python3-xdg`

2. Download und Unpack the <a href="https://github.com/cvfosammmm/Setzer/releases">latest Setzer release </a>: `tar -xf Setzer-<version>.tar.gz && cd Setzer-<version>`

3. Run meson: `meson builddir`<br />
Note: Some distributions (like Debian) may not include systemwide installations of Python modules which aren't installed from distribution packages. In this case the program won't find any modules, however you can change the installation prefix to your home directory with `meson builddir --prefix=~/.local`.

4. Install Setzer with: `ninja install -C builddir`<br />
Or run it without installation: `./scripts/setzer.dev`

## Building your documents from within the app

To build your documents from within the app you can choose from four build commands: `latexmk`, `pdflatex`, `xelatex` and `lualatex`. Make sure that you have the LaTeX builder you use installed.
I recommend building with `latexmk`, which can be configured to use any build method in a `latexmkrc` file (see `man latexmk`).

## Getting in touch

Setzer development / discussion takes place on GitHub at [https://github.com/cvfosammmm/setzer](https://github.com/cvfosammmm/setzer "project url").

## Acknowledgements

Setzer draws some inspiration from other LaTeX editors. For example the symbols in the sidebar are mostly the same as in Latexila, though I continue to change / reorganize them. The autocomplete suggestions are mostly the same as in Texmaker. I took some icons from Gnome Builder. Syntax highlighting schemes are based on the Tango scheme in GtkSourceView and the Gnome Builder Scheme.

## License

Setzer is licensed under GPL version 3 or later. See the COPYING file for details.
