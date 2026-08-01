namespace DesktopManagerStock.Client;

public partial class App : Application
{
    public App()
    {
        InitializeComponent();
        // Antes se asignaba acá "MainPage = new AppShell();", pero esa
        // propiedad está obsoleta desde .NET MAUI 9: la ventana raíz ahora
        // se define devolviendo un Window desde CreateWindow (ver abajo).
    }

    protected override Window CreateWindow(IActivationState? activationState)
    {
        var window = new Window(new AppShell())
        {
            Title = "DesktopManagerStock",
            Width = 1200,
            Height = 800,
            MinimumWidth = 900,
            MinimumHeight = 600,
        };

        // Workaround para un bug conocido de WinUI3/Windows App SDK en apps
        // "unpackaged" (WindowsPackageType=None, como esta): al cerrar la
        // ventana, el propio runtime de Windows a veces revienta con
        // "Exception Processing Message 0xc0000005 - Unexpected parameters"
        // durante la limpieza nativa de COM (WebView2 incluido), DESPUÉS de
        // que la app ya terminó de hacer su trabajo. No es un bug de la
        // lógica de la app: es un problema de orden de destrucción del
        // propio WinUI3. Se fuerza el cierre del proceso apenas la ventana
        // empieza a destruirse, antes de que esa limpieza nativa problemática
        // llegue a ejecutarse.
#if WINDOWS
        window.Destroying += (_, _) => Environment.Exit(0);
#endif

        return window;
    }
}
