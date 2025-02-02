from fpdf import FPDF

def generar_pdf(cliente, costos, imagen, output_path, coste_total_siniestro):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.cell(200, 10, txt="Informe de daños y costos", ln=True, align='C')

    # Información del cliente
    pdf.cell(0, 10, f"Nombre: {cliente['nombre']} {cliente['apellido']}", ln=True)
    pdf.cell(0, 10, f"DNI: {cliente['dni']}", ln=True)
    pdf.cell(0, 10, f"Número de póliza: {cliente['numero_poliza']}", ln=True)
    pdf.cell(0, 10, f"Prima: {cliente['prima']}", ln=True)
    pdf.cell(0, 10, f"Marca: {cliente['marca_vehiculo']}", ln=True)
    pdf.cell(0, 10, f"Modelo: {cliente['modelo_vehiculo']}", ln=True)
    pdf.cell(0, 10, f"Provincia: {cliente['provincia']}", ln=True)
    pdf.cell(0, 10, f"Ciudad: {cliente['ciudad']}", ln=True)

    # Imagen de daños
    pdf.cell(0, 10, "Imagen de daños:", ln=True)
    pdf.image(imagen, x=10, y=None, w=100)

    # Costos
    pdf.cell(0, 10, "Desglose de costos:", ln=True)
    for componente in costos:
        costo_total = round(componente['coste_material'] + componente['coste_mano_obra'], 2)
        pdf.cell(0, 10, f"Componente: {componente['componente']}", ln=True)
        pdf.cell(0, 10, f"  - Coste del material: {componente['coste_material']} Eur", ln=True)
        pdf.cell(0, 10, f"  - Coste de la mano de obra: {componente['coste_mano_obra']} Eur", ln=True)
        pdf.cell(0, 10, f"  - Coste total: {costo_total} Eur", ln=True)

    # Coste total del siniestro
    pdf.cell(0, 10, "", ln=True)  # Línea vacía para separación
    pdf.cell(0, 10, f"Coste Total Siniestro: {coste_total_siniestro:.2f} Eur", ln=True)

    # Guardar el PDF
    pdf.output(output_path)