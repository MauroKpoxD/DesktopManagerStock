namespace DesktopManagerStock.Client.Services;

public enum Seccion { Dashboard, Productos, ProductoDetalle, Movimientos, StockBajo, Reportes, Usuarios, Perfil }

/// <summary>
/// La app no usa el Router de Blazor basado en URLs (@page "/...") porque no
/// hace falta deep-linking ni botón "atrás" en un panel de escritorio como
/// este: alcanza con un estado simple de "qué sección estoy mostrando",
/// controlado desde el menú lateral (ver NavMenu.razor). ProductoDetalle es
/// la única sección que necesita un parámetro (qué producto mostrar), así
/// que se guarda aparte en ProductoIdParametro.
/// </summary>
public class NavigationState
{
    public Seccion SeccionActual { get; private set; } = Seccion.Dashboard;
    public int? ProductoIdParametro { get; private set; }

    public event Action? OnChange;

    public void IrA(Seccion seccion)
    {
        if (SeccionActual == seccion && seccion != Seccion.ProductoDetalle) return;
        SeccionActual = seccion;
        OnChange?.Invoke();
    }

    public void IrAHistorialProducto(int productoId)
    {
        SeccionActual = Seccion.ProductoDetalle;
        ProductoIdParametro = productoId;
        OnChange?.Invoke();
    }
}
