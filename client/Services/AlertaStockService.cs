namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Guarda el último conteo conocido de productos con stock bajo, para
/// mostrar una alerta (badge) en el ítem "Stock bajo" del menú lateral sin
/// tener que pedirle a la API ese dato desde el propio NavMenu. Dashboard y
/// StockBajo actualizan este valor cuando cargan sus datos.
/// </summary>
public class AlertaStockService
{
    public int Cantidad { get; private set; }

    public event Action? OnChange;

    public void Actualizar(int cantidad)
    {
        if (Cantidad == cantidad) return;
        Cantidad = cantidad;
        OnChange?.Invoke();
    }
}
