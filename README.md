# Setzer

Simple yet full-featured LaTeX editor for the GNU/Linux desktop, written in Python with Gtk.

Website: <a href="https://www.cvfosammmm.org/setzer/">https://www.cvfosammmm.org/setzer/</a>

<a href="https://flathub.org/apps/details/org.cvfosammmm.Setzer"><img src="https://www.cvfosammmm.org/setzer/images/flathub-badge-en.svg" width="150" height="50"></a>

![Screenshot](https://github.com/cvfosammmm/Setzer/raw/master/data/screenshot.png)

Setzer is a LaTeX editor written in Python with Gtk. I'm happy if you give it a try and provide feedback via the issue tracker here on GitHub, be it about design, code architecture, bugs, feature requests, ... I try to respond to issues immediately.

## Running Setzer with Gnome Builder

To run Setzer with Gnome Builder just click the "Clone.." button on the start screen, paste in the url (https://github.com/cvfosammmm/Setzer.git), click on "Clone" again, wait for it to download and hit the play button. It will build Setzer and its dependencies and then launch it.

Warning: Building Setzer this way may take a long time (~ 30 minutes on my laptop).

## Running Setzer on Debian (probably Ubuntu, other Distributions too?)

This way is probably a bit faster and may save you some disk space. I develop Setzer on Debian and that's what I tested it with. On Debian derivatives (like Ubuntu) it should probably work the same. On distributions other than Debian and Debian derivatives it should work more or less the same. If you want to run Setzer from source on another distribution and don't know how please open an issue here on GitHub. I will then try to provide instructions for your system.

1. Run the following command to install prerequisite Debian packages:<br />
`apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-gtksource-4 gir1.2-gspell-1 gir1.2-poppler-0.18 python3-xdg`

2. Download und Unpack Setzer from GitHub

3. cd to Setzer folder

4. Run meson: `meson builddir`

5. Install Setzer with: `ninja install -C builddir`<br />
Or run it locally: `./scripts/setzer.dev`

Note: Some distributions may not include systemwide installations of Python modules which aren't installed from distribution packages. In this case, you want to install Setzer in your home directory with `meson builddir --prefix=~/.local`.

## Building your documents from within the app

To build your documents from within the app you have to specify a build command. I recommend building with latexmk, which on Debian can be installed like so:
`apt-get install latexmk`

To specify a build command open the "Preferences" dialog and type in the command you want to use under "Build command", which in the case of latexmk could be the following:
`latexmk -synctex=1 -interaction=nonstopmode -pdf -output-directory=%OUTDIR %FILENAME`

## Getting in touch

Setzer development / discussion takes place on GitHub at [https://github.com/cvfosammmm/setzer](https://github.com/cvfosammmm/setzer "project url").

## Acknowledgements

Setzer draws some inspiration from other LaTeX editors. For example the symbols in the sidebar are mostly the same as in Latexila, though I continue to change / reorganize them. The autocomplete suggestions are mostly the same as in Texmaker. I took some icons from Gnome Builder. Syntax highlighting schemes are based on the Tango scheme in GtkSourceView and the Gnome Builder Scheme.

## License

Setzer is licensed under GPL version 3 or later. See the COPYING file for details.
