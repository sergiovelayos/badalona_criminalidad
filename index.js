import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Bar } from 'recharts';

const WebAppCriminalidad = () => {
  const [datos, setDatos] = useState([]);
  const [municipioSeleccionado, setMunicipioSeleccionado] = useState('');
  const [tipoDelitoSeleccionado, setTipoDelitoSeleccionado] = useState('');
  const [loading, setLoading] = useState(true);

  // Simulamos la carga de datos (reemplazar con datos reales)
  useEffect(() => {
    // Simular datos basados en el formato especificado
    const datosSimulados = [
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T1',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 2,
        tasa_criminalidad_x1000: 0.009,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.012
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T2',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 1,
        tasa_criminalidad_x1000: 0.005,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.010
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T3',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 3,
        tasa_criminalidad_x1000: 0.014,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.015
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T4',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 0,
        tasa_criminalidad_x1000: 0.000,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.008
      },
      // Más datos simulados para robos
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T1',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '2. Robos con violencia o intimidación',
        valor: 45,
        tasa_criminalidad_x1000: 0.206,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.180
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T2',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '2. Robos con violencia o intimidación',
        valor: 52,
        tasa_criminalidad_x1000: 0.238,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.200
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T3',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '2. Robos con violencia o intimidación',
        valor: 38,
        tasa_criminalidad_x1000: 0.174,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.190
      },
      {
        geo: '08911 Badalona',
        año: 2023,
        trimestre: 'T4',
        municipio: 'Badalona',
        codigo_postal: '08911',
        poblacion: 218886,
        tipo_normalizado: '2. Robos con violencia o intimidación',
        valor: 41,
        tasa_criminalidad_x1000: 0.187,
        codigo_provincia: '08',
        tasa_promedio_provincial: 0.175
      },
      // Datos de otro municipio para comparación
      {
        geo: '28001 Madrid',
        año: 2023,
        trimestre: 'T1',
        municipio: 'Madrid',
        codigo_postal: '28001',
        poblacion: 3280782,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 8,
        tasa_criminalidad_x1000: 0.002,
        codigo_provincia: '28',
        tasa_promedio_provincial: 0.003
      },
      {
        geo: '28001 Madrid',
        año: 2023,
        trimestre: 'T2',
        municipio: 'Madrid',
        codigo_postal: '28001',
        poblacion: 3280782,
        tipo_normalizado: '1. Homicidios dolosos y asesinatos consumados',
        valor: 6,
        tasa_criminalidad_x1000: 0.002,
        codigo_provincia: '28',
        tasa_promedio_provincial: 0.002
      }
    ];
    
    setTimeout(() => {
      setDatos(datosSimulados);
      setLoading(false);
    }, 1000);
  }, []);

  // Obtener listas únicas para los selectores
  const municipiosUnicos = useMemo(() => {
    const municipios = [...new Set(datos.map(d => d.geo))].sort();
    return municipios;
  }, [datos]);

  const tiposDelitoUnicos = useMemo(() => {
    const tipos = [...new Set(datos.map(d => d.tipo_normalizado))].sort();
    return tipos;
  }, [datos]);

  // Filtrar datos según selección
  const datosFiltrados = useMemo(() => {
    if (!municipioSeleccionado || !tipoDelitoSeleccionado) return [];
    
    return datos
      .filter(d => d.geo === municipioSeleccionado && d.tipo_normalizado === tipoDelitoSeleccionado)
      .sort((a, b) => {
        if (a.año !== b.año) return a.año - b.año;
        return a.trimestre.localeCompare(b.trimestre);
      })
      .map(d => ({
        periodo: `${d.año}-${d.trimestre}`,
        municipio_tasa: d.tasa_criminalidad_x1000,
        provincial_tasa: d.tasa_promedio_provincial,
        valor: d.valor,
        año: d.año,
        trimestre: d.trimestre
      }));
  }, [datos, municipioSeleccionado, tipoDelitoSeleccionado]);

  // Componente de tooltip personalizado
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-300 rounded shadow-lg">
          <p className="font-semibold">{`Periodo: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.dataKey === 'municipio_tasa' && `Tasa Municipal: ${entry.value.toFixed(3)} por 1000 hab`}
              {entry.dataKey === 'provincial_tasa' && `Promedio Provincial: ${entry.value.toFixed(3)} por 1000 hab`}
              {entry.dataKey === 'valor' && `Casos: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando datos de criminalidad...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📊 Análisis de Criminalidad por Municipios
          </h1>
          <p className="text-gray-600">
            Visualiza las tasas de criminalidad por cada 1000 habitantes y compara con el promedio provincial
          </p>
        </div>

        {/* Controles */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Selector de Municipio */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Seleccionar Municipio
              </label>
              <select
                value={municipioSeleccionado}
                onChange={(e) => setMunicipioSeleccionado(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">-- Selecciona un municipio --</option>
                {municipiosUnicos.map((municipio) => (
                  <option key={municipio} value={municipio}>
                    {municipio}
                  </option>
                ))}
              </select>
            </div>

            {/* Selector de Tipo de Delito */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Seleccionar Tipo de Delito
              </label>
              <select
                value={tipoDelitoSeleccionado}
                onChange={(e) => setTipoDelitoSeleccionado(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">-- Selecciona un tipo de delito --</option>
                {tiposDelitoUnicos.map((tipo) => (
                  <option key={tipo} value={tipo}>
                    {tipo}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Gráfico */}
        {municipioSeleccionado && tipoDelitoSeleccionado && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {municipioSeleccionado.split(' ').slice(1).join(' ')} - {tipoDelitoSeleccionado}
            </h2>
            
            {datosFiltrados.length > 0 ? (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={datosFiltrados}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="periodo" 
                      stroke="#6b7280"
                      fontSize={12}
                    />
                    <YAxis 
                      yAxisId="tasa"
                      orientation="left"
                      stroke="#2563eb"
                      fontSize={12}
                      label={{ value: 'Tasa por 1000 hab', angle: -90, position: 'insideLeft' }}
                    />
                    <YAxis 
                      yAxisId="casos"
                      orientation="right"
                      stroke="#dc2626"
                      fontSize={12}
                      label={{ value: 'Número de casos', angle: 90, position: 'insideRight' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    
                    {/* Barras para los valores */}
                    <Bar 
                      yAxisId="casos"
                      dataKey="valor" 
                      fill="#dc2626" 
                      fillOpacity={0.6}
                      name="Casos"
                    />
                    
                    {/* Línea principal del municipio */}
                    <Line
                      yAxisId="tasa"
                      type="monotone"
                      dataKey="municipio_tasa"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                      name="Tasa Municipal"
                    />
                    
                    {/* Línea de promedio provincial (con puntos) */}
                    <Line
                      yAxisId="tasa"
                      type="monotone"
                      dataKey="provincial_tasa"
                      stroke="#059669"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={{ fill: '#059669', strokeWidth: 2, r: 3 }}
                      name="Promedio Provincial"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">No hay datos disponibles para la selección actual</p>
              </div>
            )}
          </div>
        )}

        {/* Mensaje cuando no hay selección */}
        {(!municipioSeleccionado || !tipoDelitoSeleccionado) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-blue-800 font-medium">
              👆 Selecciona un municipio y un tipo de delito para ver el análisis
            </p>
          </div>
        )}

        {/* Información adicional */}
        <div className="mt-8 bg-gray-100 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-2">ℹ️ Información sobre el gráfico:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li><span className="text-blue-600">●</span> <strong>Línea azul sólida:</strong> Tasa de criminalidad del municipio seleccionado</li>
            <li><span className="text-green-600">●</span> <strong>Línea verde punteada:</strong> Promedio provincial (2 primeros dígitos del código postal)</li>
            <li><span className="text-red-600">■</span> <strong>Barras rojas:</strong> Número absoluto de casos registrados</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default WebAppCriminalidad;