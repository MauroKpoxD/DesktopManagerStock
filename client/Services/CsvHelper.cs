using Microsoft.Maui.Storage;
using Microsoft.Maui.ApplicationModel;
using Microsoft.Maui.ApplicationModel.DataTransfer;

namespace DesktopManagerStock.Client.Services;

/// <summary>
/// Exportar a CSV los datos que el usuario ya tiene cargados/filtrados en
/// pantalla es más simple y rápido que pedirle un reporte PDF/Excel a la API
/// cuando lo único que se necesita son los datos crudos.
/// </summary>
public static class CsvHelper
{
    /// <summary>Escapa un valor para CSV: si tiene coma, comillas o salto de línea, lo entrecomilla.</summary>
    public static string Escapar(object? valor)
    {
        var texto = valor?.ToString() ?? string.Empty;
        if (texto.Contains(',') || texto.Contains('"') || texto.Contains('\n'))
        {
            return "\"" + texto.Replace("\"", "\"\"") + "\"";
        }
        return texto;
    }

    public static async Task GuardarYAbrirAsync(string nombreBase, string contenidoCsv)
    {
        var nombreArchivo = $"{nombreBase}_{DateTime.Now:yyyyMMdd_HHmmss}.csv";
        var ruta = Path.Combine(FileSystem.Current.CacheDirectory, nombreArchivo);
        // BOM UTF-8 al principio para que Excel abra los acentos/ñ bien en Windows.
        await File.WriteAllTextAsync(ruta, "\uFEFF" + contenidoCsv);
        await Launcher.Default.OpenAsync(new OpenFileRequest("Exportación CSV", new ReadOnlyFile(ruta)));
    }
}
