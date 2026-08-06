namespace DesktopManagerStock.Client.Models;

public class Producto
{
    public int Id { get; set; }
    public string Nombre { get; set; } = string.Empty;
    public decimal Precio { get; set; }
    public int Stock { get; set; }
    public int StockMinimo { get; set; } = 5;
    public int StockMaximo { get; set; } = 100;
    public bool Activo { get; set; } = true;
    public string? Categoria { get; set; }
    public string? Sku { get; set; }
    public string? ProveedorNombre { get; set; }
    public string? ProveedorContacto { get; set; }

    /// <summary>Nivel de stock respecto al mínimo/máximo, para pintar el badge en la UI.</summary>
    public string NivelStock =>
        !Activo ? "inactive" :
        Stock <= 0 ? "out" :
        Stock <= StockMinimo ? "low" : "ok";
}

/// <summary>Body para crear un producto (POST /productos).</summary>
public class ProductoCreateRequest
{
    public string Nombre { get; set; } = string.Empty;
    public decimal Precio { get; set; }
    public int Stock { get; set; }
    public int StockMinimo { get; set; } = 5;
    public int StockMaximo { get; set; } = 100;
    public string? Categoria { get; set; }
    public string? Sku { get; set; }
    public string? ProveedorNombre { get; set; }
    public string? ProveedorContacto { get; set; }
}

/// <summary>Body para actualizar un producto (PUT /productos/{id}). Todo opcional.</summary>
public class ProductoUpdateRequest
{
    public string? Nombre { get; set; }
    public decimal? Precio { get; set; }
    public int? StockMinimo { get; set; }
    public int? StockMaximo { get; set; }
    public string? Categoria { get; set; }
    public string? Sku { get; set; }
    public string? ProveedorNombre { get; set; }
    public string? ProveedorContacto { get; set; }
    public bool? Activo { get; set; }
}

/// <summary>Resultado de un ajuste de stock aplicado, para poder "deshacerlo" (ver Productos.razor).</summary>
public record AjusteStockResultado(int ProductoId, int Cantidad, bool EsEntrada);

/// <summary>Resultado de POST /productos/importar-csv.</summary>
public class ImportacionResultado
{
    public int TotalFilas { get; set; }
    public int Creados { get; set; }
    public List<string> ProductosCreados { get; set; } = new();
    public List<ImportacionOmitida> Omitidos { get; set; } = new();
}

public class ImportacionOmitida
{
    public int Fila { get; set; }
    public string Motivo { get; set; } = string.Empty;
}
