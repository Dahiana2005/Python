import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from io import BytesIO
import os

# Cargar datos financieros
archivo_cuentas = pd.read_csv('datos_validaciones.csv',delimiter=';')
print(archivo_cuentas)

#Funciones y validaciones

#Sumar las columnas que contienen valores
archivo_cuentas['valor_total'] = archivo_cuentas['IMPORTE'] + archivo_cuentas['VALOR_IVA_']

# Convertir fechas a formato datetime
archivo_cuentas['FECHA_DE_DOCUMENTO'] = pd.to_datetime(archivo_cuentas['FECHA_DE_DOCUMENTO'], dayfirst=True)
archivo_cuentas['FECHA_CORTE'] = pd.to_datetime(archivo_cuentas['FECHA_CORTE'], dayfirst=True)

# Comparar fechas
archivo_cuentas['operacion_en_rango'] = archivo_cuentas['FECHA_DE_DOCUMENTO'] <= archivo_cuentas['FECHA_CORTE']

#Sacar o filtar las columnas exclusivas con una unica entidad 
Filtro_entidad = [archivo_cuentas['ENTIDAD'] == 'Promotora Chilena S.A.']

# Expresiones regulares
archivo_cuentas['fecha_extraida'] = archivo_cuentas['FECHA_DE_DOCUMENTO'].dt.strftime(r'(\d{2}/\d{2}/\d{4})')

# Montos
filtro = archivo_cuentas['DETALLE_DE_LA_OPERACION_'].str.contains("Compras de servicios", na=False)
archivo_cuentas.loc[filtro, 'monto_extraido'] = archivo_cuentas.loc[filtro, 'IMPORTE']
       
# Palabras clave
archivo_cuentas['categoria_palabra'] = archivo_cuentas['DETALLE_DE_LA_OPERACION_'].str.extract(r'\b(Arrendamientos|Intereses|Venta de producto|Servicios)\b')  

#Se hace el filtro por las dos iniciales de la factura especifica
filtro_factura = archivo_cuentas['NO_FACTURA_'].str.startswith('HS')
filtro_factura = filtro_factura.fillna(False) 

# Se utiliza la funcion de filtro_factura para sumar las columnas de importe y el valor iva
suma_individual = archivo_cuentas.loc[filtro_factura, ['IMPORTE', 'VALOR_IVA_']].sum()

# Calcular el total sumando las dos columnas cuando la factura inicia por FN
suma_total = suma_individual['IMPORTE'] + suma_individual['VALOR_IVA_']

# Eliminacion de caracteres especiales del numero de factura
archivo_cuentas['NO_FACTURA_'] = archivo_cuentas['NO_FACTURA_'].str.replace(r'[^\w\d]', '', regex=True)

#Verificacion que la columna de DOC_CONTABLE contenga n cantidad de digitos
archivo_cuentas['DOC_CONTABLE_'] = archivo_cuentas['DOC_CONTABLE_'].fillna('').astype(str)
archivo_cuentas['cuenta_valida'] = archivo_cuentas['DOC_CONTABLE_'].str.match(r'^\d{6,10}$')

# Comparacion de las cuentas dos archivos
maestro_cuentas = pd.read_csv('balance_prueba.csv', delimiter=';')
archivo_cuentas['DOC_CONTABLE_'] = archivo_cuentas['DOC_CONTABLE_'].astype(str)
maestro_cuentas['DOC_CONTABLE_'] = maestro_cuentas['DOC_CONTABLE_'].astype(str)

comparacion = archivo_cuentas.merge(maestro_cuentas, on='DOC_CONTABLE_', how='left')

# Indicadores clave
indicadores = archivo_cuentas.groupby('TIPO')['valor_total'].sum().reset_index()
operaciones_en_rango = archivo_cuentas[archivo_cuentas['operacion_en_rango']].shape[0]

# Resultados
print(indicadores)
print(f'Operaciones dentro del rango: {operaciones_en_rango}')

def generar_grafico_indicadores(indicadores):
    fig, ax = plt.subplots()
    ax.bar(indicadores['TIPO'], indicadores['valor_total'], color='skyblue')
    ax.set_xlabel('Tipo de Operación')
    ax.set_ylabel('Valor Total')
    ax.set_title('Indicadores por Tipo de Operación')
    archivo_imagen = "grafico_indicadores.png"
    plt.savefig(archivo_imagen)
    plt.close()
    return archivo_imagen

def generar_informe_pdf(archivo_cuentas, indicadores, operaciones_en_rango, comparacion):
    pdf_file = canvas.Canvas("informe_financiero.pdf", pagesize=letter)
    pdf_file.setFont("Helvetica", 12)

    pdf_file.drawString(200, 750, "Informe de Validaciones Financieras")
    y_position = 730
    pdf_file.drawString(50, y_position, "1. Validación de Fechas: ")
    y_position -= 20
    pdf_file.drawString(50, y_position, f"- Operaciones en rango: {operaciones_en_rango}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "2. Sumar columnas IMPORTE y VALOR_IVA: ")
    y_position -= 20
    pdf_file.drawString(50, y_position, f"- Total suma: {archivo_cuentas['valor_total'].sum()}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "3. Filtrar operaciones de entidad 'Promotora Chilena S.A.':")
    y_position -= 20
    entidad_filtrada = archivo_cuentas[archivo_cuentas['ENTIDAD'] == 'Promotora Chilena S.A.']
    pdf_file.drawString(50, y_position, f"- Total de operaciones: {entidad_filtrada.shape[0]}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "4. Operaciones con fecha extraída:")
    y_position -= 20
    pdf_file.drawString(50, y_position, f"- Total de operaciones con fecha extraída: {archivo_cuentas['fecha_extraida'].dropna().shape[0]}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "5. Montos extraídos de compras de servicios:")
    y_position -= 20
    pdf_file.drawString(50, y_position, f"- Total de montos extraídos: {archivo_cuentas['monto_extraido'].dropna().shape[0]}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "6. Palabras clave:")
    y_position -= 20
    for keyword in ['Arrendamientos', 'Intereses', 'Venta de producto', 'Servicios']:
        count = archivo_cuentas[archivo_cuentas['categoria_palabra'] == keyword].shape[0]
        pdf_file.drawString(50, y_position, f"- {keyword}: {count} operaciones")
        y_position -= 20

    y_position -= 40
    pdf_file.drawString(50, y_position, f"7. Total facturas que inician con HS (IMPORTE + IVA): {suma_total}")

    y_position -= 40
    pdf_file.drawString(50, y_position, "8. Comparación de cuentas (DOC_CONTABLE):")
    y_position -= 20
    pdf_file.drawString(50, y_position, f"- Total de coincidencias: {comparacion.shape[0]}")

    # Sección de gráficos
    pdf_file.showPage()

    # Segunda página con el gráfico
    pdf_file.drawString(50, 750, "Gráfico de Indicadores Clave")

    archivo_imagen = generar_grafico_indicadores(indicadores)
    pdf_file.drawImage(archivo_imagen, 50, 500, width=500, height=200)
    os.remove(archivo_imagen)

    pdf_file.save()

generar_informe_pdf(archivo_cuentas, indicadores, operaciones_en_rango, comparacion)

print("Informe PDF generado exitosamente.")