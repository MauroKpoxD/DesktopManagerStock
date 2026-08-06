using Microsoft.Maui.Storage;

namespace DesktopManagerStock.Client.Services;

public enum FormatoReporte { Pdf, Excel }

public class ReporteService
{
    private readonly HttpClient _http;

    public ReporteService(IHttpClientFactory factory)
    {
        _http = factory.CreateClient("ApiConAuth");
    }

    public Task<string> DescargarReporteProductosAsync(FormatoReporte formato) =>
        DescargarYGuardarAsync($"reportes/productos?formato={Formato(formato)}", "productos", formato);

    public Task<string> DescargarReporteStockBajoAsync(FormatoReporte formato, int? umbral = null)
    {
        var url = $"reportes/stock-bajo?formato={Formato(formato)}";
        if (umbral.HasValue) url += $"&umbral={umbral.Value}";
        return DescargarYGuardarAsync(url, "stock-bajo", formato);
    }

    public Task<string> DescargarReporteMovimientosAsync(
        FormatoReporte formato, DateOnly? desde = null, DateOnly? hasta = null, int? productoId = null)
    {
        var query = new List<string> { $"formato={Formato(formato)}" };
        if (desde.HasValue) query.Add($"fecha_desde={desde.Value:yyyy-MM-dd}");
        if (hasta.HasValue) query.Add($"fecha_hasta={hasta.Value:yyyy-MM-dd}");
        if (productoId.HasValue) query.Add($"producto_id={productoId.Value}");
        return DescargarYGuardarAsync($"reportes/movimientos?{string.Join("&", query)}", "movimientos", formato);
    }

    private static string Formato(FormatoReporte formato) => formato == FormatoReporte.Pdf ? "pdf" : "excel";

    /// <summary>
    /// Descarga el archivo binario del reporte, lo guarda en el directorio de
    /// caché de la app y devuelve la ruta local. Desde la UI se abre con
    /// Launcher.OpenAsync (visor de PDF / Excel del sistema operativo), en
    /// vez de intentar mostrarlo dentro de la propia app.
    /// </summary>
    private async Task<string> DescargarYGuardarAsync(string url, string nombreBase, FormatoReporte formato)
    {
        var response = await _http.GetAsync(url);
        await response.EnsureSuccessOrThrowAsync();

        var extension = formato == FormatoReporte.Pdf ? "pdf" : "xlsx";
        var nombreArchivo = $"{nombreBase}_{DateTime.Now:yyyyMMdd_HHmmss}.{extension}";
        var rutaCompleta = Path.Combine(FileSystem.Current.CacheDirectory, nombreArchivo);

        var bytes = await response.Content.ReadAsByteArrayAsync();
        await File.WriteAllBytesAsync(rutaCompleta, bytes);

        return rutaCompleta;
    }
}
